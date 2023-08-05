#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION = '0.9.2'

if sys.argv[-1] == 'publish':
    os.system('rm -rf *.egg-info')
    os.system('rm -rf build dist')
    os.system('python setup.py sdist upload')
    sys.exit()


setup(
        name        = 'rhcloud',
        version     = '0.0.1',
        py_modules  = ['rhcloud'],
        author      = 'Fris',
        author_email = 'fris@live.com',
        url         = '',
        description = 'Just for test first',
    )
