#
# mkbackup/install.py
#
# Windows, Linux and ghettoVCB.sh installation 


import os, sys, time, re
import platform, posixpath, subprocess
import urllib2, tarfile, zipfile, tempfile, StringIO, shutil

sample_ini_url='http://www.magikmon.com/download/mksbackup/sample.ini'
ghettovcb_url='http://www.magikmon.com/download/mksbackup/ghettoVCB-mksbackup-last.tar.gz'
readme_txt_url='http://www.magikmon.com/download/mksbackup/README.txt'
#ftpput_url='http://www.magikmon.com/download/mksbackup/ftpput'


# =====================================================================
def raw_input_with_default(msg, prompt, default):

#    try:
#        import pyreadline as readline
#            
#        def pre_input_hook():
#            readline.insert_text(default)
#            readline.redisplay()
#        
#        readline.set_pre_input_hook(pre_input_hook)
#        try:
#            return raw_input(msg+prompt)
#        finally:
#            readline.set_pre_input_hook(None)
#    except ImportError, e:
#        print 'ERROR', e
        if default:
            line="%s [%s]%s" % (msg, default, prompt)
        else:
            line="%s%s" % (msg, prompt)
        value=raw_input(line)
        if value=='' and default:
            return default
        return value

# =====================================================================
def Install():
    """Install"""
    if sys.platform in ('win32', ):
        Windows_Install()
    else:
        Linux_Install()
        
# =====================================================================
def Install_GhettoVCB(mksbackup_target, sources=None):
        print 'Download a well tested version of ghettoVCB.sh at %s' % (ghettovcb_url, )
        print 'The last version can be found at "https://github.com/lamw/ghettoVCB", this'
        print 'version has not been tested with MKSBackup but should probably works.'
        vmware_dir=os.path.join(mksbackup_target, 'vmware')
        try:
            os.mkdir(vmware_dir)
        except Exception:
            pass
        try:
            data=urllib2.urlopen(ghettovcb_url, None).read()
        except (urllib2.URLError, urllib2.HTTPError, Exception), e:
            print 'Download failed'
        else:
            print 'Install ghettoVCB.sh and ghettoVCB.conf in sub directory vmware'
            cwd=os.getcwd()
            tmp_dir=tempfile.mkdtemp()
            try:
                if ghettovcb_url.endswith('.zip'):
                    zipfile.ZipFile(StringIO.StringIO(data, mode='r')).extractall(tmp_dir)
                else:
                    tarfile.open(fileobj=StringIO.StringIO(data), mode='r:gz').extractall(tmp_dir)
            except Exception, e:
                print 'Unexpected error extraction %s (%s)' % (posixpath.basename(ghettovcb_url), e)
            else:
                actions={ 'ghettoVCB.conf':'ghettoVCB.conf.new', 'ghettoVCB.sh':None, 'ghettoVCB-vm_backup_configuration_template':None }
                for root, dirs, files in os.walk(tmp_dir):
                    for filename in files:
                        try:
                            rename=actions[filename]
                        except KeyError:
                            pass
                        else:
                            dst_filename=os.path.join(vmware_dir, filename)
                            src_filename=os.path.join(root, filename)
                            if rename and os.path.isfile(dst_filename):
                                dst_filename=os.path.join(vmware_dir, rename)
                            data=open(src_filename).read() 
                            if filename in ('ghettoVCB.conf','ghettoVCB-vm_backup_configuration_template', 'ghettoVCB-restore_vm_restore_configuration_template', ):
                                # convert text file in windows/linux format
                                if sys.platform in ('win32', ):                                 
                                    data=re.sub('(?<!\r)\n','\r\n', data)
                                else:
                                    data=re.sub('\r\n','\n', data)
                            f=open(dst_filename, 'wb')
                            f.write(data)
                            f.close()

