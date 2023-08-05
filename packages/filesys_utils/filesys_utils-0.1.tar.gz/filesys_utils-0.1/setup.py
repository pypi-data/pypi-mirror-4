#!/usr/bin/env python

from distutils.core import setup

with open('README.txt') as f:
	long_description = f.read()

setup(
	name='filesys_utils',
	version='0.1',
	author='Andrea Leopardi',
	author_email='an.leopardi@gmail.com',
	mantainer='Andrea Leopardi',
	mantainer_email='an.leopardi@gmail.com',
	license='This module is distributed under the GNU license, and it is reusable by everyone',
	description='Utilities for working (only under Unix, for now) with file and directories sizes, space on internal/external hard drives',
	long_description=long_description,
	platforms='Unix',
	py_modules=['filesys_utils']
	)