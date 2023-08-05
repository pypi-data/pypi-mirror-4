#!/usr/bin/python

import os
from distutils.core import setup

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='common-python-difio',
    version='1.3.1',
    description='Common module for Difio Python clients',
    author='Alexander Todorov',
    author_email='atodorov@nospam.dif.io',
    url = 'http://github.com/difio/common-difio-python',
    keywords = ['difio', 'updates', 'cloud'],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: System",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        ],
    long_description = long_description,
    install_requires = ['pip'],
    packages=['common_difio'],
)
