#!/usr/bin/env python
# -*- coding: latin1 -*- vim: ts=8 sts=4 sw=4 si et tw=79
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from os.path import dirname, join

def read(name):
    fn = join(dirname(__file__), name)
    return open(fn, 'r').read()

__author__ = "Tobias Herp <tobias.herp@gmx.net>"
VERSION = (0,
           1,   # initial version
           1,   # Syntax errors removed
           ## the Subversion revision is added by setuptools:
           # 'rev-%s' % '$Rev: 907 $'[6:-2],
           )
__version__ = '.'.join(map(str, VERSION))

setup(name='thebops'
    , version=__version__
    , packages=find_packages()
    , scripts=['scripts/rexxbi_demo.py',
               'scripts/shtools_demo.py',
               'scripts/termwot_demo.py',
               'scripts/scanpath.py',
               'scripts/py-env.py',
               'scripts/fancyhash.py',
               ]
    , author='Tobias Herp'
    , author_email='tobias.herp@gmx.net'
    , namespace_packages = ['thebops']
    , description="Tobias Herp's bag of Python stuff"
    , license='GPL'
    , long_description=read('README.TXT')
    )

