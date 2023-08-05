# -*- coding: UTF-8 -*-

""" Setup script for building jaraco-util distribution

Copyright © 2004-2009 Jason R. Coombs
"""

name = 'jaraco.xutil'

from setuptools import setup, find_packages
setup (name = name,
		version = '1.0',
		description = 'Test script',
		author = 'Jason R. Coombs',
		author_email = 'jaraco@jaraco.com',
		url = 'http://pypi.python.org/pypi/'+name,
		packages = find_packages(exclude=['tests']),
		namespace_packages = ['jaraco',],
		license = 'MIT',
		classifiers = [
			"Development Status :: 4 - Beta",
			"Intended Audience :: Developers",
			"Programming Language :: Python",
		],
	)
