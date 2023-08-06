#!/usr/bin/python
#coding=utf-8

import os
import plublog
import plublog.options

################ Inital config file ################
c = plublog.options.c

c.add_section('Site')
c.set('Site', 'name', 'plublog')
c.set('Site', 'title', 'hello')
c.set('Site', 'description', 'welcome to plublog :)')
c.set('Site', 'url', 'http://localhost/')

c.add_section('Theme')
c.set('Theme', 'theme', 'your_theme_name')

c.add_section('Build')
c.set('Build', 'build_path', '/your/path/')

c.add_section('Path')
c.set('Path', 'blog_path', os.getcwd())

c.write(open(plublog.__config__, 'w'))


################ Inital folders ################
os.mkdir('posts')
os.mkdir('site')
os.mkdir('templates')
os.mkdir('theme')
os.mkdir('plugins')


################ Inital file __init__.py for plugins ################
with open('plugins/__init__.py', 'w') as f:
    f.write("""\
import os
for _file in os.listdir('plugins'):
    if _file == '__init__.py' or not _file.endswith('.py'):    pass
    else:
        exec('import %s' % _file[:-3])"""
    )
    f.close()
