#!/usr/bin/python
#coding=utf-8

from tornado.util import ObjectDict as o
from ConfigParser import ConfigParser
import plublog

c = ConfigParser()
c.read(plublog.__config__)
o.config = {}

for section in c.sections():
    o.config[section] = {}
    for key in c.options(section):
        o.config[section][key] = c.get(section, key)
# o.config should like: {'Section': {'key': 'value'}, {...}}
