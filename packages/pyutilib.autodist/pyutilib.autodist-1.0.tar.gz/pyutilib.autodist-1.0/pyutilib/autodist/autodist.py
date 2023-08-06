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
from sys import version_info as py_ver, path as sys_path
from os import environ, pathsep
from os.path import join, abspath, dirname, exists, getmtime
from inspect import getfile, currentframe

#baseDir = abspath(join(dirname(__file__),".."))
# DO NOT USE __file__ !!!
# __file__ fails if script is called in different ways on Windows
# __file__ fails if someone does os.chdir() before
# sys.argv[0] also fails because it doesn't not always contains the path
myFile = abspath( getfile( currentframe() ) )
myDir = dirname( myFile )

# Python 3-compatible version of "execfile"
#exec( compile( open(os.path.join(myDir, 'autodist_core.py')).read(),
#               os.path.join(myDir, 'autodist_core.py'), 'exec') )

# Since we may not be running this from within the pyutilib.autodist
# package, this is a poor-man's version of "import autodist_core"
autodist_core_pyc = join(myDir, 'autodist_core.pyc')
if not exists(autodist_core_pyc) \
        or getmtime(autodist_core_pyc) < getmtime(myFile):
    import py_compile
    py_compile.compile(autodist_core_pyc[:-1])
# This is a trick to directly execute the compiled script bytecode:
# the first 8 bytes in a pyc are actually 2 longs: a version stamp
# and a timestamp.  The rest of the file is straight bytecode.
from marshal import loads
_pyc = open(autodist_core_pyc, 'rb')
_pyc.read(8)
exec(loads(_pyc.read()))
_pyc.close()


baseDir = abspath(join(myDir, '..'))
targetDir = join(baseDir, 'lib', 'python%i.%i' % py_ver[:2], 'site-packages')
scriptDir = join(baseDir, 'bin', 'local-py%d%d' % py_ver[:2])
Config.setup_paths(baseDir, targetDir, scriptDir)

# Set up our local site-packages
pythonpath = environ.get('PYTHONPATH',None)
if pythonpath:
    environ['PYTHONPATH'] = pathsep.join((targetDir,pythonpath))
else:
    environ['PYTHONPATH'] = targetDir
# Note: insert the targetDir *second* in the list: '' (the current
# directory) should always be first.
sys_path.insert(1,targetDir)
    
# If the site-packages is not present, install it
if not exists(targetDir):
    install_packages(__name__ == '__main__')
    
# Now we need to configure our site-packages (i.e., process the *.pth files)
site.addsitedir(targetDir, site._init_pathinfo())
