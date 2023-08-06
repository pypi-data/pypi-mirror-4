#!/usr/bin/python
#coding=utf-8

import sys
import os
import plublog.builtin
sys.path.append(os.getcwd())
import plugins
from options import o

os.chdir('site')

for page in o.page:
    with open(page, 'w') as f:
        f.write(o.page[page])
        f.close()
