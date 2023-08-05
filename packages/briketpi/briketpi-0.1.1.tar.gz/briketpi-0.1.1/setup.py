#!/usr/bin/env python

from setuptools import setup, find_packages
requires = [
	'RPi.GPIO',
	'PyYAML',
        'picdaemon',
        ]
setup(
    name='briketpi',
    version='0.1.1',
    packages=find_packages(),
    install_requires=requires,)