#        print 'Download ftpput a ftp uploader for VMware'
#        try:
#            data=urllib2.urlopen(ftpput_url, None).read()
#        except (urllib2.URLError, urllib2.HTTPError, Exception), e:
#            print 'Download failed (%s)' % (e, )
#        else:
#            dst_filename=os.path.join(vmware_dir, 'ftpput')
#            open(dst_filename, 'w').write(data)
    

# =====================================================================
def Install_ini(source_dir, target_dir):
    if source_dir:
        sample_ini=os.path.join(source_dir, 'sample.ini')
        
    if source_dir and os.path.isfile(sample_ini):
        sample_ini_data=open(sample_ini).read()
    else:
        print 'Retrieve sample.ini file from %s ...' % (sample_ini_url, )
        try:
            sample_ini_data=urllib2.urlopen(sample_ini_url, None).read()
        except (urllib2.URLError, urllib2.HTTPError, Exception), e:
            sample_ini_data='# mksbackup.ini more on http://www.magikmon.com/mksbackup\n# sample .ini file at %s\n' % (sample_ini_url, )
            pass

    if sys.platform in ('win32', ):
        # convert text file in windows format 
        sample_ini_data=re.sub('(?<!\r)\n','\r\n', sample_ini_data)
    
    mksbackup_ini=os.path.join(target_dir, 'mksbackup.ini')
    if os.path.isfile(mksbackup_ini):
        print 'Config file already exists: %s' % (mksbackup_ini, )
    else:
        print 'Create sample config file: %s' % (mksbackup_ini, )
        open(mksbackup_ini, 'wb').write(sample_ini_data)
        
    return mksbackup_ini

# =====================================================================
def Linux_Install():
    """create directories in /etc and download ghettoVCB"""

    mksbackup_target='/etc/mksbackup'
    choice=raw_input_with_default('Do you want to setup config files in %s ? (y/n)' % (mksbackup_target, ), '>', 'y')
    if choice!='y':
        print 'bye'
        return 0
        
    if not os.path.isdir(mksbackup_target):
        os.makedirs(mksbackup_target)
    
    Install_ini(None, mksbackup_target)
       
    if os.path.isdir('/etc/cron.d'):
        if not os.path.isfile('/etc/cron.d/mksbackup'):
            mksbackup_starter='"%s" "%s"' % (sys.executable, os.path.abspath(sys.argv[0]))
            cron_file=open('/etc/cron.d/mksbackup', 'w')
            print >>cron_file, '# MKSBACKUP cron file http://www.magikmon.com/mksbackup'
            print >>cron_file, '# un-comment and edit line bellow'
            print >>cron_file, '# 45 22 * * * root %s -c /etc/mksbackup/mksbackup.ini backup BACKUP_JOB' % mksbackup_starter
            cron_file.close()
        else:
            print 'file already exists: /etc/cron.d/mksbackup'

    choice=raw_input_with_default('Do you want to download and install ghettoVCB ?', '>', 'y')
    if choice=='y':
        Install_GhettoVCB(mksbackup_target)

    print 'More at http://www.magikmon.com/mksbackup\n' 
    print 'Edit and modify files: /etc/mksbackup/mksbackup.ini and /etc/cron.d/mksbackup'


