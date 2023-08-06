#!/bin/env python
#
# main.py
#
# (c) Alain Spineux alain.spineux@gmail.com
#
# mksbackup is a front-end for popular and free linux and windows archiver tools.
#
# Supported archiver:
# - ntbackup
# - wbadmin
# - tar
# - ghettoVCB

# Features:
# - job definitions are stored in a configuration file
# - the destination of the archive can be set to different location depending
#   on the day, the week or the month to allow very complex schema of backup
# - send and email at the end of job
# - the email contains all information to evalute the reliability of the backup jobs
#
#
# mksbackup is released under the GNU GPL license
#

import sys, os, subprocess, time, smtplib, calendar, re, socket, urllib, urllib2, logging, logging.handlers, codecs
import traceback, StringIO 
import platform, locale 
from optparse import OptionParser
import ConfigParser

from datetime import datetime, timedelta

from archiver import boolean, check_mail_config, Destinations, sendmail, Manager, send_mail_report, write_status, ftp_url_re

import cron

if sys.platform in ('win32', ):
    from windows import WindowsErrorDecode as ErrorDecode
else:
    from archiver import ErrorDecode

from version import __version__

last_version_url='http://www.magikmon.com/download/mksbackup/last2.txt'

def repl_ftp_password(m):
    """used by re.sub to replace ftp password by ***********"""
    username, password, host, port, directory=m.group('username', 'password', 'host', 'port', 'directory')
    st='ftp://'
    if username:
        host='@'+host
        st+=username
    if password:
        st+=':********'
        
    st+=host
    if port:
        st+=':'+port
    if directory:
        st+=directory
    return st
        
        
def gen_archiver(name):
    name=name.lower()
    if name=='ntbackup':
        import ntbackup
        return ntbackup.NTBackup
    elif name=='tar':
        import tar
        return tar.Tar
    elif name=='ghettovcb':
        import ghettovcb
        return ghettovcb.Ghettovcb
    elif name=='esxmon':
        import esxmon
        return esxmon.ESXMon
    elif name=='wbadmin':
        import wbadmin
        return wbadmin.Wbadmin
    elif name=='wbadminsys':
        import wbadmin
        return wbadmin.WbadminSys
    else:
        return None

# ---------------------------------------------------------------------------
def update_check(version, backend):
    """Check if and new version of MKSBackup is available and return the
    announcement message if available
    """
    
    up2date, msg='yes', ''
    data=urllib.urlencode(dict(version=version, backend=backend, platform=sys.platform, osver=platform.version()[:10]))
    current=__version__.split('.')

    try:
        data=urllib2.urlopen('%s?%s' % (last_version_url, data)).read()
#        data=urllib2.urlopen(last_version_url, data).read()
        state='version'
        msg=''
        vall=vbackend=None
        for line in data.split('\n'):
            line=line.strip()
            if not line:
                state='msg'
                continue
            if state=='version':
                try:
                    prog, ver=line.split(':')
                except ValueError:
                    continue
                else:
                    prog=prog.strip()
                    ver=ver.strip()
                    if prog==backend:
                        vbackend=ver
                    elif prog=='*':
                        vall=ver
            elif state=='msg':
                msg+=line+'\n'

        if vbackend==None:
            vbackend=vall
            
        if vbackend!=None:
                    
            last=vbackend.split('.')
            for i in range(min(len(current), len(last))):
                if int(current[i])<int(last[i]):
                    up2date='no'
                    break
            
    except (urllib2.URLError, urllib2.HTTPError):
#        raise
        up2date='unk'
    except Exception, e:
#        raise
        up2date='unk'

    return up2date, msg

# ---------------------------------------------------------------------------        
def gen_status(start, job, status, end):

    if end==None:
        end=int(time.time())
    st=u''
    st+='name=%s\r\n' % job['name']
    st+='program=%s\r\n' % job.get('program','')
    st+='version=%s\r\n' % __version__
    st+='status=%s\r\n' % (status, )
    st+='hostname=%s\r\n' % platform.node()
    st+='start=%s\r\n' % time.ctime(start)
    st+='end=%s\r\n' % time.ctime(end)
    st+='start_epoch=%d\r\n' % start
    st+='end_epoch=%d\r\n' % end
    return st

