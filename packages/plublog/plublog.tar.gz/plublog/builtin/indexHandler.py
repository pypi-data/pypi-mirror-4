#!/usr/bin/python
#coding=utf-8

import sys
import os
from plublog.options import o

o.page['index.html'] = o.jinja2.get_template('index.html').render()