# =====================================================================
def Windows_Install():
    """Install the exe, setup a default .ini and create task in scheduler"""

    choice=raw_input_with_default('Do you want to install MKSBackup ? (y/n)', '>', 'y')
    if choice!='y':
        print 'bye'
        return 0
        
    target=raw_input_with_default('Installation directory ', '>', 'C:\Magik')
    mksbackup_target=os.path.join(target, 'MKSBackup')
    if os.path.isdir(mksbackup_target):
        print 'Directory %s already exists, continue.' % (mksbackup_target,)
    else:
        try:
            os.makedirs(mksbackup_target)
        except Exception, e:
            print 'Error creating directory %s (%s)', (mksbackup_target, e)
        else:
            print 'Directory created'

    import shutil
    
    source=os.path.dirname(sys.argv[0])
    # copy .exe
    if sys.argv[0][-4:].lower()=='.exe':
        if os.path.realpath(sys.argv[0])==os.path.realpath(mksbackup_target):
            """.exe already in place"""
        else:
            print 'Copy %s' % (os.path.basename(sys.argv[0]))
            shutil.copy(sys.argv[0], mksbackup_target)

    # copy and rename sample.ini
    doc_src=os.path.join(source, 'doc')
    mksbackup_ini=Install_ini(doc_src, target)
        
    # copy doc
    if os.path.isdir(doc_src):
        doc_dst=os.path.join(mksbackup_target, 'doc')
        try:
            os.mkdir(doc_dst)
        except Exception:
            pass
        try:
            for filename in os.listdir(doc_src):
                shutil.copy(os.path.join(doc_src, filename), doc_dst)
        except Exception, e:
            print 'Error copying documentation, continue'
        else:
            print 'Copy documentation'
    else:
        # try to get Readme
        print 'Documentation not found, try to retrieve Readme.txt'
        print 'from %s ...' % (readme_txt_url, )
        try:
            readme_txt_data=urllib2.urlopen(readme_txt_url, None).read()
        except (urllib2.URLError, urllib2.HTTPError, Exception), e:
            readme_txt_data='more on http://www.magikmon.com/mksbackup\n'
        open(os.path.join(mksbackup_target, 'Readme.txt'), 'w').write(readme_txt_data)

    # install ghettoVCB and other VMware tools
    ghettovcb_choice=raw_input_with_default('Do you want to download and install ghettoVCB ?', '>', 'y')
    if ghettovcb_choice=='y':
        Install_GhettoVCB(target)
        
    # create task in scheduler if not already exists
    stdout, stderr=subprocess.Popen('SCHTASKS /Query', stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if stdout.find('MKSBackup')==-1:
        print 'create task MKSBackup in scheduler'
        jobs=raw_input_with_default('Enter your job names separated by spaces', '>', 'BACKUP_JOB')
        cmd='"%s" -q -l "%s" -c "%s" backup %s' % (os.path.join(mksbackup_target, os.path.basename(sys.argv[0])), os.path.join(target, 'mksbackup.log'), os.path.join(target, 'mksbackup.ini'), jobs) 
        schtasks_cmd=[ 'SCHTASKS', '/Create', '/SC', 'DAILY', '/TN', 'MKSBackup', '/ST', '22:45:00', '/RU', os.getenv('USERNAME'),  '/TR', cmd ]
        if sys.getwindowsversion()[0]>5:
            # under 2008 backup require HIGHEST privilege
            schtasks_cmd.insert(2, 'HIGHEST')
            schtasks_cmd.insert(2, '/RL')
            # under 2008, to force the system to ask for the password, set empty password 
            i=schtasks_cmd.index('/RU')+2
            schtasks_cmd.insert(i, '')
            schtasks_cmd.insert(i, '/RP')
        else:
            pass
            
        # print ' '.join(schtasks_cmd)
        process=subprocess.Popen(schtasks_cmd)
        _code=process.wait()
    else:
        print 'task MKSBackup already exists, skip'

    print 'Open task scheduler'
    subprocess.Popen([ 'control.exe',  'schedtasks', ])  # taskschd.msc works under 2008 not on XP
    print 'Open config file in notepad'    
    subprocess.Popen([ 'notepad', mksbackup_ini] )
    if ghettovcb_choice=='yes':
        print 'Open ghettoVCB.conf file in notepad', os.path.join(target, 'vmware\ghettoVCB.conf')    
        subprocess.Popen([ 'notepad', os.path.join(target, 'vmware\ghettoVCB.conf') ] )
        
    print 'Update or review your configuration and task'
    print 'More at http://www.magikmon.com/mksbackup' 
    raw_input('Install completed, press ENTER to quit')

    return 0