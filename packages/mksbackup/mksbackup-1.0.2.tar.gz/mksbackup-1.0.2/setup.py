# /bin/env python
# setup.py
# (c) alain.spineux@gmail.com

import sys, os

if 'bdist_egg' in sys.argv and 'py2exe' in sys.argv :
    # both "patch" distutil and py2exe cannot be mix together 
    print "don't mix bdist_egg and py2exe in the same command !"
    sys.exit(1)

if 'bdist_egg' in sys.argv:
    from setuptools import setup
else:
    from distutils.core import setup

if 'py2exe' in sys.argv:
    # ... http://www.py2exe.org/index.cgi/win32com.shellhttp://www.py2exe.org/index.cgi/win32com.shell
    # ModuleFinder can't handle runtime changes to __path__, but win32com uses them

    # py2exe 0.6.4 introduced a replacement modulefinder.
    # This means we have to add package paths there, not to the built-in
    # one.  If this new modulefinder gets integrated into Python, then
    # we might be able to revert this some day.
    # if this doesn't work, try import modulefinder
    try:
        import py2exe.mf as modulefinder
    except ImportError:
        import modulefinder
    import win32com
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell"]: #,"win32com.mapi"
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)

    from py2exe.build_exe import py2exe

    class build_zip(py2exe):
        """This class inherit from py2exe, builds the exe file(s), then creates a ZIP file."""
        def run(self):
            
            import zipfile
            # initialize variables and create appropriate directories in 'buid' directory
            # please don't change 'dist_dir' in setup()
             
            orig_dist_dir=self.dist_dir
            self.mkpath(orig_dist_dir)
            zip_filename=os.path.join(orig_dist_dir, '%s-%s-win32.zip' % (self.distribution.metadata.name, self.distribution.metadata.version,))
            bdist_base=self.get_finalized_command('bdist').bdist_base
            dist_dir=os.path.join(bdist_base, '%s-%s' % (self.distribution.metadata.name, self.distribution.metadata.version, ))
            self.dist_dir=dist_dir
            print 'dist_dir is %s' % (dist_dir, )

            # let py2exe do it's work.
            py2exe.run(self)
            
            # remove zipfile if exists
            if os.path.exists(zip_filename):
                os.unlink(zip_filename)
            
            # create the zipfile
            print 'Building zip file %s' % (zip_filename, )
            zfile=zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED)
            for root, dirs, files in os.walk(dist_dir):
                for f in files:
                    filename=os.path.join(root, f)
                    zfile.write(filename, os.path.relpath(filename, bdist_base))
                    
#            zfile.writestr('EGG-INFO/PKG-INFO', 'This file is required by PyPI to allow upload as and bdist_egg archive')
            zfile.close()
            # pip and easy_install try to use the win32 .zip archive as a source file
            # whatever it's type is and faile ! This file cannot be uploaded on PyPI
            # self.distribution.dist_files.append(('bdist_dumb', '2.3', zip_filename))


basename='mksbackup'
from mksbackuplib.version import __version__ as version
print 'VERSION', version

extra_options = {}
doc_dir='share/doc/%s-%s' % (basename, version)

cmdclass = {}

if 'py2exe' in sys.argv and os.name=='nt':
    doc_dir='doc'
    cmdclass = {"py2exe": build_zip}
    win32zip='%s-%s' % (basename, version)
    py2exe_options =  { # 'ascii': True, # exclude encodings
                        'packages':['email', 'new'], 
                        'dll_excludes': ['w9xpopen.exe'], # no support for W98 
                        'compressed':True, 
                        # 'dist_dir': ????  # !!! DONT CHANGE distdir HERE 
                        # exclude big and unused python packages from the binary
                        'excludes': [ 'difflib', 'doctest', 'pdb'],
                        }
    extra_options = { 'console': ['mksbackup', ],  # list of scripts to convert into console exes
                      'windows': [],          # list of scripts to convert into gui exes
                      'options': { 'py2exe': py2exe_options, } ,
                    }
    if '--single-file' in sys.argv[1:]:
        sys.argv.remove('--single-file')
        py2exe_options.update({ 'bundle_files': 1, })
        extra_options.update({ 'zipfile': None, }) # don't build a separate zip file with all libraries, put them all in the .exe  

data_files=[ (doc_dir, [ 'README.txt', 'Changelog.txt', 'LICENSE.txt', 'ghettoVCB.txt', 'sample.ini' ]),
#             ('', ['__main__.py', ]),
           ]

# if 'bdist_egg' in sys.argv:
#     data_files.append(('', ['__main__.py', ]))

setup(name='mksbackup',
      version=version, 
      author='Alain Spineux',
      author_email='alain.spineux@gmail.com',
      url='http://www.magikmon.com/mksbackup',
      description='Front-end for popular Windows, Linux and VMware backup tools. Sending a mail report at end of backup.',
      long_description='MKSBackup can run Windows ntbackup, wbadmin or Linux tar or even VMWare ESX(i) '
                       'ghettoVCB.sh using settings found in a .ini file. When done MKSBackup can '
                       'send emails including a full report. The email subject display an unambiguous '
                       'status "ERR" or "OK" to allow easy filtering in any mail reader. '
                       'MKSBackup handle custom target destination directory and filename naming based '
                       'on date and time. '
                       'MKSBackup can also monitor VMWare ESX(i) hardware via included esxmon module. '
                       'Backup reports can also be sent to MagiKmon http://www.magikmon.com to '
                       'be parsed and compiled into more synthetic reports and graphs. MagiKmon can '
                       'generate alerts when backups fails for too long. '
                       'MKSBackup is the new name for old MKBackup.'
                       'A .exe for windows and a runnable .egg that don''t need installation are '
                       'available from the site at http://www.magikmon.com/mksbackup'
                       ,
      license='GPL',
      py_modules = [ '__main__', ],
      packages=[ 'mksbackuplib', 'mksbackuplib.pywbem'],
      scripts=['mksbackup',],

      data_files=data_files,

      classifiers=["Development Status :: 5 - Production/Stable",
                  "Environment :: Console",
                  "License :: OSI Approved :: GNU General Public License (GPL)",
                  "Topic :: System :: Archiving :: Backup",
                  "Operating System :: OS Independent",
                  ],

      cmdclass = cmdclass,

      **extra_options)


