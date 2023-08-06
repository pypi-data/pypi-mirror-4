#!/usr/bin/env python
#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#

import site
import sys
from os import environ, pathsep
from os.path import join, abspath, dirname, split, \
     exists as path_exists, sep as path_sep
from inspect import getfile, currentframe

class Config(object):
    # Indicator if the localized site-packages directory was configured by
    # this Python process.
    just_installed = False
    # output stream
    OUT = sys.stdout
    
    # useful output string
    stars = "\n"+"*"*72+"\n"
    
    ### General path settings
    # base directory for the installation
    baseDir = None    
    # site-packages location (nominally, base/lib/pythonX.Y/site-packages)
    targetDir = None
    # directory to install raw scripts (nominally base/bin)
    scriptDir = None
    # directory holding the python packages to install (i.e., src and dist)
    srcDir = None
    
    @staticmethod
    def setup_paths(base, target=None, script=None, src=None):
        if target is None:
            target = join( base, 'lib', 'python%i.%i' % sys.version_info[:2],
                           'site-packages' )
        if script is None:
            script = join( base, 'bin' )
        if src is None:
            src    = join( base, 'dist', 'python' )
        Config.baseDir = base
        Config.targetDir = target
        Config.scriptDir = script
        Config.srcDir = src
    

def Write(*args):
    Config.OUT.flush()
    Config.OUT.write(*args)
    Config.OUT.flush()
    
def Log(*args):
    Write(*args)
    if Config.OUT is not sys.stdout:
        sys.stdout.write(".")
        sys.stdout.flush()

setup_override = """
AUTODIST_SETUP_DATA={}
def setup(*args, **kwargs):
  global AUTODIST_SETUP_DATA
  AUTODIST_SETUP_DATA.update(kwargs)
  AUTODIST_SETUP_DATA['*args'] = args

"""
setup_reporter = """
import pickle
import sys
for key in list(AUTODIST_SETUP_DATA.keys()):
    if 'require' not in key:
        del AUTODIST_SETUP_DATA[key]
sys.stdout.write( "START_AUTODIST_SETUP" +
                  pickle.dumps(AUTODIST_SETUP_DATA) +
                  "END_AUTODIST_SETUP" )
"""
nsis_package = """
Section "%(name)s"
;  %(rsection)s
  DetailPrint ""
  DetailPrint "--------------------------------------------------------------"
  DetailPrint "Package: Python %(name)s"
  DetailPrint "--------------------------------------------------------------"
  DetailPrint ""
  StrCpy $9 $PythonExecutable -11
install:
  DetailPrint "Installing %(name)s"
  SetOutPath \"$INSTDIR\\%(tpl)s\\%(name)s\"
  nsExec::ExecToLog '\"$PythonExecutable\" \"$INSTDIR\\%(tpl)s\\%(name)s\\setup.py\" %(mode)s' $0
done:
  SetOutPath \"$INSTDIR\"
  DetailPrint "Package %(name)s complete."
  DetailPrint ""
SectionEnd
"""
unins_package = """
Section "un.%(name)s"
  DetailPrint "--------------------------------------------------------------"
  DetailPrint "Removing %(name)s Package"
  DetailPrint "--------------------------------------------------------------"
  nsExec::ExecToLog 'pip uninstall %(name)s -y' $0
SectionEnd
"""
nsis_data_head = """
/*
 * data.nsh
 *
 * The Coopr data section.
 */

Section "" SEC02

  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
"""
nsis_data_tail = """

SectionEnd

"""
nsis_uninst_head = """
/*
 * uninstall.nsh
 *
 * The uninstallation section.
 */

Function UninstallPrevious
  ;
  ; Get the installer from the registry
  ;
  ReadRegStr $2 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString"
  ;
  ; Skip execution if this isn't installed
  ;
  StrCmp "$2" "" done
  IfFileExists "$2" 0 done
  ;
  ; Execute installer silently
  ;
  ; This is a bit of a hack.  To ensure that the top-level installer waits,
  ; we use the _? option.  But this prevents the uninstaller from deleting
  ; itself.  Hence, we check to see if the uninstaller is exists, and if so
  ; we explicitly delete it.  {SIGH}
  ;
  ClearErrors
  ExecWait '"$2" /S _?=$INSTDIR' $0
  IfErrors 0 +3
     MessageBox MB_OK "Failed to uninstall ${PRODUCT_NAME}" IDOK 0
     Abort
  ;Abort
  IfFileExists $2 0 done
    Delete $2
    RMDir $INSTDIR
done:
FunctionEnd



"""
nsis_uninst_tail = """
Section "Uninstall"
  ; Remove from path
  ;;Push $INSTDIR\bin
  ;;Call un.RemoveFromPath
  ;;${un.EnvVarUpdate} $0 "PATH" "R" "HKLM" "$INSTDIR\\bin"
  ; Is this a good idea?
  RMDIR /r "$INSTDIR"

  IfFileExists "$INSTDIR" 0 NoErrorMsg
    IfSilent NoErrorMsg 0
       MessageBox MB_OK "Note: $INSTDIR could not be removed!" IDOK 0 ; skipped if file doesn't exist
       Abort
    
  NoErrorMsg:

  SetShellVarContext all
  ;Delete "$SMPROGRAMS\\${PRODUCT_NAME}\\Uninstall.lnk"
  Delete "$SMPROGRAMS\\${PRODUCT_NAME}\\*.*"
  RMDir "$SMPROGRAMS\\${PRODUCT_NAME}"

  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\\${PRODUCT_NAME}"
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"

  SetAutoClose false
SectionEnd

"""


