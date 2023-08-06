#!/usr/bin/env python
# -*- coding: latin1 -*- vim: ts=8 sts=4 sw=4 si et tw=79
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from os.path import dirname, abspath, join

def read(name):
    fn = join(dirname(abspath(__file__)), name)
    return open(fn, 'r').read()

__author__ = "Tobias Herp <tobias.herp@gmx.net>"
VERSION = (0,
           3, # sys.argv-Filterung
           12, # i18n preparations
           ## the Subversion revision is added by setuptools:
           # 'rev-%s' % '$Rev: 942 $'[6:-2],
           )
__version__ = '.'.join(map(str, VERSION))

setup(name='tsvn'
    , version=__version__
    , packages=find_packages()
    , entry_points = {
        'console_scripts': [
            '%s = thebops.tools.%s:main'
                % (s, s.replace('-', '_'))
            for s in [
                'tsvn',
                ]
            ],
        }
    , author='Tobias Herp'
    , author_email='tobias.herp@gmx.net'
    , namespace_packages = ['thebops',
                            'thebops.tools',
                            ]
    , description="svn-like commandline interface to TortoiseSVN"
    , license='GPL'
    , install_requires=['thebops >= 0.1.3',
                        ]
    , long_description=read('README.txt')
    )

