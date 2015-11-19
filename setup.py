#!/usr/bin/env python
from setuptools import setup

NAME = 'coyote'
DESCRIPTION = 'An attempt to make a Chaos Monkey like framework in Python'
VERSION = open('VERSION').read().strip()
LONG_DESC = open('README.rst').read()
LICENSE = open('LICENSE').read()

setup(
    name=NAME,
    version=VERSION,
    author='Charles Thomas',
    author_email='ch@rlesthom.as',
    packages=['coyote'],
    url='https://github.com/charlesthomas/%s' % NAME,
    license=LICENSE,
    description=DESCRIPTION,
    long_description=LONG_DESC,
    # install_requires=[],
    # scripts=['bin/'],
    # classifiers=[],
)
