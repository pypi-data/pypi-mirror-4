#!/usr/bin/env python

import os
try:
    from setuptools import setup
except ImportError:
    print 'setuptools are required for the setup. Get it at http://pypi.python.org/pypi/setuptools...'
    exit(1)

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "mcommand",
    version = "0.2",
    entry_points = {},
    author = "Jakub Dvorak",
    author_email = "nytmyn@gmail.com",
    description = ("Mercurial-like command dispatch"),
    license = "BSD",
    keywords = "command console",
    url = "https://bitbucket.org/nytmyn/mcommand",
    packages = [],
    py_modules = ['mcommand'],
    long_description=read('README'),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Utilities"
    ],
)
