#!/usr/bin/python
#coding=utf-8

from plublog.options import o

o.posts = []
o.jinja2 = None
o.page = {}
import loadPosts
import loadJinja2
import indexHandler