# ---------------------------------------------------------------------------        
def mail_exception(start, job, extra, manager, subject, status):
    
    msg_body=job['msg_header']
    msg_body+='\nUnexpected error, read "traceback.txt" for more\n\n'
    msg_body+='\n%s\n' % status
    msg_body+=extra+'\n'

    try:
        tb=StringIO.StringIO()
        exctype, value = sys.exc_info()[:2]
        traceback.print_exc(None, tb)
        tb_st=tb.getvalue()
        tb.close()
    except Exception, e:
        tb_st='Traceback failed: %r' % e
    
    attachments=manager.attachments[:]
    attachments+=[ # the type, subtype and coding is not used
           ('traceback.txt', None, tb_st.decode('ascii', 'replace'), 'text', 'plain', 'utf-8'), # ascii is already utf8, no need to encode
           ('status.txt', None, status.encode('utf-8'), 'text', 'plain', 'utf-8'),
    ]

    try:
        log_output=manager.stop_logging()
        attachments.append(('logging.txt', None, log_output.encode('utf-8'), 'text', 'plain', 'utf-8'))
    except Exception:
        msg_body+='\nminor error when attaching logging\n'                      
    
    errmsg=sendmail(job, subject, msg_body, attachments, manager.log, 'exception')


class MyFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, encoding='utf-8'):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.encoding=encoding
 
    def format(self, record):
        t=logging.Formatter.format(self, record)
        return t
        # ASX
        if isinstance(t, unicode):
            t=t.encode(self.encoding, 'replace')
        return t

#======================================================================
#
# Main
#
#======================================================================