def install_setuptools():
    # Set up the setuptools (if needed)
    try:
        from setuptools import setup
    except ImportError:
        from subprocess import Popen, PIPE
        
        Write(Config.stars+"Installing setuptools"+Config.stars)
        # We cannot install setuptools from within this interpreter
        # because this would result in importing setuptools from the
        # install source (and not the final installation directory)
        CMD = "import sys; sys.path.insert(0, '%s'); "\
              "from setuptools.command.easy_install import bootstrap; "\
              "sys.argv=sys.argv[:1]+['--install-dir=%s','--script-dir=%s']; "\
              "sys.exit(bootstrap())" % \
              ( abspath(join( Config.srcDir,'dist','setuptools'
                              )).replace('\\','\\\\'), 
                Config.targetDir.replace('\\','\\\\'),
                Config.scriptDir.replace('\\','\\\\') )
        Write("Command: %s\n" % CMD)
        proc = Popen( [sys.executable, "-c", CMD],
                      stdout=Config.OUT, stderr=Config.OUT )
        ANS = proc.communicate()
        if ANS[1]:
            Write(ANS[1])
        Config.OUT.flush()
        if proc.returncode:
            raise Exception("ERROR installing setuptools")



def configure_packages():
    import os
    import re
    import pickle
    from subprocess import Popen, PIPE

    def interrogate_dependencies(package):
        setup_re = re.compile('setup\\(')
        CMD=open(os.path.join(package,'setup.py'),'r').readlines()
        i = 0;
        while i < len(CMD):
            if setup_re.search(CMD[i]):
                break
            i += 1
        if i == len(CMD):
            return ""
        if CMD[i].lstrip() != CMD[i]:
            while i > 0 and not CMD[i][0].strip():
                i -= 1
        CMD.insert(i, setup_override)
        tmp = join(package,'setup_autodist.py')
        FILE = open(tmp, 'w')
        FILE.write("".join(CMD))
        FILE.write(setup_reporter)
        FILE.close()
        proc = Popen( [ sys.executable, tmp ],
                      stdout=PIPE, stderr=PIPE, cwd=package )
        ANS = proc.communicate()
        if ANS[1]:
            Write(ANS[1])
        Config.OUT.flush()
        os.remove(tmp)
        if proc.returncode:
            raise Exception("ERROR interrogating %s" % (p,))
        if ANS[0]:
            pickleStr = ANS[0] \
                        .split('START_AUTODIST_SETUP',1)[-1] \
                        .split('END_AUTODIST_SETUP')[0] \
                        .replace('\r\n','\n')
            return pickle.loads(pickleStr)
        else:
            return {}
    def sort_packages(pkg, unsorted, sorted, all_deps, base2pkg):
        prereqs = all_deps.get(os.path.basename(pkg), [])
        for prereq in prereqs:
            prereq = prereq.split('>',1)[0].split('=',1)[0].split('<',1)[0]
            p_pkg = base2pkg.get(prereq.lower(), None)
            if p_pkg and p_pkg in unsorted:
                unsorted.remove(p_pkg)
                sort_packages(p_pkg, unsorted, sorted, all_deps, base2pkg)
        sorted.append(pkg)

    Write(Config.stars+"Interrogating package dependencies"+Config.stars)

    packages = [
        join(Config.srcDir,'dist',x)
        for x in sorted(os.listdir(join(Config.srcDir,'dist')))
        if x != 'setuptools' ]
    tpls = set(packages)
    packages.extend(
        join(Config.srcDir,'src',x)
        for x in sorted(os.listdir(join(Config.srcDir,'src'))) )
    
    deps={}
    base2pkg = {}
    for p in packages:
        Write("Interrogating %s\n" % p)
        if not os.path.isdir(p):
            continue
        _deps = interrogate_dependencies(p)
        deps[os.path.basename(p)] = _deps.get('install_requires',[])
        base2pkg[os.path.basename(p).lower()] = p
    pkg_order = []
    while packages:
        sort_packages(packages.pop(0), packages, pkg_order, deps, base2pkg)
    packages = pkg_order
    return packages, tpls


