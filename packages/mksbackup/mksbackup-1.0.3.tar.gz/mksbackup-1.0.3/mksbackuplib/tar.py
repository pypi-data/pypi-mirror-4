#
# ghettovcb.py
#
# mkbackup ghettovcb frontent
#

import os, string, subprocess, fnmatch, platform
import shutil
from datetime import datetime, timedelta

from archiver import *
import cron


class Tar(Archiver):
    
    name='tar'
    exe='tar'

    types=dict(normal='normal', full='normal', incremental='incremental', inc='incremental', differential='differential', diff='differential', copy='copy', daily='daily')

    def __init__(self):
        Archiver.__init__(self)
        
        self.include=[]
        self.exclude_dir=[]
        self.exclude=[]
        self.find_bin=None
        self.tar_bin=None
        self.snapshot=None
        self.destination=None
        self.index='auto'
        self.index_file=None
        self.error='auto'
        self.error_file=None
        self.error_find='auto'
        self.error_find_file=None
        
        self.tar_options=[]
        self.find_options=[]
        self.gzip_options=[]
        self.bzip2_options=[]
        
        self.find_args=[]
        self.tar_args=[]
        self.tar_env=None
        
        self.target=None
        self.type=None
        self.target_dir=None

    
    def load(self, job, manager):

        log=manager.log
        now=manager.now

        errors, warnings, extra={}, {}, ''

        #
        # check job config
        #

        self.include=job.get('include', [])
        if not self.include:
            errors['include']='option mandatory'
        else:
            self.include=map(string.strip, self.include.split('\n'))
            for path in self.include:
                if not os.path.isdir(path) and not os.path.isfile(path):
                    warnings['include']='file or directory not found'

        self.exclude_dir=job.get('exclude_dir', [])
        if self.exclude_dir:
            self.exclude_dir=map(string.strip, self.exclude_dir.split('\n'))
            for path in self.exclude_dir:
                if not os.path.isdir(path):
                    warnings['exclude_dir']='directory not found'

        self.exclude=job.get('exclude', [])
        if self.exclude:
            self.exclude=map(string.strip, self.exclude.split('\n'))
                    
        self.find_bin=job.get('find', None)
        if self.find_bin:
            if not os.path.isfile(self.find_bin):
                errors['find']='file not found'
            elif not os.access(self.find_bin, os.X_OK):
                errors['find']='file cannot be executed'

        self.tar_bin=job.get('tar', None)
        if self.tar_bin:
            if not os.path.isfile(self.tar_bin):
                errors['tar']='file not found'
            elif not os.access(self.tar_bin, os.X_OK):
                errors['tar']='file cannot be executed'

        self.snapshot=job.get('snapshot', None)
        if self.snapshot:
            if not os.path.isdir(os.path.dirname(self.snapshot)):
                try:
                    os.makedir(os.path.dirname(self.snapshot))
                except:
                    errors['snapshot']='directory not found: '+os.path.dirname(self.snapshot)

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
                if ('differential' in self.destination.used_types or 'incremental' in self.destination.used_types) and not self.snapshot:
                    errors['destination']='parameter "snapshot" required to do differential or incremental backups'
                     
                if self.type!=None and self.type!='none':
                    self.target_dir=os.path.dirname(self.target)
                    if not os.path.isdir(self.target_dir):
                        try:
                            os.makedirs(self.target_dir)
                        except OSError, e:
                            errors['destination']='directory not found: %s (%s)' % (self.target_dir, e)

        for attr in ('index', 'error', 'error_find'):
            filename=job.get(attr, 'auto')
            setattr(self, attr, filename)
            if not filename in ('auto', 'no'):
                head, tail=os.path.split(filename)
                if not os.path.isfile(filename) or not os.access(filename, os.W_OK):
                    if not os.path.isdir(head):
                        errors[attr]='directory not found'
                    elif not os.access(head, os.W_OK):
                        errors[attr]='directory not writable'
                    
        if not errors:
            for name in ('tar_options', 'find_options', 'gzip_options', 'bzip2_options'):
                option=job.get(name, None)
                if not option:
                    continue
                try:
                    options=quoted_string_list(option)
                except ValueError:
                    errors[name]='not a valid quoted string list'
                else:
                    setattr(self, name, options)

            if self.type!=None and self.type!='none':

                # find_args
                self.find_args=[ 'find' ] + self.include
                for path in self.exclude_dir:
                    self.find_args+=[ "-path" , path, "-prune", "-o" ]
                self.find_args+=[ "-not", "-type", "s" ] # exclude socket
                self.find_args+=self.find_options
                self.find_args.append("-print")
        
                if not self.find_bin:
                    for self.find_bin in [ '/usr/local/bin/find', '/bin/find', '/usr/bin/find', 'find' ]:
                        if os.access(self.find_bin, os.X_OK):
                            break
        
                extra+='find_cmdline=%s\n' % '  '.join(self.find_args)
                extra+='find_bin=%s\n' % self.find_bin
                
                # tar_args
                self.tar_args=[ 'tar', 'cvTf', '-', self.target, '--no-recursion' ] + self.tar_options
                if self.snapshot:
                    if self.type=='normal':
                        self.tar_args.append('--listed-incremental='+self.snapshot)
                    elif self.type in ('differential', 'incremental'):
                        self.tar_args.append('--listed-incremental='+self.snapshot+'-1')
        
                self.tar_env=None
                if self.gzip_options:
                    self.tar_env=os.environ
                    self.tar_env['GZIP']=' '.join(self.gzip_options)
                if self.bzip2_options:
                    if not self.tar_env:
                        self.tar_env=os.environ
                    self.tar_env['BZIP2']=' '.join(self.bzip2_options)
        
                if not self.tar_bin:
                    for self.tar_bin in [ '/usr/local/bin/tar', '/bin/tar', '/usr/bin/tar', 'tar' ]:
                        if os.access(self.tar_bin, os.X_OK):
                            break
        
                extra+='tar_cmdline=%s\n' % '  '.join(self.tar_args)
                extra+='tar_bin=%s\n' % self.tar_bin
        
        return errors, warnings, extra
    
    def run(self, command, job, manager):

        log=manager.log
        now=manager.now

        target_noext=self.target
        for ext in ('.tar', '.tar.gz', '.tgz', '.tbz2', '.tbz'):
            if target_noext.endswith(ext):
                target_noext=target_noext[:-len(ext)]
                break
            
        if self.index=='auto':
            self.index_file=target_noext+'.idx'
        elif self.index=='no':
            self.index_file='/dev/null'
        else:
            self.index_file=self.index

        if self.error=='auto':
            self.error_file=target_noext+'.err'
        elif self.error=='no':
            self.error_file='/dev/null'
        else:
            self.error_file=self.error

        if self.error_find=='auto':
            self.error_find_file=target_noext+'_find.err'
        elif self.error_find=='no':
            self.error_find_file='/dev/null'
        else:
            self.error_find_file=self.error_find

        if self.snapshot:
            if self.type=='normal':
                try:
                    os.unlink(self.snapshot)
                except:
                    pass
                try:
                    os.unlink(self.snapshot+'-1')
                except:
                    pass
            elif self.type=='differential':
                if os.path.isfile(self.snapshot):
                    shutil.copyfile(self.snapshot, self.snapshot+'-1')
            elif self.type=='incremental':
                if not os.path.isfile(self.snapshot+'-1'):
                    if os.path.isfile(self.snapshot):
                        shutil.copyfile(self.snapshot, self.snapshot+'-1')
        
        start=int(time.time())
        p_find = subprocess.Popen(self.find_args, executable=self.find_bin, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=os.open(self.error_find_file, os.O_WRONLY|os.O_CREAT|os.O_TRUNC))
        p_tar = subprocess.Popen(self.tar_args, executable=self.tar_bin, env=self.tar_env, stdin=subprocess.PIPE, stdout=os.open(self.index_file, os.O_WRONLY|os.O_CREAT|os.O_TRUNC), stderr=os.open(self.error_file, os.O_WRONLY|os.O_CREAT|os.O_TRUNC))

        p_find.stdin.close()
        file_count, file_excluded=0, 0
        #output = p_tar.communicate()[0]
        for line in p_find.stdout:
            filename=line.rstrip('\n')
            match=0
            for pattern in self.exclude:
                match=fnmatch.fnmatchcase(filename, pattern)
                if match:
                    file_excluded+=1
                    log.debug('exclude file: %s', filename)
                    break
            if not match:
                p_tar.stdin.write(line)
                file_count+=1
                
        p_tar.stdin.close()   
        
        p_find.wait()
        # print 'returncode find=%r' % (p_find.returncode, )

        p_tar.wait()
        
        end=int(time.time())

        # print 'returncode find=%r, tar=%r' % (p_find.returncode, p_tar.returncode)
        
        if p_find.returncode!=0:
            backup_status='ERR'
        else:
            if p_tar.returncode==0:
                backup_status='OK'
            elif p_tar.returncode==1:
                backup_status='WAR'
            else:
                backup_status='ERR'

        status=u''
        status+='name=%s\r\n' % job['name']
        status+='program=%s\r\n' % self.name
        status+='version=%s\r\n' % self.__version__
        status+='hostname=%s\r\n' % platform.node()

        status+='status=%s\r\n' % backup_status
        
        status+='tar_exit_code=%r\r\n' % p_tar.returncode
        status+='find_exit_code=%r\r\n' % p_find.returncode
        status+='start=%s\r\n' % time.ctime(start)
        status+='end=%s\r\n' % time.ctime(end)
        
        status+='file_count=%d\r\n' % file_count
        status+='file_excluded=%d\r\n' % file_excluded
        
        #
        # target file and directory
        #
        target_dir_list, _total_size=list_dir(self.target_dir, log)

        status+='target=%s\r\n' % self.target
        try:
            stat=os.stat(self.target)
        except Exception, e:
            log.error('checking target file: %s', e)
            status+='target_stat_err=%s\r\n' % e
        else:
            status+='target_size=%d\r\n' % stat.st_size
            status+='target_mtime_epoch=%d\r\n' % stat.st_mtime
            status+='target_mtime=%s\r\n' % time.ctime(stat.st_mtime)
        
        try:
            total_free_bytes=free_space(self.target_dir, log)
        except Exception, e:
            log.error('checking target directory: %s', e)
            status+='target_free_space=%s\r\n' % e
        else:
            status+='target_free_space=%d\r\n' % total_free_bytes
        
        status+='start_epoch=%d\r\n' % start
        status+='end_epoch=%d\r\n' % end
        status+='cmd_tar=%s\r\n' % ' '.join(self.tar_args)
        status+='cmd_find=%s\r\n' % ' '.join(self.find_args)

        attachments=[ # the type, subtype and coding is not used
                       ('dir.txt', None, target_dir_list.encode('utf-8'), 'text', 'plain', 'utf-8'),
                    ]

        if self.error!='no':
            attachments.append(('err.txt', self.error_file, None, 'text', 'plain', 'utf-8'))
            
        if self.error_find!='no':
            attachments.append(('err_find.txt', self.error_find_file, None, 'text', 'plain', 'utf-8'))


        return backup_status, status, attachments