#
# Parse the command line
#
def main():

    if len(sys.argv)>1 and sys.argv[1]=='ftp':
        args=sys.argv[:]
        args.remove('ftp')
        import ftpd
        ftpd.ftpmain(args)
        sys.exit(0)
    
    parser=parser=OptionParser(version='%%prog %s' % __version__ )
    parser.set_usage('%prog [options] command [job..]\n\n'
                     '\tcommand in "backup", "check", "checkmail"\n\n'
                     '\tuse "ftp" in first place to start buil-in ftp server,\n'
                     '\tuse "ftp -h" in this order for more')
    
    parser.add_option("-c", "--config", dest="config", default='mksbackup.ini', help="use another ini file", metavar="configfile")
    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False, help="switch to debug level, increase verbosity")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=True, help="write logging to the terminal (default)")
    parser.add_option("-q", "--quiet", dest="verbose", action="store_false", default=True, help="don't write logging to the terminal")
    parser.add_option("-l", "--logfile", dest="logfile", default='mksbackup.log', help="log to this file", metavar="logfile")
    parser.add_option("-s", "--statusdir", dest="statusdir", default=None, help="the directory where to write status of this backup", metavar="statusdir")
    parser.add_option("-e", "--encoding", dest="encoding", default='auto', help="configuration file encoding", metavar="encoding")
    
    parser.add_option("-i", "--install", dest="install", action="store_true", help="install and pre-setup a task in scheduler")
    
    cmd_options, cmd_args=parser.parse_args(sys.argv)
    
    if cmd_options.install or len(sys.argv)==1:
        import install
        try:
            res=install.Install()
        except Exception, e:
            print 'Unexpected Error: %s' % (e, )
            raise
        sys.exit(res)
    
    root_handler=logging.handlers.RotatingFileHandler(cmd_options.logfile, 'a', 1024**2, 2)
    root_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-3.3s %(message)s', '%Y-%m-%d %H:%M:%S'))
    log=logging.getLogger()
    log.setLevel(logging.INFO)
    log.addHandler(root_handler)
    
    if cmd_options.debug:
        log.setLevel(logging.DEBUG)
    else:
        # this stop early the logging process of loglevel<=DEBUG and should 
        # improve performance a little bit
        logging.disable(logging.DEBUG)
    
    logging.getLogger("paramiko").setLevel(logging.WARNING)
        
    if cmd_options.verbose:
        console=logging.StreamHandler()
        encoding=sys.stderr.encoding
        if encoding==None:
            encoding='ascii'
        console.setFormatter(MyFormatter('%(asctime)s,%(msecs)03d %(levelname)-3.3s %(message)s', '%H:%M:%S', encoding=encoding))
        log.addHandler(console)
    
    log.info(u'start version=%s cmd=%r', __version__, sys.argv)
    
    if len(cmd_args)<2:
        parser.error('no "command" set')
        
    command=cmd_args[1]
    if command.lower() not in ('backup', 'check', 'checkmail'):
        parser.error('invalid command "%s"' % command)
    
    command=command.lower()
    
    if command=='backup':
        command_display='BACKUP'
    else:
        command_display='CONFIG'
        
    job_list=cmd_args[2:]
    
    if not job_list:
        parser.error('no "job"')
    
    # define a default_encoding
    default_encoding=locale.getdefaultlocale()[1]
    console_encoding=sys.stderr.encoding
    
    if not default_encoding:
        # use default per platform
        if sys.platform in ('win32', ):
            default_encoding='windows-1252'
        else:
            default_encoding='utf-8'
    
    if not console_encoding:
        # use default per platform
        if sys.platform in ('win32', ):
            console_encoding='cp850'
        else:
            console_encoding='utf-8'

    #
    # load the configuration file
    #
    config_default=dict(verify='no',
                        update_check='yes',
                        smtp_host='127.0.0.1',
                        smtp_mode='normal',
                        night_shift='yes',
                        attachment_size='1000',
                        attachment_gzip='100',
                        )
    
    try:
        config_file=open(cmd_options.config, 'r')
    except IOError, e:
        log.error('error reading configuration file "%s": %s', cmd_options.config, ErrorDecode(e, default_encoding))
        sys.exit(1)
    
    config_text=config_file.read()
    config_file.close()
    config_file=None
    
    if cmd_options.encoding=='auto':
        # try to guess the file encoding  
        bomdict = { codecs.BOM_UTF8 : ('utf-8', 1),  # or ( 'utf_8_sig', 0) but utf_8_sig dont exist in 2.4
                    codecs.BOM_UTF16_BE : ('utf-16', 0),
                    codecs.BOM_UTF16_LE : ('utf-16', 0) }
    
        for bom, (encoding, skip) in bomdict.items():
            if config_text.startswith(bom):
                cmd_options.encoding=encoding
                cmd_options.skip=skip
                config_file=codecs.open(cmd_options.config, 'r', encoding)
                if skip:
                    config_file.read(skip)
                break
        
        if cmd_options.encoding=='auto':
            # if no BOM use default
            cmd_options.encoding=default_encoding
            config_file=codecs.open(cmd_options.config, 'r', cmd_options.encoding)
    else:
        try:
            config_file=codecs.open(cmd_options.config, 'r', cmd_options.encoding)        
        except LookupError, e:
            log.error('error reading configuration file %s: %s', cmd_options.config, ErrorDecode(e, default_encoding))
            sys.exit(1)
    
    config=ConfigParser.RawConfigParser(config_default)
    try:
        config.readfp(config_file)
    except (IOError, UnicodeDecodeError), e:
        log.error('error reading configuration file %s: %s', cmd_options.config, ErrorDecode(e, default_encoding))
        sys.exit(1)
    
    err, failed_job=0, job_list[:]
    for job_name in job_list:
        try:
            program=config.get(job_name, 'program')
        except ConfigParser.NoOptionError, e:
            log.error('no "program" set for job "%s"', job_name)
            err+=1
        except ConfigParser.NoSectionError, e:
            log.error('job not found: %s',job_name)
            err+=1
        else:
            if not gen_archiver(program):
                log.error('program "%s" unknown in job "%s"', program, job_name)
                err+=1
            else:
                failed_job.remove(job_name)
                
                # check for update for this back-end
                
                up2date, up2date_msg='unk', ''
                check_for_update=config.get(job_name, 'update_check')
                if boolean.get(check_for_update.lower(), None)!=False:
                    up2date, up2date_msg=update_check(__version__, program)
                    if up2date=='no':
                        log.warning('!'*60)
                        for line in up2date_msg.split('\n'):
                            if line:
                                log.warning(line)
                        log.warning('!'*60)

                config.set(job_name, 'up2date', up2date)
                config.set(job_name, 'up2date_msg', up2date_msg)
    
    if err>0:
        parser.error('in jobs: %s' % ' '.join(failed_job))
        sys.exit(3)
    
    exit_code=0
    
    # remove password from .INI file 
    sanitized_config_file_content=codecs.open(cmd_options.config, 'r', cmd_options.encoding).read()
    for password_key in ('password', 'smtp_password',):
        sanitized_config_file_content=re.sub('(?m)^#?(?P<key>\s*%s\s*)=(?P<value>.*)$' % (password_key,), '\g<key>=********', sanitized_config_file_content)

    sanitized_config_file_content=ftp_url_re.sub(repl_ftp_password, sanitized_config_file_content)
    
    manager=Manager(platform.node(), log)
    manager.default_encoding=default_encoding
    manager.console_encoding=console_encoding
    manager.formater=MyFormatter('%(asctime)s %(levelname)-3.3s %(message)s', '%Y-%m-%d %H:%M:%S', encoding='utf-8')

    manager.sanitized_config_file_content=sanitized_config_file_content
    
    manager.attachments=[ ('config.ini', None, manager.sanitized_config_file_content.encode(cmd_options.encoding), 'text', 'plain', cmd_options.encoding), ] 
    
    for job_name in job_list:
    
        manager.start_logging()
    
        now=datetime.now()
        manager.now=now
        start=int(time.time())
        job=dict(config.items(job_name))
        program=job.get('program')
        arch=gen_archiver(program)()
        arch.__version__=__version__
        arch.night_shift=boolean.get(job.get('night_shift', 'on').lower(), True)
        job=dict(config.items(job_name))
        job['name']=job_name
        job['config']=cmd_options.config
        job['config_encoding']=cmd_options.encoding
                
        if job['up2date']=='no':
            job['msg_header']='\n%s\n' % job['up2date_msg']
        else:
            job['msg_header']=''
        
        mail_config_errors=check_mail_config(job)
    
        # check job parameters 
        
        try:
            errors, warnings, extra=arch.load(job, manager)
        except Exception, e:
            try:
                log.exception('loading job %s by program %s', job_name, program)
            except UnicodeDecodeError:
                log.error('loading job %s by program %s: %s', job_name, program, ErrorDecode(e, default_encoding))

            status=gen_status(start, job, 'ERR', None)
            status+='runtime_error=%r\r\n' % sys.exc_info()[1]
    
            if job['mail'] and not mail_config_errors:
                subject='MKSBACKUP %s ERR %s ' % (command_display, job['name'], )
                mail_exception(start, job, '', manager, subject, status)
            
            if cmd_options.statusdir:
                write_status(status, cmd_options.statusdir, job['name'])
            
            continue
    
        for line in extra.split('\n'):
            if line:
                log.info('    %s', line)
    
        errors.update(mail_config_errors)
        
        msg_body=job['msg_header']
            
        if errors:
            exit_code=3
            msg_body+='Errors in section: %s\n\n' % job['name']
            log.error('Errors in section: %s', job['name'])
            for k, v in errors.iteritems():
                log.error('\tparameter "%s" : %s', k, v)
                msg_body+='       parameter "%s" : %s\n\n' % (k, v)
    
            for k, v in warnings.iteritems():
                log.warning('%s: %s', k, v)
                msg_body+='%s\n    %s\n\n' % (k, v)
                    
            if job['mail'] and not mail_config_errors and not command=='check':
                subject='MKSBACKUP %s ERR %s ' % (command_display, job['name'], )
                status=gen_status(start, job, 'ERR', None)
                attachments=manager.attachments[:]
                attachments.append(('status.txt', None, status.encode('utf-8'), 'text', 'plain', 'utf-8')),
                errmsg=sendmail(job, subject, msg_body, attachments, manager.log, 'err')
                if cmd_options.statusdir:
                    write_status(status, cmd_options.statusdir, job['name'])

            continue
    
        if warnings:
            log.warning('Warnings in section: %s', job['name'])
            for k, v in warnings.iteritems():
                log.warning('%s: %s', k, v)
        else:
            log.info('No errors in section: %s', job['name'])
    
        destination=getattr(arch, 'destination', None)
        
        if command in ('check', 'checkmail'):
            msg_body=job['msg_header']
            if destination and isinstance(destination, Destinations): 
                msg_body+='Destinations day by day:\n\n'
                log.info('Destinations day by day:')
                for i in range(destination.full_cycle):
                    today=now+timedelta(days=i)
                    typ, target=destination.match(today, night_shift=arch.night_shift)
                    if typ=='none':
                        ty='none'
                        target='-----------------'
                    elif typ==None:
                        ty=''
                        target='??? no target ???'
                    else:
                        ty=typ
                    msg_body+='    %s %-12s %s\n' % (today.strftime('%a %d %b %Y'), ty, target)
                    log.info('    %s %-12s %s', today.strftime('%a %d %b %Y'), ty, target)

                    if typ!='none' and typ!=None:
                        if target.startswith('ftp://'):
                            msg_body+='      ftp directory not tested\n'
                            log.info('       ftp directory not tested: %s', target)
                        elif not os.path.isdir(os.path.dirname(target)):
                            msg_body+='        directory not found !!!\n'
                            log.warning('        directory not found: %s', os.path.dirname(target))
                        
            msg_body='%s\n\n%s\n' % (msg_body, extra)
            if job['mail'] and command=='checkmail':
                subject='MKSBACKUP %s OK %s ' % (command_display, job['name'], )
                errmsg=sendmail(job, subject, msg_body, manager.attachments, manager.log, 'check')
            continue 
    
        #print 'destination', destination
        if destination and isinstance(destination, Destinations): 
            typ, target=destination.match(now, night_shift=arch.night_shift)
            if typ=='none' or typ==None:
                log.info('bye, no backup today')
                continue
    
        log.info('start command=%s job=%s archiver=%s', command, job_name, program)
        try:
            result=arch.run(command, job, manager)
        except Exception, e:
            exit_code=2
            try:
                log.exception('running command=%s job=%s archiver=%s', command, job_name, program)
            except UnicodeDecodeError:
                log.error('running command=%s job=%s archiver=%s : %s', command, job_name, program, ErrorDecode(e, default_encoding))

            status=gen_status(start, job, 'ERR', None)
            status+='runtime_error=%r\r\n' % sys.exc_info()[1]

            if job['mail']:
                subject='MKSBACKUP BACKUP ERR %s ' % (job['name'], )
                mail_exception(start, job, extra, manager, subject, status)

            if cmd_options.statusdir:
                write_status(status, cmd_options.statusdir, job['name'])
                
        else:
            log.info('end command=%s job=%s archiver=%s', command, job_name, program)
    
            if isinstance(result, int):
                exit_code=max(exit_code, result)
            else:
                if result[0]!='OK':
                    exit_code=max(exit_code, 1)
    
                if cmd_options.statusdir:
                    write_status(result[1], cmd_options.statusdir, job['name'])
                    
                errmsg=send_mail_report(job, result, manager)

        
    log.info('final exit code=%d', exit_code)

    return exit_code
    
