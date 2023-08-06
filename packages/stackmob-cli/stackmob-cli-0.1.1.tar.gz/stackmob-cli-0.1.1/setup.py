#!/usr/bin/env python

from setuptools import setup

setup(name='stackmob-cli',
version='0.1.1',
description='A command line interface for accessing your StackMob API',
author='Aaron Schlesinger',
author_email='aaron@stackmob.com',
url='http://github.com/stackmob/stackmob-cli',
scripts=['stackmob-cli'],
packages=['client', 'util'],
install_requires=['oauth', 'requests'])
