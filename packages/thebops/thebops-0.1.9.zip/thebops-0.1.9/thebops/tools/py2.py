#!/usr/bin/env python
# -*- coding: latin1 -*- vim: ts=8 sts=4 sw=4 si et tw=79
"""\
Ruft den "besten" Python-2-Interpreter auf dem System auf
"""

__author__ = "Tobias Herp <tobias.herp@gmx.net>"
VERSION = (0,
           1,   # initial version
           'rev-%s' % '$Rev: 955 $'[6:-2],
           )
__version__ = '.'.join(map(str, VERSION))

from sys import argv
from subprocess import Popen
from thebops.likeix import find_python, get_best

def main():
    PYTHON = get_best(find_python,
                      version_below=(3, 0))
    rc = Popen([PYTHON]+argv[1:]).wait()
    raise SystemExit(rc)

if __name__ == '__main__':
    main()
