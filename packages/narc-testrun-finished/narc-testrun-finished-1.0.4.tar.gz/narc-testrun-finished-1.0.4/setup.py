#!/usr/bin/env python

__author__ = 'Jason Corbett'

import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name="narc-testrun-finished",
    description="A plugin for narc to mark testruns as finished whenever they run out of NO_RESULT results",
    version="1.0" + open("build.txt").read(),
    license="License :: OSI Approved :: Apache Software License",
    long_description=open('README.txt').read(),
	py_modules=['narc_testrunfinished',],
    install_requires=['slickqa-narc>=1.0.7', 'slickqa>=2.0.15'],
    author="Slick Developers",
    url="http://code.google.com/p/slickqa",
    entry_points={
        'narc.response' : ['testrunfinished = narc_testrunfinished:TestrunFinishedPlugin',]
    }
)
