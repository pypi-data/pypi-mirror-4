#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from pycnb import version

setup(
    name='pycnb',
    version=version,
    description='Library, CLI and Twisted protocol for `Czech National Bank daily rates',
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
