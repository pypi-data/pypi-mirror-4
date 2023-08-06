import sys
if sys.version_info[:2] >= (2,6):
    import urllib2
else:
    import httpsproxy_urllib2
import urllib
import re
import struct
import os
import os.path

nbits = struct.calcsize('P')*8

def download_pyqt():
    url = 'http://www.riverbankcomputing.co.uk/static/Downloads/PyQt4/'
    #
    # Download from URL
    #
    output = urllib2.urlopen(url, timeout=30).read()
    if output == '':
        sys.exit(1)
    #
    # Setup pattern
    #
    version = '.'.join(map(str,sys.version_info[:2]))
    if nbits == 32:
        pat = '^PyQt-Py%s-x86-gpl-[^ex]+exe$' % version
    else:
        pat = '^PyQt-Py%s-x64-gpl-[^ex]+exe$' % version
    #
    links = re.findall('<a href[^>]+>[^\<]+\</a>',output)
    for link in links:
	file = re.split('>', link[:-4])[-1]
	if re.match(pat,file):
	    break
        file = None
    if not file:
	print "Compatible PyQt installer found for Python %s %d-bit" % (version, nbits)
        sys.exit(1)
    print "Downloading",file,'...'
    sys.stdout.flush()
    urllib.urlretrieve(url+file, 'PyQt-setup.exe')
    print "done."
    sys.stdout.flush()


def download_pyyaml():
    url = 'http://pyyaml.org/download/pyyaml/'
    #
    # Download from URL
    #
    output = urllib2.urlopen(url, timeout=30).read()
    #sys.exit(1)
    if output == '':
        sys.exit(1)
    #
    # Setup pattern
    #
    version = '.'.join(map(str,sys.version_info[:2]))
    pat = 'PyYAML-(.*)\.win32-py%s\.exe' % version
    #
    links = re.findall('<a href[^>]+>[^\<]+\</a>',output)
    newest_link = None
    newest_version = None
    for link in links:
	file = re.split('>', link[:-4])[-1]
	m = re.match(pat,file)
	if m:
	    version = m.group(1)
	    version = map(int, version.split('.'))
	    if newest_version is None or version < newest_version:
                newest_link = file
		newest_version = version
	    break
        file = None
    if not file:
	print "Compatible PyYAML installer found for Python %s %d-bit" % (version, nbits)
        sys.exit(1)
    print "Downloading",file,'...'
    sys.stdout.flush()
    urllib.urlretrieve(url+file, 'PyYAML-setup.exe')
    print "done."
    sys.stdout.flush()


def download_numpy():
    url = 'http://www.riverbankcomputing.co.uk/static/Downloads/PyQt4/'
    #
    # Download from URL
    #
    output = urllib2.urlopen(url, timeout=30).read()
    if output == '':
        sys.exit(1)
    #
    # Setup pattern
    #
    version = '.'.join(map(str,sys.version_info[:2]))
    if nbits == 32:
        pat = '^PyQt-Py%s-x86-gpl-[^ex]+exe$' % version
    else:
        pat = '^PyQt-Py%s-x64-gpl-[^ex]+exe$' % version
    #
    links = re.findall('<a href[^>]+>[^\<]+\</a>',output)
    for link in links:
	file = re.split('>', link[:-4])[-1]
	if re.match(pat,file):
	    break
        file = None
    print "Downloading",file,'...'
    sys.stdout.flush()
    if not file:
        sys.exit(1)
    urllib.urlretrieve(url+file, 'NumPy-setup.exe')
    print "done."
    sys.stdout.flush()


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if sys.argv[1] == 'PyQt':
        download_pyqt()
    elif sys.argv[1] == 'NumPy':
        download_numpy()
    elif sys.argv[1] == 'PyYAML':
        download_pyyaml()
    else:
        print "ERROR:", ' '.join(sys.argv)
    
