#!/usr/bin/python
#coding=utf-8

import os
import jinja2
from plublog.options import o

o.jinja2 = jinja2.Environment(
    loader=jinja2.FileSystemLoader([
        'templates', os.path.join('theme', o.config['Theme']['theme'])
    ])
)
o.jinja2.globals['Site'] = o.config['Site']
o.jinja2.globals['Posts'] = o.posts
