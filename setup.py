#!/usr/bin/env python
#
# Usage: python setup.py install
#

try:
	from setuptools import setup, find_packages
except ImportError:
	import ez_setup
	ez_setup.use_setuptools()
	from setuptools import setup, find_packages

name = "howl"
version = "0.6"
author = "William Wiens"
license="MIT"
description="Howl music server"
long_description="""Howl is a python-based webserver that allows applications to access the script interfaces of desktop media players. Plugins for players like iTunes and Windows Media Player provide a web-service to each players script interface, and plugins like Howl provide user interfaces to the exposed web-services"""
packages=find_packages(exclude=['tests'])
dependencies = ["CherryPy",
				"simplejson",
				"appscript"]

def main():
	dist = setup(
		name = name,
		version = version,
		description = description,
		long_description = long_description,
		author = author,
		license = license,
		packages = packages,
		include_package_data = True,
		install_requires = dependencies,
		entry_points = {
			'console_scripts': [
				'howl = howl:main'
			]
		}
		)


if __name__ == "__main__":
	main()