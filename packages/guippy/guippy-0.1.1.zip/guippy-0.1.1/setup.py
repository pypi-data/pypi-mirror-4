#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import guippy

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name=guippy.__name__,
    version=guippy.__version__,
    author=guippy.__author__,
    author_email='tak.esxima@gmail.com',
    description='Control the Windows GUI',
    long_description=guippy.__doc__,
    url='https://bitbucket.org/tak_esxima/guippy',
    download_url='https://bitbucket.org/tak_esxima/guippy/get/6635a55503f0.zip',
    packages=['guippy'],
    include_package_data=True,
    install_requires=[],
    classifiers=(
        'Development Status :: 1 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License Version 3',
        'Operating System :: Microsoft :: Windows',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications :: Email',
        'Topic :: Officee/Business',
        ),
    )

