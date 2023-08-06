#!/usr/bin/env python
# USAGE: unix2dos.py FILENAME1 FILENAME2 ...

import sys
import string
import os.path

for file in sys.argv[1:]:
  if not os.path.exists(file):
     continue
  contents = open(file, 'rb').read()
  open(file, 'wb').write(string.replace(contents, '\n', '\r\n')) 
