#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='zaguan',
    version='0.1',
    author='Felipe Lerena',
    author_email='flerena@msa.com.ar',
    packages=['zaguan'],
    scripts=[],
    url='http://pypi.python.org/pypi/zaguan/',
    license='LICENSE.txt',
    description='Front end framework to develop apps with webkit an pygtk',
    long_description=open('README.txt').read(),
    install_requires=[],
)
