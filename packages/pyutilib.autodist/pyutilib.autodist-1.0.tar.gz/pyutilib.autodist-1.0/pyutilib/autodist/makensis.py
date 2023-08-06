#!/usr/bin/env python
"""Create a "virtual" Python installation
"""

from os.path import join, abspath, dirname, exists, getmtime
from inspect import getfile, currentframe
from optparse import OptionParser

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


def main():
    parser = OptionParser(
        usage="%prog [OPTIONS] target_nsis_dir source_dir")

    parser.add_option(
        '-v', '--verbose',
        action='count',
        dest='verbose',
        default=0,
        help="Increase verbosity")

    parser.add_option(
        '-q', '--quiet',
        action='count',
        dest='quiet',
        default=0,
        help='Decrease verbosity')

    options, args = parser.parse_args()
    
    verbosity = options.verbose - options.quiet
    
    write_nsis_codes(args[0], args[1], verbose=verbosity)    
    
if __name__ == '__main__':
     main()