def install_packages(verbose=True):
    import os
    from subprocess import Popen, PIPE

    if not verbose:
        sys.stdout.write("Configuring Python packages for first use")
        Config.OUT = open(join(Config.baseDir, 'dist', 'autodist.log'), 'w')

    libs    = ['--install-lib=%s' % (Config.targetDir,),
               '--install-purelib=%s' % (Config.targetDir,),
               '--install-platlib=%s' % (Config.targetDir,),
               '--install-data=%s' % (Config.targetDir,),
               ]
    scripts = ['--install-scripts=%s' % (Config.scriptDir,)]

    if not path_exists(Config.targetDir):
        os.makedirs(Config.targetDir)

    if 'PYTHONPATH' in os.environ.keys():
        Write("PYTHONPATH = '%s'\n" % (os.environ['PYTHONPATH'],))
    else:
        Write("PYTHONPATH = (undefined)\n")

    # Set up the setuptools (if needed)
    install_setuptools()

    # Determine the package installation order
    packages, tpls = configure_packages()
    Write("\nPackage install sequence:\n\t"+"\n\t".join(packages))

    # Install all packages
    Write(Config.stars+"Installing all packages"+Config.stars)
    for package in packages:
        setupFile = join(Config.srcDir, package, 'setup.py')
        Log("\n(INFO) installing %s\n" % (package,))
        if not os.stat(setupFile):
            Write("WARNING: %s not found.  Cannot install the package\n"
                  % (setupFile,) )
            continue
        CMD = [sys.executable, setupFile, 'install'] + libs + scripts
        Write("Command: %s\n" % CMD)
        proc = Popen( CMD, stdout=Config.OUT, stderr=Config.OUT,
                      cwd=join(Config.srcDir,package) )
        proc.communicate()
        Config.OUT.flush()
        if proc.returncode:
            raise Exception("ERROR: %s did not install correctly\n"
                            % (package,))

    # localize all scripts
    Write(Config.stars+"Localizing all package scripts"+Config.stars)
    for script in os.listdir(Config.scriptDir):
        if script.endswith('.pyc'):
            continue
        if script.startswith('_'):
            continue
        if script.endswith('-script.py'):
            continue
        if script.endswith('.exe'):
            continue
        if script.endswith('.py'):
            base = script[:3]
        else:
            base = script
        absName = join(Config.scriptDir,base)
        if not path_exists(absName+'-script.py'):
            Write("(INFO) Localizing %s -> %s-script.py\n" % (script,base))
            os.rename(join(Config.scriptDir,script), absName+'-script.py')
    open(join(Config.scriptDir,'__init__.py'), "w").close()

    Config.just_installed = True

    if not verbose:
        sys.stdout.write("\n")
        sys.stdout.flush()
        Config.OUT.close()
        Config.OUT = sys.stdout



