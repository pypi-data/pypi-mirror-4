#!/usr/bin/env python
# # cat ~/.pypirc
# [pypirc]
# servers = pypi
# [server-login]
# username:
# password:
# 
# python setup.py register sdist upload
# python setup.py sdist upload

from setuptools import setup, find_packages

setup(
		name = "youkudownloader",
		version="0.1.4",
		packages = find_packages(),
		scripts = ['scripts/youkudownloader','scripts/fastreaming'],

		description = "Python module and script for downloading video source files from the major video sites in China.",
		long_description = "Python module and script for downloading video source files from the major video sites in China.",
		author = "feisky",
		author_email = "feiskyer@gmail.com",		

		license = "MIT",
		keywords = ("video downloader", "youku"),
		platforms = "Independant",
		url = "http://www.cnblogs.com/feisky/",

	 )

