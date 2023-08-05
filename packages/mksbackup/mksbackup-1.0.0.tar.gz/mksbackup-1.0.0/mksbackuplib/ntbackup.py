#
# ntbackup.py
#
# ntbackup manager for mkbackup
# 
# (c) alain.spineux@gmail.com

import os, sys, subprocess, time, platform
from datetime import datetime, timedelta
import win32com.shell
from win32com.shell import shell, shellcon

from archiver import *
from windows import WindowsErrorDecode, windows_list_dir

import cron


# ===========================================================================
class NTBackup(Archiver):
    # http://support.microsoft.com/kb/814583
    # http://support.microsoft.com/default.aspx?scid=kb;en-us;233427
    #
    # Normal - selected files, marking their archive attributes
    # Copy - selected files without marking their archive attributes. This is good for making tape copies that do not interfere with archive backups, since it does not set the archive attribute.
    # Incremental - selected files, marking their archive attributes, but only backs up the ones that have changed since the last backup.
    # Differential - selected files, NOT marking their archive attributes, but only backs up the ones that have changed since the last backup.
    # Daily - only backs up files that have changed that day, does not mark their archive attributes.
    #
    # ntbackup stuff
    #   http://www.fishbrains.com/2007/11/12/utilizing-the-built-in-windows-backup-ntbackupexe-for-windows/
    #   http://episteme.arstechnica.com/eve/forums/a/tpc/f/12009443/m/165002540831
    
    name='ntbackup'
    exe='ntbackup.exe'
    ev_logtype='Application'
    ev_source='NTBackup'
    
    boolean={ True: 'yes', False:'no'}
    onoff={ True: 'on', False:'off'}
    
    types=dict(normal='normal', full='normal', incremental='incremental', inc='incremental', differential='differential', diff='differential', copy='copy', daily='daily')

    # -----------------------------------------------------------------------
    def __init__(self):
        Archiver.__init__(self)
        
        self.selection=None
        self.verify=None
        self.restricted=None
        self.logdir=None
        self.snap=None
        self.options=[]
        
        self.type=None
        self.target=None
        self.target_dir=None
        self.target_tape=None

        systemroot=os.environ.get('SystemRoot', os.environ.get('windir', 'C:\\windows'))
        self.program_exe=os.path.join(systemroot, 'system32', 'ntbackup.exe')

        self.is64bits=os.path.isdir(os.path.join(systemroot, 'SysWOW64'))            

        # check if we are on a x64 running a 32bit MKBackup
        
    # -----------------------------------------------------------------------
    def load(self, job, manager):
        
        log=manager.log
        now=manager.now

        errors, warnings, extra={}, {}, ''

        #
        # check job config
        #
        
        self.selection=job.get('selection', None)
        if not self.selection:
            errors['selection']='option mandatory'
        else:
            if self.selection.startswith('"') and self.selection.endswith('"'):
                self.selection=self.selection[1:-1]
            if self.selection.startswith('@'):
                if not os.path.isfile(self.selection[1:]):
                    errors['selection']='file not found: %s' % (self.selection[1:],)
            elif os.path.isfile(self.selection) and self.selection[-4:].lower()=='.bks':
                errors['selection']='looks like a ".bks" file and need to be prefixed by a @'
            elif not os.path.isdir(self.selection) and not os.path.isfile(self.selection):
                errors['selection']='file or directory not found'

        self.verify=boolean.get(job.get('verify', 'no').lower(), None)
        if self.verify==None:
            errors['verify']='boolean must have value in (on, yes, true, 1, off, no, false and 0)'

        if job.get('snap'):
            self.snap=boolean.get(job.get('snap').lower(), None)
        if self.verify==None:
            errors['snap']='boolean must have value in (on, yes, true, 1, off, no, false and 0)'

        self.restricted=boolean.get(job.get('restricted', 'no').lower(), None)
        if self.restricted==None:
            errors['restricted']='boolean must have value in (on, yes, true, 1, off, no, false and 0)'

        self.logdir=job.get('logdir', None)
        if not self.logdir:
            self.logdir=os.path.join(shell.SHGetPathFromIDList(shell.SHGetSpecialFolderLocation (0, shellcon.CSIDL_LOCAL_APPDATA)), 'Microsoft\Windows NT\NTBackup\data')
            # dont check if logdir exist here because ntbackup.exe will create it
        else:
            if self.logdir.startswith('"') and self.logdir.endswith('"'):
                self.logdir=self.logdir[1:-1]

        if not os.path.isdir(self.logdir):
            # I want to be sure the user know what he is doing
            warnings['logdir']='directory not found ! Notice, NTBackup create its "logdir" directory at first run'
    
        self.program_exe=job.get('ntbackup', self.program_exe)
        if self.program_exe.startswith('"') and self.program_exe.endswith('"'):
            self.program_exe=self.program_exe[1:-1]
        
        if not os.path.exists(self.program_exe):
            if self.is64bits:
                errors['ntbackup']='file "%s" not found ! On 64bits system you must use the 64bits trick, see the doc for more' % (self.program_exe, )
            else:
                errors['ntbackup']='file "%s" not found ! ' % (self.program_exe, )

        self.destination=job.get('destination', None)
        if not self.destination:
            errors['destination']='option mandatory'
        else:
            self.destination=self.destination.replace('\n','')
            try:
                self.destination=Destinations(self.destination, self)
            except (DestinationSyntaxError, cron.CronException), e:
                errors['destination']='syntax error: %s' % (str(e), )
            else:
                self.type, self.target=self.destination.match(now, self.night_shift)
                if self.type!=None and self.type!='none':
                    if self.target[:7].lower() in ('tape://', 'tape:\\'):
                        self.target_dir=None
                        self.target_tape=self.target[7:]
                    else:
                        self.target_tape=None
                        self.target_dir=os.path.dirname(self.target)
                        if not os.path.isdir(self.target_dir):
                            try:
                                os.makedirs(self.target_dir)
                            except WindowsError, e:
                                errors['destination']='directory not found: %s (%s)' % (self.target_dir, WindowsErrorDecode(e))

        options=job.get('options', '')
        try:
            options=quoted_string_list(options)
        except ValueError:
            errors['options']='not a valid quoted string list'
        else:
            self.options=options

        
        extra+='ntbackup=%s\n' % self.program_exe

        if not errors:
    
            if self.type!=None and self.type!='none':
                
                # ntbackup backup "@m:\asx\src\magik\job1.bks" /a /d "Set created 14/11/2009 at 2:29" 
                # /v:no /r:no /rs:no /hc:off /m normal /j "backup" /l:s /f "s:\Backup.bkf"
                self.cmd_args=[ self.program_exe, 'backup', self.selection, '/J', job['name'], '/M', self.type, '/rs:no', ]
                if self.target_dir: 
                    self.cmd_args.extend(['/F', self.target])
                if self.target_tape: 
                    self.cmd_args.extend(['/P', self.target_tape, '/um'])
                if job.get('description', None): self.cmd_args.extend(['/d', job.get('description')])
                self.cmd_args.append('/v:'+self.boolean[self.verify])
                self.cmd_args.append('/r:'+self.boolean[self.restricted])
                if self.snap:
                    self.cmd_args.append('/SNAP:'+self.onoff[self.snap])
                
                self.cmd_args.append('/l:s') # logging [s]ummary
                self.cmd_args.extend(self.options)
                # '/hc:off'
            
                extra+='cmdline=%s\n' % '  '.join(self.cmd_args)
    
        return errors, warnings, extra
        
    # -----------------------------------------------------------------------
    def run(self, command, job, manager):

        log=manager.log
        now=manager.now

        import windows

        try:
            start=int(time.time())
            process=subprocess.Popen(param_encode(self.cmd_args, manager.default_encoding), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            std_out, std_err=process.communicate()
            end=int(time.time())
        except UnicodeEncodeError, e:
            st=' '.join(param_encode(self.cmd_args, manager.default_encoding, 'backslashreplace'))
            raise RuntimeError, 'Unicode error, avoid the use of non us-ascii characters in your .ini file: '+st
        except WindowsError:
            log.error('command: %r', self.cmd_args)
            if self.is64bits: 
                log.error('On 64bits system you must use the 64bits trick, check the doc for more...')
            raise

        # choose the oldest log file
        logfile, last=None, 0
        for filename in os.listdir(self.logdir):
            full_filename=os.path.join(self.logdir, filename)
            current=os.stat(full_filename).st_mtime
            if last<current:
                logfile, last=full_filename, current
                
        # retrieve records in the event viewer
        ev_status, ev_out=windows.ReadEvLog(NTBackup.ev_logtype, NTBackup.ev_source, log, start)
        if not ev_out:
            log.warning('event log is empty')

        if logfile:
            if ev_status=='OK':
                flog=log.debug
            else:
                flog=log.info
            for line in open(logfile, 'r').read().decode('utf-16').split('\n'):
                flog('> %s', line)
        
        status=u''
        status+='name=%s\r\n' % job['name']
        status+='program=%s\r\n' % self.name
        status+='version=%s\r\n' % self.__version__
        status+='hostname=%s\r\n' % platform.node()
        
        status+='status=%s\r\n' % ev_status

        status+='exit_code=%r\r\n' % process.returncode
        status+='start=%s\r\n' % time.ctime(start)
        status+='end=%s\r\n' % time.ctime(end)
        status+='logfile=%s\r\n' % logfile.decode(manager.default_encoding, 'backslashreplace')
        
        status+='start_epoch=%d\r\n' % start
        status+='end_epoch=%d\r\n' % end
        status+='selection=%s\r\n' % self.selection
        status+='type=%s\r\n' % self.type
        status+='target=%s\r\n' % self.target
        
        dir_out=None
        if self.target_dir:
            # retrieve info about the target file
            try:
                stat=os.stat(self.target)
            except Exception, e:
                log.error('checking target file: %s', WindowsErrorDecode(e))
                status+='target_stat_error=%s\r\n' % WindowsErrorDecode(e)
            else:
                status+='target_size=%d\r\n' % stat.st_size
                status+='target_mtime_epoch=%d\r\n' % stat.st_mtime
                status+='target_mtime=%s\r\n' % time.ctime(stat.st_mtime)
        
            # retrieve info about the target directory
            try:
                total_free_bytes=free_space(self.target_dir, log)
                dir_out, _total_size=windows_list_dir(self.target_dir, log)        
            except Exception, e:
                log.error('checking target directory: %s', WindowsErrorDecode(e))
                status+='target_directory_error=%s\r\n' % WindowsErrorDecode(e)
            else:
                status+='target_free_space=%d\r\n' % total_free_bytes

        status+='cmdline=%s\r\n' % ' '.join(self.cmd_args)

        attachments=[ # the type, subtype and coding is not used
                       ('log.txt', logfile, None, 'text', 'plain', 'utf-16'),
                       ('evlog.txt', None, ev_out.encode('utf-8'), 'text', 'plain', 'utf-8'),
                    ]

        if dir_out:
            attachments.append(('dir.txt', None, dir_out.encode('utf-8'), 'text', 'plain', 'utf-8'))
        if self.selection.startswith('@'):
            attachments.append(('selection.bks', self.selection[1:], None, 'text', 'plain', 'utf-16'))
        if std_out:
            attachments.append(('stdout.txt', None, std_out, 'text', 'plain', manager.console_encoding))
        if std_err:
            attachments.append(('stderr.txt', None, std_err, 'text', 'plain', manager.console_encoding))

        return ev_status, status, attachments
