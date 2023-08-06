#!/usr/bin/env python

__author__ = 'Jason Corbett'

import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name="slickqa",
    description="A client library for the Slick QA result database",
    version="2.0" + open("build.txt").read(),
    license="License :: OSI Approved :: Apache Software License",
    long_description=open('README.txt').read(),
    packages=find_packages(),
    package_data={'': ['*.txt', '*.rst', '*.html']},
    include_package_data=True,
    install_requires=['requests>=1.1.0',],
    author="Slick Developers",
    url="http://code.google.com/p/slickqa"
)
