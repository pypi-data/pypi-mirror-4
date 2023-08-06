
# Copyright (c) 2013 Daniel Foote.
#
# See the file LICENSE for copying permission.

from distutils.core import setup

setup(
	name='pminterface',
	description="Paasmaker Python interface library",
	author="Daniel Foote",
	author_email="freefoote@paasmaker.org",
	url="http://paasmaker.org",
	version='0.9',
	packages=['pminterface'],
	classifiers = [
		"Programming Language :: Python",
		"Development Status :: 4 - Beta",
		"Environment :: Other Environment",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
	],
	long_description=open('README').read()
)