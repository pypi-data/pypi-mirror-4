#!/usr/bin/python
#coding=utf-8

from setuptools import setup, find_packages
import plublog

setup(
    name='plublog',
    version=plublog.__version__,
    author='rephaslife',
    author_email='rephaslife@gmail.com',
    url='http://github.com/rephaslife/plublog/',
    description='anthor static blog generator..',
    entry_points={
        'console_scripts': ['plublog = plublog.cli:main'],
    },
    packages=find_packages()
)