def write_nsis_codes(nsis_dir, src_dir, verbose=True):
    """ Command inside autodist to create NSIS installation code for
    each package and dependency rather than to actually install them on
    the system.  """
    
    import os
    from subprocess import Popen, PIPE

    Config.setup_paths(base=os.getcwd(), src=src_dir)

    if not verbose:
        sys.stdout.write("Generating NSIS installer script fragments")
        Config.OUT = open(join(Config.baseDir, 'autodist.log'), 'w')

    if not path_exists(nsis_dir):
        os.makedirs(nsis_dir)

    if 'PYTHONPATH' in os.environ.keys():
        Write("PYTHONPATH = '%s'\n" % (os.environ['PYTHONPATH'],))
    else:
        Write("PYTHONPATH = (undefined)\n")

    # Set up the setuptools (if needed)
    install_setuptools()

    # This doesn't really belong here, but needs to go somewhere
    for d in ('dist','src'):
        for x in os.listdir(join(Config.srcDir,d)):
            if not os.path.isdir(join(Config.srcDir,d,x)):
                os.unlink(join(Config.srcDir,d,x))
    
    packages, tpls = configure_packages()
    # setuptools *must* be first
    packages.insert(0, join(Config.srcDir,'dist','setuptools'))

    Write("\nPackage install sequence:\n\t"+"\n\t".join(packages))

    # Install all packages
    Write(Config.stars+"Writing NSIS code"+Config.stars)

    UNINST = open(join(nsis_dir, 'uninstall.nsh'),'w')
    PKGFILE = open(join(nsis_dir, 'dyn_packages.nsh'),'w')
    DATAFILE = open(join(nsis_dir, 'dyn_data.nsh'),'w')

    DATAFILE.write(nsis_data_head)
    for package in packages:
        p,n = os.path.split(package)
        location = os.path.basename(p)
        inscode = nsis_package % {
            'name':     n,
            'rsection': {'dist':'','src':'InSection RO'}[location],
            'tpl':      location,
            'mode':     {'dist':'install','src':'develop'}[location],
            }
        PKGFILE.write(inscode)
    
    # NB: We need to uninstall packages in the reverse order!
    UNINST.write(nsis_uninst_head)
    for package in reversed(packages):
        p,n = os.path.split(package)
        if package in tpls:
            uninscode = ''
        else:
            uninscode = unins_package%{'name': n}
        UNINST.write(uninscode)
    

    # pack up all the source code
    DATAFILE.write('  File /r %s\n'%join(Config.srcDir,'*.*'))

    UNINST.write(nsis_uninst_tail)
    DATAFILE.write(nsis_data_tail)
    UNINST.close()
    PKGFILE.close()
    DATAFILE.close()
    

def run_script(name):
    # Unfortunately, try as I might, the auto-install process messes
    # with the Python environment *just enough* that key applications
    # (mostly those that rely on component / plugin systems) fail to run
    # properly.  As a workaround, we will just re-run the original
    # script that got us here.
    if Config.just_installed:
        from sys import exit, executable
        from subprocess import call
        exit(call([executable] + sys.argv))

    fname = join( Config.baseDir, 'bin', Config.scriptDir,
                  "%s-script.pyc" % (name,) )
    if not path_exists(fname):
        import py_compile
        py_compile.compile(fname[:-1])
    script = open(fname, 'rb')

    # This is a trick to directly execute the compiled script bytecode:
    # the first 8 bytes in a pyc are actually 2 longs: a version stamp
    # and a timestamp.  The rest of the file is straight bytecode.
    pyc = script.read()
    env = dict()
    env['__name__'] = '__main__'
    # Hide the fact that we are using a wrapper executable (on Windows)
    sys.argv[0] = sys.argv[0].replace('-script.py','')
    from marshal import loads
    exec(loads(pyc[8:]), env, env)


def localized_script(name):
    return join( Config.baseDir, 'bin', Config.scriptDir,
                 '%s-script.py' % (name,) )


