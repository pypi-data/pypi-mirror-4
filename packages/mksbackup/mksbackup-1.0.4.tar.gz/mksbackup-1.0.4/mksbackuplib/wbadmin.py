#
# wbadmin.py
#
# MKBackup frontend for wbadmin
#
# (c) alain.spineux@gmail.com  


import os, sys, subprocess, time, platform
import cStringIO, zipfile, gzip
from datetime import datetime, timedelta
import xml.dom.minidom

import win32wnet
import win32netcon 

from windows import WindowsErrorDecode, windows_list_dir, is_volumeid

from archiver import *

import cron

def getvalue(parentnode, nodename):
      return parentnode.getElementsByTagName(nodename)[0].childNodes[0].data

# ===========================================================================
#
# ===========================================================================
class WbadminBase(Archiver):

    name='WBADMIN-BASE'
    exe='WBADMIN-BASE'
    
    types=dict() 
    
    # -----------------------------------------------------------------------
    def __init__(self):
        Archiver.__init__(self)

        self.destination=None
        self.type=None
        self.target=None
        self.options=[]

        systemroot=os.environ.get('SystemRoot', os.environ.get('windir', 'C:\\windows'))
        self.wbadmin_bin=os.path.join(systemroot, 'system32', 'wbadmin.exe')
        self.wevtutil_bin=os.path.join(systemroot, 'system32', 'wevtutil.exe')
        # check if we are on a x64 running a 32bit MKBackup
        if platform.machine()=='x86' and os.path.exists(os.path.join(systemroot, 'sysnative', 'wbadmin.exe')):
                # yes we are
                self.wbadmin_bin=os.path.join(systemroot, 'sysnative', 'wbadmin.exe')
                self.wevtutil_bin=os.path.join(systemroot, 'sysnative', 'wevtutil.exe')

        self.machine=platform.node()

    # -----------------------------------------------------------------------
    def load(self, job, manager):
        
        log=manager.log
        now=manager.now

        errors, warnings, extra={}, {}, ''

        #
        # check job config
        #
        self.destination=job.get('destination', None)
        if self.destination:
            self.destination=self.destination.replace('\n','')
            try:
                self.destination=Destinations(self.destination, self)
            except (DestinationSyntaxError, cron.CronException), e:
                errors['destination']='syntax error: %s' % (str(e), )

        options=job.get('options', '')
        try:
            options=quoted_string_list(options)
        except ValueError:
            errors['options']='not a valid quoted string list'
        else:
            self.options=options

        self.wbadmin_bin=job.get('wbadmin_bin', self.wbadmin_bin)
        self.wevtutil_bin=job.get('wevtutil_bin', self.wevtutil_bin)
        self.machine=job.get('machine', self.machine)

        extra+='wbadmin_bin=%s\n' % self.wbadmin_bin
        extra+='wevtutil_bin=%s\n' % self.wevtutil_bin
        
        return errors, warnings, extra
    
    # -----------------------------------------------------------------------
    def run(self, command, job, manager):

        log=manager.log
        now=manager.now

        import windows

        start=int(time.time())
        wba_del_process=None           
        if self.name=='wbadminsys' and self.keepversions:
            wba_del_args=[ self.exe, 'delete', 'systemstatebackup', '-quiet', '-keepVersions:%d'%(self.keepversions-1,), '-backupTarget:%s' % ( self.target, ), '-machine:%s' % ( self.machine, ),   ]
            log.info('run: %s', self.hide_password(' '.join(wba_del_args)))
            try:
                wba_del_process=subprocess.Popen(param_encode(wba_del_args, manager.default_encoding), executable=self.wbadmin_bin, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                wba_del_out, wba_del_err=wba_del_process.communicate()
            except Exception, e:
                log.error('Unexpected exception running command: %s', self.hide_password(' '.join(wba_del_args)))
                raise
            else:
                if wba_del_process.returncode!=0:
                    log.error('Error code=%d running command: %s', wba_del_process.returncode, self.hide_password(' '.join(wba_del_args)))
            time.sleep(2)
        
        start2=int(time.time())
        log.info('run: %s', self.hide_password(' '.join(self.wba_args)))
        try:
            wba_process=subprocess.Popen(param_encode(self.wba_args, manager.default_encoding), executable=self.wbadmin_bin, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            wba_out, wba_err=wba_process.communicate()
        except UnicodeEncodeError, e:
            st=self.hide_password(' '.join(param_encode(self.wba_args, manager.default_encoding, 'backslashreplace')))
            raise RuntimeError, 'Unicode error, avoid the use of non us-ascii characters in your .ini file: '+st
        except Exception, e:
            log.error('Unexpected exception running command: %s', self.hide_password(' '.join(self.wba_args)))
            raise
        else:
            if wba_process.returncode!=0:
                log.error('Error code=%d running command: %s', wba_process.returncode, self.hide_password(' '.join(self.wba_args)))

        end=int(time.time())
        
        # get the Events
        # Sometime I miss the last event, retry 3 times at least
        time.sleep(1)
        count=3 # try only once now
        
        ev_status, hresult, msg, backupfailurelog='ERR', '', '', None
        while count>0:
            count-=1 
            wevt_args=[ 'wevtutil.exe', 'qe', 'Microsoft-Windows-Backup', '/rd:true', '/e:root', '/f:RenderedXml',# '/f:XML',
                        '/q:*[System[TimeCreated[timediff(@SystemTime)<=%d]]]' % (1000*int(time.time()-start2+1), ), 
                      ]  
            log.info('run: %s', ' '.join(wevt_args))
            wevt_process=subprocess.Popen(param_encode(wevt_args, manager.default_encoding), executable=self.wevtutil_bin, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            wevt_out, wevt_err=wevt_process.communicate()

            if not wevt_out:
                log.info('wevtutil output is empty exit=%d ERR[:128]=%r', wevt_process.returncode, wevt_err[:128])
            else:
                dom=xml.dom.minidom.parseString(wevt_out.decode(manager.default_encoding).encode('utf-8'))
                # search all Event, for HRESULT in EventID==14
                computer=platform.node()
                # TODO: check if computer name match
                for node in dom.getElementsByTagName('Event'):
                    system=node.getElementsByTagName('System')[0]
                    if getvalue(system, 'EventID')=='14':
                        eventdata=node.getElementsByTagName('EventData')[0]
                        for data in eventdata.getElementsByTagName('Data'):
                            if data.getAttribute('Name')=='HRESULT':
                                hresult=data.childNodes[0].data
                            elif data.getAttribute('Name')=='BackupFailureLogPath':
                                try:
                                    backupfailurelog=data.childNodes[0].data
                                except IndexError:
                                    pass
                                
                        renderinginfo=node.getElementsByTagName('RenderingInfo')[0]
                        msg=getvalue(renderinginfo, 'Message')
                    break
                
                if hresult:
                    break

            if count>0:
                log.info('EventID 14 missed, retry')
                time.sleep(21)
            else:
                if wba_process.returncode==0:
                    log.warning('EventID 14 not found')
                else:
                    log.info('EventID 14 not found')
                    
        if wba_process.returncode==0 and hresult in ('0', '0x0') :
            ev_status='OK'
            flog=log.debug
        else:
            flog=log.info

        for line in wba_out.decode(manager.console_encoding).split('\n'):
            flog('> %s', line)

        status=u''
        status+='name=%s\r\n' % job['name']
        status+='program=%s\r\n' % self.name
        status+='version=%s\r\n' % self.__version__
        status+='hostname=%s\r\n' % platform.node()

        status+='status=%s\r\n' % ev_status
        
        status+='exit_code=%r\r\n' % wba_process.returncode
        status+='hresult=%s\r\n' % hresult
        status+='message=%s\r\n' % msg
        
        total_free_bytes, dir_out, dir_up_out, total_size=None, None, None, None
        
        if self.target and not is_volumeid(self.target):
            status+='target=%s\r\n' % self.target
            
            if self.target[-1]==':':
                target_dir=os.path.join(self.target+'\\', 'WindowsImageBackup', platform.node())
            else:
                target_dir=os.path.join(self.target, 'WindowsImageBackup', platform.node())
            if self.name=='wbadminsys':
                target_dir=os.path.join(target_dir, 'SystemStateBackup')
                
            # print 'ASX target_dir', target_dir
    
            # free_space
            try:
                target_full_filename=''
                total_free_bytes=free_space(self.target, log)
                # Search the Backup directory 
                dir_up_out, _ts=windows_list_dir(os.path.dirname(target_dir), log, manager.default_encoding)
                for filename in os.listdir(target_dir): #
                    full_filename=os.path.join(target_dir, filename)
                    stat=os.stat(full_filename)
                    if os.path.isdir(full_filename) and filename.lower().startswith('backup '):
                        if target_full_filename<full_filename:
                            target_full_filename=full_filename

                if target_full_filename:
                    dir_out, total_size=windows_list_dir(target_full_filename, log, manager.default_encoding)  
               
            except Exception, e:
                unc=os.path.splitunc(self.target)[0]
                if not unc or not self.user or not self.password:
                    log.error('checking target directory: %s', WindowsErrorDecode(e, manager.default_encoding))
                    status+='target_free_space=%s\r\n' % WindowsErrorDecode(e, manager.default_encoding)
                else:
                    try:
                        win32wnet.WNetAddConnection2(win32netcon.RESOURCETYPE_DISK, None, param_encode(self.target, manager.default_encoding), None, param_encode(self.user, manager.default_encoding), param_encode(self.password, manager.default_encoding))
                        try:
                            total_free_bytes=free_space(self.target, log)
                            dir_up_out, _ts=windows_list_dir(os.path.dirname(target_dir), log, manager.default_encoding)
                            for filename in os.listdir(target_dir): #
                                full_filename=os.path.join(target_dir, filename)
                                stat=os.stat(full_filename)
                                if os.path.isdir(full_filename) and filename.lower().startswith('backup '):
                                    dir_out, total_size=windows_list_dir(full_filename, log, manager.default_encoding)
                                    break  
                        finally:
                            win32wnet.WNetCancelConnection2(param_encode(self.target, manager.default_encoding), 0, False)
                    except Exception, e:
                        log.error('checking target directory: %s', WindowsErrorDecode(e, manager.default_encoding))
                        status+='target_free_space=%s\r\n' % WindowsErrorDecode(e, manager.default_encoding)
    
            if total_free_bytes:
                status+='target_free_space=%d\r\n' % total_free_bytes
            if total_size:
                status+='target_size=%d\r\n' % total_size

        # run wbadmin get versions
        wba_versions_args=[ self.exe, 'get', 'versions', ]
        #if self.target:
        #    wba_versions_args.append('-backupTarget:%s' % ( self.target, ))
        #    wba_versions_args.append('-machine:%s' % (self.machine, ))
        log.info('run: %s', ' '.join(wba_versions_args))
        wba_versions_process=subprocess.Popen(param_encode(wba_versions_args, manager.default_encoding), executable=self.wbadmin_bin, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wba_versions_out, wba_versions_err=wba_versions_process.communicate()

        status+='start=%s\r\n' % time.ctime(start)
        status+='end=%s\r\n' % time.ctime(end)
        status+='start_epoch=%d\r\n' % start
        status+='end_epoch=%d\r\n' % end
        status+='wba_cmd=%s\r\n' % self.hide_password(' '.join(self.wba_args))
        status+='wevt_cmd=%s\r\n' % ' '.join(wevt_args)
        status+='wevt_exit_code=%s\r\n' % wevt_process.returncode
        status+='wba_get_versions_cmd=%s\r\n' % ' '.join(wba_versions_args)
        status+='wba_get_versions_exit_code=%s\r\n' % wba_versions_process.returncode
        
        if wba_del_process:
            
            status+='wba_del_cmd=%s\r\n' % ' '.join(wba_del_args)
            status+='wba_del_exit_code=%s\r\n' % wba_del_process.returncode
        
        attachments=[ # the type, subtype and coding is not used
                    ]
        
        if dir_up_out:
            attachments.append(('dir_up.txt', None, dir_up_out.encode('utf-8'), 'text', 'plain', 'utf-8'))

        if dir_out:
            attachments.append(('dir.txt', None, dir_out.encode('utf-8'), 'text', 'plain', 'utf-8'))
            
        if wba_out:
            attachments.append(('wba_out.txt', None, wba_out, 'text', 'plain', manager.console_encoding))
        if wba_err:
            attachments.append(('wba_err.txt', None, wba_err, 'text', 'plain', manager.console_encoding))

        if wba_del_process and wba_del_out:
            attachments.append(('wba_del_out.txt', None, wba_del_out, 'text', 'plain', manager.console_encoding))
        if wba_del_process and wba_del_err:
            attachments.append(('wba_del_err.txt', None, wba_del_err, 'text', 'plain', manager.console_encoding))

        if wba_versions_out:
            attachments.append(('wba_versions_out.txt', None, wba_versions_out, 'text', 'plain', manager.console_encoding))
        if wba_versions_err:
            attachments.append(('wba_versions_err.txt', None, wba_versions_err, 'text', 'plain', manager.console_encoding))
        
        if wevt_out:
            attachments.append(('wevt_out.txt', None, wevt_out, 'text', 'plain', manager.default_encoding))
        if wevt_err:
            attachments.append(('wevt_err.txt', None, wevt_err, 'text', 'plain', manager.default_encoding))
 
        if backupfailurelog:
            try:
                value=open(backupfailurelog, 'r').read()
            except Exception, e:
               log.error('reading backup failure log "%s": %s', backupfailurelog.decode(manager.default_encoding, 'replace'), WindowsErrorDecode(e, manager.default_encoding))
            else:
                if len(value)>2: # BOM
                    status+=u'backup_failure_log=%s\r\n' % backupfailurelog.decode(manager.default_encoding, 'replace')
                    attachments.append(('backupfailurelog.txt', None, value, 'text', 'plain', 'utf-16'))
               
        return ev_status, status, attachments

# ===========================================================================
#
# ===========================================================================
class Wbadmin(WbadminBase):

    name='wbadmin'
    exe='wbadmin.exe'
    
    types=dict(vsscopy='vsscopy', vssfull='vssfull', copy='copy') # copy is deprecated 
    
    # -----------------------------------------------------------------------
    def __init__(self):
        WbadminBase.__init__(self)

        self.user=None
        self.password=None
        
    # -----------------------------------------------------------------------
    def load(self, job, manager):
        
        errors, warnings, extra=WbadminBase.load(self, job, manager)

        log=manager.log
        now=manager.now

        #
        # check job config
        #

        self.include=job.get('include', None)
        if self.include and not self.destination:
            errors['include']='destination required'

        self.user=job.get('user', None)
        if self.user and not self.destination:
            errors['user']='destination required'
            
        self.password=job.get('password', None)
        self.register_password(self.password)
            
        if self.user and not self.destination:
            errors['password']='destination required'

        if (self.user and not self.password) or (not self.user and self.password):
            errors['password']='login and password must be set together'

        if not errors:
            if not self.destination:
                self.type, self.target='default', None
            else:
                self.type, self.target=self.destination.match(now, self.night_shift)
                
                if self.type!=None and self.type!='none':            
                    # check the target
                    if self.target and not is_volumeid(self.target) and not os.path.isdir(self.target):
                        try:
                            os.makedirs(self.target)
                        except WindowsError, e:
                            unc=os.path.splitunc(self.target)[0]
                            if unc and self.user and self.password:
                                try:
                                    win32wnet.WNetAddConnection2(win32netcon.RESOURCETYPE_DISK, None, param_encode(unc, manager.default_encoding), None, param_encode(self.user, manager.default_encoding), param_encode(self.password, manager.default_encoding))
                                    try:
                                        if not os.path.isdir(self.target):
                                            try:
                                                os.makedirs(self.target)
                                            except WindowsError, e:
                                                errors['destination']='directory not found: %s (%s)' % (self.target, WindowsErrorDecode(e))
                                    finally:
                                        win32wnet.WNetCancelConnection2(param_encode(unc, manager.default_encoding), 0, False)
                                except Exception, e:
                                    errors['destination']='directory not found: %s (%s)' % (self.target, WindowsErrorDecode(e))
                            else:
                                errors['destination']='directory not found: %s (%s)' % (self.target, WindowsErrorDecode(e))

        if not errors:

            if self.type!=None and self.type!='none':
                
                self.wba_args=[ self.exe, 'start', 'backup', '-quiet' ]
                # TODO: remove this
                
                if self.target:
                    self.wba_args.append('-backupTarget:%s' % ( self.target, ))
                    
                if self.include:
                    self.wba_args.append('-include:%s' % ( self.include, ))
                
                if self.target and self.target.startswith('\\\\') and not is_volumeid(self.target) and self.user and self.password:
                    self.wba_args+=[ '-user:%s' % ( self.user, ), '-password:%s' % ( self.password,) ]
                    
                if self.type.lower()=='vssfull':
                    self.wba_args.append('-vssFull')
                elif self.type.lower()=='vsscopy':
                    self.wba_args.append('-vssCopy')
                    
                self.wba_args.extend(self.options)
                extra+='cmdline=%s\n' % self.hide_password('  '.join(self.wba_args))
    
        return errors, warnings, extra


# ===========================================================================
#
# ===========================================================================
class WbadminSys(WbadminBase):

    name='wbadminsys'
    exe='wbadmin.exe'
    
    types=dict(systemstate='systemstate')

    # -----------------------------------------------------------------------
    def load(self, job, manager):
        
        log=manager.log
        now=manager.now

        errors, warnings, extra=WbadminBase.load(self, job, manager)

        #
        # check job config
        #
            
        if not self.destination:
            errors['destination']='destination required'

        self.keepversions=job.get('keepversions', None)
        if self.keepversions:
            try:
                self.keepversions=int(self.keepversions)
                if self.keepversions<1:
                    errors['keepversions']='must be >= 1'
            except Exception:
                errors['keepversions']='must be an integer'

        if not errors:

            if self.destination:
                self.type, self.target=self.destination.match(now, self.night_shift)
    
            if self.type!=None and self.type!='none':
                
                self.wba_args=[ self.exe, 'start', 'systemstatebackup', '-quiet']
                if self.target:
                    self.wba_args.append('-backupTarget:%s' % ( self.target, )) 

                self.wba_args.extend(self.options)
                extra+='cmdline=%s\n' % '  '.join(self.wba_args)
    
        return errors, warnings, extra


# http://social.technet.microsoft.com/Forums/en/windowsbackup/thread/1437d4ab-e0eb-40af-953c-ca2d0b5d951f
#The backup versions are stored on the VSS shadow copies on the backup volume. 
#If space for the current backup is not enough, the older backup shadow copy 
#is reclaimed to make space for the new backup. It is recommended that the 
#backup target free space be at least 1.5 times the backup sources volume's 
#space, and the backup target be used for only storing backups 
#(other data churn on the backup target, may cause loss of shadowcopies, hence 
#loss of backup versions). Increasing the space allocated for shadow copies can 
#increase the number of backups avaliable. This can be done using the 
#vssadmin.exe utility, the command below will enable all the space in the 
#backup target to be used for shadow copies.
#
#vssadmin resize shadowstorage /for=d: /on=d: /maxsize=unbounded 
#
#Note: If Faster backup performance setting is turned on, Windows will leave
#a shadow copy on the source volume to use to track the changes. During next 
#backup operation, only the changes since last the backup are transferred
#(by reading from the "diff area" of the source volume shadow copy)-as 
#compared to the Normal backup performance option, where the entire source 
#volume data is transferred. (Because only changed blocks are written, there 
#is a performance increase.) The space used on the backup storage location 
#will still only be for the changed blocks detected on the source. Use this 
#method for servers that are less I/O intensive because shadow copies can 
#degrade the performance of write operations for the volume they are on 
#(read operations are not affected).
#

# http://social.technet.microsoft.com/Forums/en/windowsbackup/thread/3d4b3a2a-3f4f-4866-8d05-9baa86279e18
#You use the VSS Full Backup with VSS Aware applications like SQL Server, 
#Exchange Server to clear the transaction logs when the backup completed 
#succesfully. This is what they mean with 'Clearing application logs'.
#
#The best way to explain this is: Other backup applications clear the Archive 
#bit when the file is backed up, so they know this file has already been done. 
#When the file gets changed in any way after the backup, the archive bit is 
#set again so the backup application knows that the file needs to backed up.
#
#The VSS Copy Backup doesn't do anything with the archive bit, if it's on, 
#it's on. If it's off, it's off. If you use another product to backup the 
#same volume, use the VSS copy backup. If Windows Server Backup is the only 
#program you use, use the VSS Full Backup.

# http://social.technet.microsoft.com/Forums/en/windowsbackup/thread/d0fe1d25-c425-4491-af0e-e6ac199d89a1
#In Windows Server 2008 R2, there are several reasons which may cause the 
#windows backup to be full instead of incremental.
#
#1. Backup on the target is deleted/not present.
#2. Source volume VSS snapshot is deleted, from which the last backup was 
#taken, this can happen if the diff area on the source volume was reset, or 
#high data churn happen causing the older shadow opy to be claimed.
#3. 14 days have passed or 6 incremental backups have happened since the last 
#full backup.
#4. Churn on the backup source is high (more than 50%)
#
#Decision to do full vs incremental is a run-time decision that windows backups 
#takes. If all the conditions necessary for an incremental backup are not met, 
#a full backup is taken even if incremental backup settings are set.


# http://technet.microsoft.com/en-us/library/ee344835%28WS.10%29.aspx?ppud=4
# What's New in Windows Server Backup

# http://www.smaro.ch/blogs/Lists/Beitraege/Post.aspx?ID=772
# Backup Version and Space Management in Windows Server Backup

# http://www.tipandtrick.net/2008/how-to-suppress-and-bypass-system32-file-system-redirect-to-syswow64-folder-with-sysnative/
# How to Suppress and Bypass System32 File System Redirect to SysWOW64 Folder with Sysnative

# to install Windows Server Backup (command line)
# servermanagercmd.exe -install Backup-Features

# http://technet.microsoft.com/en-us/library/dd364735(WS.10).aspx
# There can be two ways to check if the backup had failed from the events:
#1. For every backup run, successful or failed, event-id 14 is generated. 
# The event-data for this ID contains the overall status of the backup in the 
# field 'HRESULT'. This should be 0 for a successful backup, non-zero otherwise.
#


# 
# http://social.technet.microsoft.com/Forums/en-US/windowsbackup/thread/13bb79e9-c970-4805-88cb-2000b3348070
# when backupping 2008 R2 on a samba server, share must have option 
# "strict allocate = yes" set
# Then remove existing file, they are "sparce/corrupted" and will make next backup fail 

