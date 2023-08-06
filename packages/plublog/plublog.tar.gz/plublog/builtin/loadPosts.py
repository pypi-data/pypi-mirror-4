#!/usr/bin/python
#coding=utf-8

import os
from plublog.options import o

for _file in os.listdir('posts'):
    _file = os.path.join('posts', _file)
    if _file.endswith('.html') & os.path.isfile('%s' % _file):
        o.posts.append([_file[6:], open(_file).read()])
# o.posts should like: [['file', 'content'], [...]]
