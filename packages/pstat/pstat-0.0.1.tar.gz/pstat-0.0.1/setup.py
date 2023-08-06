#!/usr/local/bin/python2.7
#coding:utf-8
import os
from setuptools import setup, find_packages

# package meta info
NAME = "pstat"
VERSION = "0.0.1"
DESCRIPTION = ""
AUTHOR = "CMGS"
AUTHOR_EMAIL = "ilskdw@gmail.com"
LICENSE = "BSD"
URL = "https://github.com/CMGS/pstat"
KEYWORDS = "process"
CLASSIFIERS = []

# package contents
MODULES = ['pstat']
PACKAGES = find_packages(exclude=['tests.*', 'tests', 'examples.*', 'examples'])
ENTRY_POINTS = """
"""

# dependencies
INSTALL_REQUIRES = ['psutil']
TESTS_REQUIRE = ['nose']
TEST_SUITE = 'nose.collector'

here = os.path.abspath(os.path.dirname(__file__))


def read_long_description(filename):
    path = os.path.join(here, filename)
    if os.path.exists(path):
        return open(path).read()
    return ""

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read_long_description('README.md'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    py_modules=MODULES,
    packages=PACKAGES,
    zip_safe=False,
    entry_points=ENTRY_POINTS,
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    test_suite=TEST_SUITE,
)