if __name__ == "__main__":
    sys.exit(main())


#<full,first su>S:\monthly\data-full-month-${month%2}.bkf
#<full,su>S:\week${week%4}\data-full-%a.bkf
#<inc,mo-sa>S:\week${week%4}\data-inc-%a.bkf



#<full,week%4=0>S:\data-full.bkf
#<inc,week%4=1>S:\data-inc.bkf

#
#w1/4
#jan/2,su
#feb-dec/2


# when start a week
# firstday=sat
#last day OF THE MONTH
#1st mon,2nd tue,3th wed,4th thu,last sat  OF THE MONTH
#1st week,2nd week,3th week,4th week,last week OF THE MONTH
#<> => empty selector to allow "no backup"
# empty target => no backup



# http://www.scalabium.com/faq/dct0082.htm
# To detect the code page of Windows operation system you must call the GetACP function from Windows API.
# If you needs to read the code page of "DOS" sessions, you must call the GetOEMCP function from Windows API. This function will return the value:
# http://msdn.microsoft.com/en-us/library/dd318070%28VS.85%29.aspx

#


# windows unicode file http://www.helpware.net/FAR/help/Unicode2.htm
# Universal Encoding Detector http://chardet.feedparser.org/docs/supported-encodings.html


# wbadmin
#
# How to use wbadmin to backup in Windows Vista 2008
# http://www.howtonetworking.com/Windows/wbadmin1.htm
#
# Backup Version and Space Management in Windows Server Backup
# https://blogs.technet.com/filecab/archive/2009/06/22/backup-version-and-space-management-in-windows-server-backup.aspx
#
# Customizing Windows Server Backup Schedule
# http://blogs.technet.com/filecab/archive/2009/04/13/customizing-windows-server-backup-schedule.aspx
#
# %windir%\logs\windowsserverbackup
#
# Output of command "Vshadow -wm2" ran on an elevated command prompt
#
# Deleting System State Backup:
# wbadmin delete systemstatebackup -deleteOldest
# wbadmin delete systemstatebackup -keepversions:10   
# The above command will keep the latest 10 versions and delete the rest all the system state backups.
#
# Deleting other backups:  Backup application stores multiple backup versions in the VSS shadow copies. Hence, older backup version can be deleted by deleting older shadow copy. Commands to list and delete VSS shadow copies are below. They need to be run in an elevated command window.
# vssadmin list shadows /for=x: ? for listing the snapshots on x: where x: is the backup location
# vssadmin delete shadows /for=x:  /oldest ? for delete the oldest shadow copy. It can be called multiple times in case there is need to delete multiple older backups.
# Note: wbadmin get versions or backup UI would still report deleted backups until next backup runs. At end of each backup ? non-existent backups are removed from the backup catalog.
#
# Win2k8: the backups are stored inside the    <drive_letter>:\WindowsImageBackup\<machineName>\SystemStateBackup
# Win2k8 R2: the backups are stored inside the <drive_letter>:\WindowsImageBackup\<machineName>\BackupSet<..>\ path

