#!/usr/bin/env python

from setuptools import setup, find_packages
requires = [
	'RPi.GPIO',
        'picdaemon',
        ]
setup(
    name='briketpi',
    version='0.1.0',
    packages=find_packages(),
    install_requires=requires,)
