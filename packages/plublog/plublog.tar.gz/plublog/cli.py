#!/usr/bin/python
#coding=utf-8

from sys import argv
import plublog

doc = """You can run plublog by:
    plublog build
    plublog init
========== plublog v%s ==========""" % plublog.__version__


def main():
    if len(argv) == 1:
        print doc
    elif argv[1] == "build":
        import plublog.build
    elif argv[1] == "init":
        import plublog.init
    else:
        print doc
