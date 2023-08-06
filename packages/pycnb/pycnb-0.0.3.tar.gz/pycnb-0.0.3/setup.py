#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

__version__ = '0.0.3'

setup(
    name='pycnb',
    version=__version__,
    description='pycnb',
    author='Jan Matejka',
    author_email='yac@blesmrt.net',
    url='https://github.com/yaccz/pycnb',

    packages = find_packages(
        where = '.'
    ),

    install_requires = [
        "cement",
        "twisted",
        "setuptools",
    ],

    entry_points = {
        'console_scripts': ['pycnb = pycnb.core:main']},

    classifiers=[
        "Operating System :: POSIX",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Framework :: Twisted",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
)
