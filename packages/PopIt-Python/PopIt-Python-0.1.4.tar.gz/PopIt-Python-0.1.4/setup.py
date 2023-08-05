#!/usr/bin/env python

from setuptools import setup

setup(name='PopIt-Python',
	version='0.1.4',
	description='Python bindings to connect to the PopIt API',
	author='mySociety',
	author_email='modules@mysociety.org',
	url='https://github.com/mysociety/popit-python',
	py_modules=['popit'],
	install_requires=['slumber','requests']
)