#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

import os
import redcap

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


required = ['requests>=0.12.1']

if __name__ == '__main__':
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    long_desc = open('README.rst').read() + '\n\n' + open('HISTORY.rst').read()

    setup(name='PyCap',
        maintainer='Scott Burns',
        maintainer_email='scott.s.burns@gmail.com',
        description="""PyCap: Python interface to REDCap""",
        license='BSD (3-clause)',
        url='http://sburns.github.com/PyCap',
        version=redcap.__version__,
        download_url='http://sburns.github.com/PyCap',
        long_description=long_desc,
        packages=['redcap'],
        install_requires=required,
        platforms='any',
        classifiers=(
                'Development Status :: 4 - Production/Stable',
                'Intended Audience :: Developers',
                'Intended Audience :: Science/Research',
                'License :: OSI Approved',
                'Topic :: Software Development',
                'Topic :: Scientific/Engineering',
                'Operating System :: Microsoft :: Windows',
                'Operating System :: POSIX',
                'Operating System :: Unix',
                'Operating System :: MacOS',
                'Programming Language :: Python',
                'Programming Language :: Python :: 2.7',)
        )
