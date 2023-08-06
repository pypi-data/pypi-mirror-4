#
# archiver.py
#

import os, sys, socket, re, time, smtplib, calendar, StringIO, logging, logging.handlers, locale, gzip, posixpath
import urllib, urllib2, urlparse, ftplib
from datetime import datetime, timedelta
import email
from email.Utils import parseaddr, formataddr, formatdate
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase

import cron

atom=r"[a-zA-Z0-9_#\$&'*+/=?\^`{}~|\-]+"
dot_atom=atom  +  r"(?:\."  +  atom  +  ")*"
quoted=r'"(?:\\[^\r\n]|[^\\"])*"'
local="(?:"  +  dot_atom  +  "|"  +  quoted  +  ")"
domain_lit=r"\[(?:\\\S|[\x21-\x5a\x5e-\x7e])*\]"
domain="(?:"  +  dot_atom  +  "|"  +  domain_lit  +  ")"
addr_spec=local  +  "\@"  +  domain
postfix_restricted_rfc2822_address_name=local
postfix_restricted_rfc2822_email_address=addr_spec
cyrus_mailbox_name=r"[a-zA-Z0-9_#$'=`{}~|-]+(?:\.[a-zA-Z0-9_#$'=`{}~|-]+)*"

domain_nameRE=re.compile('^'+dot_atom+'$')
email_addressRE=re.compile('^'+postfix_restricted_rfc2822_email_address+'$')
valid_ipRE=re.compile('^([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
valid_hostnameRE=re.compile('^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\\-]*[a-zA-Z0-9])\\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\\-]*[A-Za-z0-9])$')
ftp_url_re=re.compile(r'ftp://(?:(?P<username>[\w\.\-\+%!$&\'\(\)*,;=#]+)(?::(?P<password>[\w\.\-\+%!$&\'\(\)*,;=#]+))?@)?(?P<host>[a-zA-Z0-9\.\-]+)(?::(?P<port>\d+))?(?:(?P<directory>/.*))?')

# from FormEncode
url_re = re.compile(r'''
    ^(http|https)://
    (?:[%:\w]*@)?                           # authenticator
    (?P<domain>([a-z0-9][a-z0-9\-]{1,62}\.)*) # (sub)domain - alpha followed by 62max chars (63 total)
    (?P<tld>[a-z]{2,})                      # TLD
    (?::[0-9]+)?                            # port
    # files/delims/etc
    (?P<path>/[a-z0-9\-\._~:/\?#\[\]@!%\$&\'\(\)\*\+,;=]*)?
    $
''', re.I | re.VERBOSE)

boolean={ 'on':True, 'yes':True, 'true':True, '1':True, 1:True, 'off':False, 'no':False, 'false':False, '0':False, 0:False}

# ---------------------------------------------------------------------
def check_boolean(job, errors, options):
    for option, default in options:
        value=boolean.get(job.get(option, default).lower(), None)
        if value==None:
            errors[option]='boolean must have value in (on, yes, true, 1, off, no, false and 0)'
            value=default
        job[option]=value


# ---------------------------------------------------------------------------
def check_mail_config(job):
    
    errors={}

    defaul_port=dict(normal=25, ssl=465, tls=587)
    
    mail=job.get('mail', 'yes')
    if mail!='fail':
        mail=boolean.get(mail, None)
    
    if mail==None:
        errors['mail']='mail must have a value in (yes, no, fail)'
    else:
        job['mail']=mail

    magikmon=job.get('magikmon', '')
    if magikmon:
        if not url_re.match(magikmon):
            errors['magikmon']='not a valid URL'
        else:
            if job['program']=='esxmon':
                up=urlparse.urlparse(magikmon)
                if up[1].lower().startswith('monitoring.magikmon.com') and up[2].lower().startswith('/sendbackup'):
                    magikmon=''
                    # don't send esxmon status to MagiKmon backup service 
                    # errors['magikmon']='Cannot report status to MagikMon backup service'
                    
    job['magikmon']=magikmon
    
    if mail:
        try:
            job['smtp_host']=smtp_host=job['smtp_host'].encode('ascii')
        except UnicodeEncodeError:
            errors['smtp_host']='invalid hostname or ip address'
        else:
            if not valid_ipRE.match(smtp_host):
                if not valid_hostnameRE.match(smtp_host):
                    errors['smtp_host']='invalid hostname or ip address'
                else:
                    try:
                        ip=socket.gethostbyname(smtp_host)
                    except socket.gaierror:
                        errors['smtp_host']='cannot resolve address'
    
        smtp_mode=job['smtp_mode'].lower()
        if not smtp_mode in ('normal', 'ssl', 'tls'):
            errors['smtp_mode']='mode must be in "normal", "ssl", or "tls"'
        else:
            job['smtp_mode']=smtp_mode
            if smtp_mode in ('ssl', 'tls') and not hasattr(socket, 'ssl'):
                errors['smtp_mode']='this version of python has not support for SSL'
            if smtp_mode=='ssl' and not hasattr(smtplib, 'SMTP_SSL'):
                errors['smtp_mode']='this version of python has not SSL support for SMTP'
                
        job['smtp_login']=job.get('smtp_login')
        job['smtp_password']=job.get('smtp_password')

        smtp_port=job.get('smtp_port', defaul_port.get(smtp_mode, 25))
        try:
            port=int(smtp_port)
        except Exception:
            errors['smtp_port']='must be an integer'
        else:
            if not (0<port and port<65535):
                errors['smtp_port']='must be an integer between 1 and 65535'
            else:
                job['smtp_port']=port
            
    if mail or magikmon:

        sender=job.get('sender', None)
        if not sender:
            errors['sender']='option mandatory'
        elif not email_addressRE.match(sender):
            errors['sender']='invalid email address'
    
        recipients=job.get('recipients')
        if not recipients:
            errors['recipients']='option mandatory'
        else:
            recipients=recipients.split()
            bad=[]
            for recipient in recipients[:]:
                if not email_addressRE.match(recipient):
                    bad.append(recipient)
                domain=recipient.split('@')[-1].lower()
                if job['program']=='esxmon' and  domain=='monitoring.magikmon.com':
                    # don't send esxmon status to MagiKmon backup service 
                    # errors['recipients']='Cannot report status to MagikMon backup service'
                    recipients.remove(recipient)
                    
            if bad:
                errors['recipients']='invalid email addresses: %s' % ' '.join(bad)
            else:
                job['recipients']=recipients

        attachment_gzip=job['attachment_gzip']
        try:
            size=int(attachment_gzip)
        except Exception:
            errors['attachment_gzip']='must be an integer'
        else:
            if not (0<size and size<=10240):
                errors['attachment_gzip']='must be an integer between 1 and 10240'
            else:
                job['attachment_gzip']=size*1024 # in K

        attachment_size=job['attachment_size']
        try:
            size=int(attachment_size)
        except Exception:
            errors['attachment_size']='must be an integer'
        else:
            if not (0<size and size<=10240):
                errors['attachment_size']='must be an integer between 1 and 10240'
            else:
                job['attachment_size']=size*1024 # in K


    return errors

# ---------------------------------------------------------------------------
def socket_readlines(chan):
    """iterator reading lines from a socket"""
    line_buf=''
    while True:
        x=chan.recv(1024)
        if len(x)==0:
            break
        line_buf=line_buf+x
        lines=line_buf.split('\n')
        line_buf=lines[-1]
        for line in lines[:-1]:
            yield line

    if line_buf:
        yield line_buf

# ---------------------------------------------------------------------------
def ftp_pre_create_dir(host, port, username, password, directory):
    ftpcli=ftplib.FTP()
    try:
        ftpcli.connect(host, port, timeout=10)
    except TypeError:
        # python 2.5 and below have no timeout
        ftpcli=ftplib.FTP()
        ftpcli.connect(host, port)
           
    ftpcli.login(username, password)
    dir=directory
    dirs=[]
    while dir and dir!='/':
        dirs.insert(0, dir)
        dir=posixpath.dirname(dir)

    for dir in dirs:
        try:
            ftpcli.mkd(dir)
        except:
            pass
    try:
        ftpcli.quit()
    except:
        pass
    ftpcli.close()

# ---------------------------------------------------------------------------
def _list_dir(target_dir, log):
    total_size=0
    dir_out=u'== directory %s\r\n  epoch   |          time          |      size     |    filename\r\n' % target_dir
    for filename in os.listdir(target_dir): # if target_dir is unicode, return os.listdir return unicode
        full_filename=os.path.join(target_dir, filename)
        stat=os.stat(full_filename)
        if os.path.isdir(full_filename):
            size='<DIR>'
        else:
            size='%15d' % stat.st_size
            total_size+=stat.st_size
        dir_out+='%d %s %15s %s\r\n' % (stat.st_mtime, time.ctime(stat.st_mtime), size, filename)
        
    return dir_out, total_size

# ---------------------------------------------------------------------------
def list_dir(target_dir, log):
    try:
        dir_out, total_size=_list_dir(target_dir, log) 
    except Exception, e:
        log.error('listing target directory: %s', e)
        dir_out='error listing directory "%s": %s\r\n' % (target_dir, e)
        total_size=0
        
    return dir_out, total_size

# ---------------------------------------------------------------------------
def free_space(target_dir, log):
    
    try:
        if sys.platform=='win32':
            import win32file
            free_bytes, total_bytes, total_free_bytes=win32file.GetDiskFreeSpaceEx(target_dir)
        else:
            import os, statvfs
            s=os.statvfs(target_dir)
            total_free_bytes=s[statvfs.F_BSIZE]*s[statvfs.F_BAVAIL] 

    except Exception, e:
        if log:
            log.error('checking directory "%s": %s', target_dir, e)
        raise e

    return total_free_bytes

# ---------------------------------------------------------------------------
def quoted_string_list(st):
    """
    st  is a list of string separated by spaces like in shell script
    String containing space can be quoted
    Quote can be escaped with \
    r'1 two "t h r e e" "with a \" inside"' -->
                        ['1', 'two', 't h r e e', 'with a \\" inside']
    '" dont remove this line my editor string highlighting need it
    """                        
    lst=[]
    s=st.strip()
    while s:
        match=re.match(r'("(?:\\"|[^"])*"|[^ "]*)(.*)',  s)
        if match:
            item=match.groups()[0]
            if not item:
                raise ValueError, ("not a quoted string list '%s'" % (st,))
            elif item[0]=='"':
                lst.append(item[1:-1])
            else:
                lst.append(item)
            s=match.groups()[1].lstrip()
        else:
            raise ValueError, ("not a quoted string list '%s'" % (st,))
    return lst

# ---------------------------------------------------------------------------
def sendmail(job, subject, text, attachments, log, status):

    errmsg=''     
    if (job['mail']==False or (job['mail']=='fail' and status=='OK')) and not job['magikmon']:
        return None

    sender=job['sender']
    recipients=job['recipients']
    attachment_size=job['attachment_size']
    attachment_gzip=job['attachment_gzip']

    msg=MIMEMultipart()
    msg.preamble='' # This line is not visible on mime enable MUA
    msg.epilogue=''
    
    msg['From'] = formataddr((sender, sender)) # Display name, email address
    msg['To'] =  ', '.join([ formataddr((recipient, recipient)) for recipient in recipients ])
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg['Messsage-Id']=email.Utils.make_msgid('mksbackup')

    core=MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
    msg.attach(core)
    
    for filename, target, data, maintype, subtype, charset in attachments:
        
        if not data and target and os.path.exists(target):
            data=open(target, 'rb').read(attachment_size)

        if data==None:
            data=''

        if len(data)>attachment_gzip:
            log.info('gzip attachment %s', filename)
            file_out=StringIO.StringIO()
            zfile=gzip.GzipFile(filename, 'wb', 9, file_out)
            if maintype=='text':
                # all txt gzip file are encode in UTF8 to avoid the loose of the charset 
                data=data.decode(charset).encode('utf-8')
            zfile.write(data)
            zfile.close()
            data=file_out.getvalue()
            file_out.close()
            filename+='.gz'
            maintype, subtype='application', 'x-gzip'

        if len(data)>attachment_size:
            log.warning('attachment is too big, skipped: %s', filename)
            # replace attachment by an "error"
            data='attachment is too big: %s\n' % (filename, )
            filename=os.path.splitext(filename)[0]+'-error.txt'
            maintype, subtype, charset='text', 'plain', 'ascii'
            
        #maintype, subtype = 'application', 'octet-stream'
        if maintype=='text':
            attachment=MIMEText(data, subtype, charset)
        else:
            attachment=MIMEBase(maintype, subtype)
            attachment.set_payload(data) #, charset) #dont use the charset, here !
            email.Encoders.encode_base64(attachment)

        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(attachment)
    
    body=msg.as_string()

    # first try send by http             
    if job['magikmon'] and job['program']!='esxmon':
        try:
            data=urllib.urlencode(dict(body=body))
            try:
                urllib2.urlopen(job['magikmon'], data, timeout=30)
            except TypeError:
                # python 2.4
                urllib2.urlopen(job['magikmon'], data)
        except Exception, e:
            log.exception('error sending mail to MagiKmon url: %s (%s)', job['magikmon'], e)
            if not errmsg:
                errmsg='error sending mail to MagiKmon url'
        else:
            log.debug('mail sent to MagiKmon url: %s', job['magikmon'])
            # Don't send the mail twice via HTTP and SMTP to the same MagiKmon monitoring service
            # remove the redundant recipient if any
            # http://monitoring.magikmon.com/sendbackup/XX/secret
            # b.XX@monitoring.magikmon.com
            #    
            domain, tld, path=url_re.match(job['magikmon']).group('domain', 'tld', 'path')
            match=re.match('/sendbackup/(?P<service_id>[0-9]+)(/.*)?', path)
            if match:
                service_id=int(match.group('service_id'))
                mkm_address='b.%d@%s%s' % (service_id, domain, tld)
                for recipient in recipients[:]:
                    if recipient.lower()==mkm_address.lower():
                        log.info('"%s" removed from the list of recipients', recipient)
                        recipients.remove(recipient)
                
    if (job['mail']==True or (job['mail']=='fail' and status!='OK')) and recipients:
        smtp_host=job['smtp_host']
        smtp_port=job['smtp_port']
        smtp_mode=job['smtp_mode']
        smtp_login=job['smtp_login']
        smtp_password=job['smtp_password']
    
        rcpt=[]
        try:
            if smtp_mode=='ssl':
                smtp=smtplib.SMTP_SSL(smtp_host, smtp_port)
            else:
                smtp=smtplib.SMTP(smtp_host, smtp_port)
                if smtp_mode=='tls':
                    smtp.starttls()
                    
            if smtp_login and smtp_password:
                # login and password must be encoded because HMAC used in CRAM_MD5 require non unicode string
                smtp.login(smtp_login.encode('utf-8'), smtp_password.encode('utf-8'))
    
            ret=smtp.sendmail(sender, recipients, body)
            smtp.quit()
        except (socket.error, ), e:
            errmsg='server %s:%s not responding: %s' % (smtp_host, smtp_port, e)
        except smtplib.SMTPAuthenticationError, e:
            errmsg='authentication error: %s' % (e, )
        except smtplib.SMTPRecipientsRefused, e:
            # code, errmsg=e.recipients[recipient_addr]
            errmsg='recipients refused: '+', '.join(e.recipients.keys())
        except smtplib.SMTPSenderRefused, e:
            # e.sender, e.smtp_code, e.smtp_error
            errmsg='sender refused: %s' % (e.sender, )
        except smtplib.SMTPDataError, e:
            errmsg='SMTP protocol mismatch: %s' % (e, )
        except smtplib.SMTPHeloError, e:
            errmsg="server didn't reply properly to the HELO greeting: %s" % (e, )
        except smtplib.SMTPException, e:
            errmsg='SMTP error: %s' % (e, )
        except Exception, e:
            errmsg=str(e)
            log.exception('unexpected error sending mail: %s', e)
        else:
            rcpt=recipients[:]
            if ret:
                errmsg='recipients refused: '+', '.join(ret.keys())        
                for r in ret.keys():
                    rcpt.remove(r)
    
            if log:
                log.info('mail sent to: %s', ', '.join(rcpt))
    
        if log:
            if errmsg:
                log.error('sending mail: %s', errmsg)

    return errmsg

# ---------------------------------------------------------------------------
def write_status(status, directory, job_name, log=None):
    
    filename=os.path.join(directory, job_name+'.txt')
    try:
        f=open(filename, 'w')
        f.write(status.encode('utf-8'))
        f.close()
    except Exception, e:
        if log:
            log.warning('cannot write status into file: "%s"', filename)
    else:
        if log:
            log.info('status written into file: "%s"', filename)

# ---------------------------------------------------------------------------
def send_mail_report(job, result, manager):
    if (job['mail']==False or (job['mail']=='fail' and status=='OK')) and not job['magikmon']:
        return None
    
    backup_status, status, attachments=result

    msg_body=job['msg_header']+'\n'+status
    subject='MKSBACKUP BACKUP %s %s' % (backup_status, job['name'])
    
    attachments.extend(manager.attachments)
    attachments.append(('status.txt', None, status.encode('utf-8'), 'text', 'plain', 'utf-8'))
    log_output=manager.stop_logging()
    attachments.append(('logging.txt', None, log_output.encode('utf-8'), 'text', 'plain', 'utf-8'))                       
    
    for line in status.split('\r\n'):
        if line:
           manager.log.info('    %s', line)
    
    return sendmail(job, subject, msg_body, attachments, manager.log, backup_status)


# ---------------------------------------------------------------------------
def param_encode(lst, encoding, errors='strict'):
    """return a new encoded list of string"""
    if isinstance(lst, list):
        newlst=lst[:]
        for i, v in enumerate(lst):
            newlst[i]=v.encode(encoding, errors)
        return newlst
    elif isinstance(lst, unicode):
        return lst.encode(encoding, errors)
    else:
        return lst

#======================================================================
#
# Destinations
#
#======================================================================
class DestinationSyntaxError(Exception):
    pass

class Destinations:
    
    variables={} # default value for extra variable in Destination 
    types={}    # allowed types in Destination

    def __init__(self, raw, archiver):
        
        self.destinations=[]
        st=raw
        self.full_cycle=7
        self.archiver=archiver
        self.used_types=set()
        
        while st:
            if st[0]!='<':
                raise DestinationSyntaxError, 'starting "<" missing'
            
            try:
                pos=st.index('>')
            except ValueError:
                raise DestinationSyntaxError, 'a ">" is missing'
            
            selector=st[1:pos]
            st=st[pos+1:]
        
            pos=st.find('<')
            if pos>=0:
                target=st[:pos]
                st=st[pos:]
            else:
                target=st
                st=''
            
            typ, period=selector.split('=', 1)

            try:
                if typ.lower()=='none':
                    typ='none'
                else:
                    typ=self.archiver.types[typ.lower()]
            except KeyError:
                raise DestinationSyntaxError, 'type "%s" unknown' % (typ, )

            self.used_types.add(typ.lower())

            #print "SELECTOR<%s=%s>%s" % (typ,period,target )
            #print "CARRY=%s" % st
            period=cron.Cron(period)
            if period.weekdivisor!=None:
                self.full_cycle=max(self.full_cycle, period.weekdivisor*7)
            if period.months:
                self.full_cycle=max(self.full_cycle, 63)
                
            self.destinations.append((typ, period, target))


    def match(self, day, night_shift, variables={}):
        #print '---------------------------------', variables
        night_day=day
        if day.hour<12:
            night_day=night_day-timedelta(days=1)
        if night_shift:
            backup_day=night_day
        else:
            backup_day=day
            
        globals=dict(os.environ)
        globals.update(dict(nday='%02d'%(night_day.day,), nmonth='%02d'%(night_day.month,), nyear=str(night_day.year,), nweekday=night_day.weekday(), nyearday='%03d'%(night_day.timetuple().tm_yday,),))
        globals['nweekdayname']=night_day.strftime('%a')
        globals['nmonthname']=night_day.strftime('%b')
        
        epoch=calendar.timegm(backup_day.timetuple())
        globals['epoch']=int(epoch)
        globals['week']='0'
        globals['nweek']='0'
        globals['nmonthweek']=night_day.day/7
        
        globals.update(self.archiver.variables)
        globals.update(variables)

        for typ, period, target in self.destinations:
            #print 'ASX typ, per, tgt', typ, period, target
            if period:
                #print 'Month', backup_day.month-1, period.months
                if period.months and not backup_day.month-1 in period.months:
                    continue
                #print 'Day of week', backup_day.isoweekday()-1, period.daysofweek
                if period.daysofweek and not backup_day.isoweekday()-1 in period.daysofweek:
                    continue
                #print 'Day of month', backup_day.day-1, period.daysofmonth
                if period.daysofmonth and not backup_day.day-1 in period.daysofmonth:
                    continue
                if period.firstdayofweek!=None:
                    nday=int(epoch/86400)-period.firstdayofweek+3
                    week=int(nday/7)%period.weekdivisor
                    if period.weekselector!=None and week!=period.weekselector:
                        continue
                    globals['week']=week
                    # The night day
                    nday=int(calendar.timegm(night_day.timetuple())/86400)-period.firstdayofweek+3
                    week=int(nday/7)%period.weekdivisor
                    if period.weekselector!=None and week!=period.weekselector:
                        continue
                    globals['nweek']=week

            #print 'MATCH', typ, target
            rawtarget=target
            for exp in re.findall('\$\{([^}]*)\}', target):
                # print 'exp=', exp
                try:
                    target=target.replace('${%s}' % (exp,), str(eval(exp, globals, {})))
                except Exception, e:
                    raise DestinationSyntaxError, 'Invalid expression: "%s" (%s)' % (exp, e)
            target=target.encode('utf-8')
            try:
                target=backup_day.strftime(target)
            except:
                raise DestinationSyntaxError, 'Invalid expression: "%s"' % (target, )
            target=target.decode('utf-8')

            return typ, target
            
        return None, None


# ---------------------------------------------------------------------------

class MyMemoryHandler(logging.handlers.MemoryHandler):

     def shouldFlush(self, record):
        """
        Check for buffer full and drop oldest records.
        """
        if len(self.buffer) >= self.capacity:
            self.buffer=self.buffer[-self.capacity:]
            
        return False

# -------------------------------------------------------------------------
def ErrorDecode(exception, encoding='utf-8'):
    """This is the equivalent of my windows.WindowsErrorDecode but for 
    non windows OS"""
    st=str(exception)
    try:
        return st.decode(encoding)
    except UnicodeDecodeError:
        return st.decode('ascii', 'replace')

# ---------------------------------------------------------------------------
class Manager:
    
    def __init__(self, hostname, log):
        self.hostname=hostname
        self.log=log
        self.default_encoding=locale.getdefaultlocale()[1]
        self.console_encoding=sys.stdout.encoding
        self.formater=logging.Formatter('%(asctime)s %(levelname)-3.3s %(message)s', '%Y-%m-%d %H:%M:%S')
        
    def start_logging(self):
        self.string_log=StringIO.StringIO()
        self.stream_log=logging.StreamHandler(self.string_log)
        self.stream_log.setFormatter(self.formater)
        self.log.addHandler(self.stream_log)

    def stop_logging(self):
        self.stream_log.flush()
        self.log.removeHandler(self.stream_log)
        self.stream_log.close()
        log_output=self.string_log.getvalue()
        # self.string_log.close() don't close it !
        return log_output

# ---------------------------------------------------------------------------
class Archiver:
    
    name=None
    exe=None

    types=dict()
    variables=dict()
 
    def __init__(self):
        self.night_shift=True
        self._hidden_password=[]
        
    def hide_password(self, st):
        """replace password by fake text""" 
        for password in self._hidden_password:
            st=st.replace(password, '********')
        return st
            
    def register_password(self, password):
        """register a new password"""
        if password:
            self._hidden_password.append(password)
    
    # -----------------------------------------------------------------------


# =====================================================================
class UnixRegistry:

    directory='.mksbackup'
    
    def __init__(self, master_key):
        path=os.path.join(os.path.expanduser('~'), self.directory)
        if not os.path.isdir(path):
            os.mkdir(path)
        self.filename=os.path.join(path, master_key)
        
    def LoadValues(self, keys=[]):
        values=dict()
        try:
            for line in open(self.filename).read().split('\n'):
                line=line.strip()
                if not line: continue
                key, value=line.split('=', 1)
                values[key]=value
        except IOError:
            pass
        return values    
                
    def SaveValues(self, values):
        # update old values
        old_values=self.LoadValues()
        old_values.update(values)
        data=""
        for k, v in old_values.iteritems():
            data+='%s=%s\n' % (k, str(v))
        filedata=open(self.filename, "w")
        filedata.write(data)
        filedata.close()
        
    def Close(self):
        pass
