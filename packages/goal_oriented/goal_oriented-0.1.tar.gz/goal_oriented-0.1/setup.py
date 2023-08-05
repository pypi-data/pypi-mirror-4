#!/usr/bin/env python

from distutils.core import setup

with open('README.txt') as f:
	long_description = f.read()

setup(
	name='goal_oriented',
	version='0.1',
	author='Emanuele Acri',
	author_email='crossbower@gmail.com',
	mantainer='Emanuele Acri',
	mantainer_email='crossbower@gmail.com',
	license='This module is distributed under the BSD license, and it is reusable by everyone',
	description='This module provides a simple facility to the goal-oriented programming paradigm',
	long_description=long_description,
	platforms='UNKNOWN',
	py_modules=['goal_oriented']
	)
