#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from setuptools import setup

from alexis import __version__

if sys.version_info >= (3,):
    sys.stderr.write('Sorry! Not ready for Python 3.x')
    sys.exit(1)

readme = open('README.rst', 'r').read()

setup(
    name='clever-alexis',
    version=__version__,
    description='Clever redhead girl that builds and packs Python project with Virtualenv into rpm, deb, etc.',
    author='Taras Drapalyuk (KulaPard)',
    author_email='kulapard@gmail.com',
    url='https://bitbucket.org/KulaPard/alexis',
    packages=['alexis', 'alexis.libs'],
    include_dirs=['alexis/libs',],
    install_requires=['fabric>=1.4.0', ],
    long_description=readme,
    license='BSD License',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python'
    ]
)