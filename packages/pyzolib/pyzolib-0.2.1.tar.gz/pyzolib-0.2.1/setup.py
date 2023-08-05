# -*- coding: utf-8 -*-
# Copyright (c) 2012, The Pyzo team
#
# This file is distributed under the terms of the (new) BSD License.

import os
import sys
from distutils.core import setup

name = 'pyzolib'
description = 'Utilities for the Pyzo environment.'

# Get version and docstring
__version__ = None
__doc__ = ''
docStatus = 0 # Not started, in progress, done
initFile = os.path.join(os.path.dirname(__file__), '__init__.py')
for line in open(initFile).readlines():
    if (line.startswith('__version__')):
        exec(line.strip())
    elif line.startswith('"""'):
        if docStatus == 0:
            docStatus = 1
            line = line.lstrip('"')
        elif docStatus == 1:
            docStatus = 2
    if docStatus == 1:
        __doc__ += line

setup(
    name = name,
    version = __version__,
    author = 'Science Applied',
    author_email = 'a.klein@science-applied.nl',
    license = '(new) BSD',
    
    url = 'http://code.google.com/p/pyzolib/',
    download_url = 'http://code.google.com/p/pyzolib/downloads/list', # todo: pypi?
    keywords = "Pyzo cython gcc path paths interpreters",
    description = description,
    long_description = __doc__,
    
    platforms = 'any',
    provides = ['pyzolib'],
    requires = [], # No requirements
    
    packages = ['pyzolib', 'pyzolib.ssdf', 'pyzolib.interpreters'],
    py_modules = [  'pyzolib.path', 'pyzolib.paths', 
                    'pyzolib.pyximport', 'pyzolib.gccutils',
                    'pyzolib.insertdocs', ],
    package_dir = {'pyzolib': '.'}, # must be a dot, not an empty string
    )
