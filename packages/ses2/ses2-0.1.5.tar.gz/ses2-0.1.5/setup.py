#!/usr/local/bin/python
from distutils.core import setup

setup(
	name='ses2',
	version='0.1.5',
	author='Darrell Enns',
	author_email='darrell@darrellenns.com',
	url='http://pypi.python.org/pypi/ses2',
	description='Library for status/control of SES2 enclosure management devices',
	classifiers=[
		"Programming Language :: Python","Programming Language :: Python :: 3",
		"Operating System :: POSIX :: BSD :: FreeBSD",
		"Intended Audience :: Developers",
		"License :: Other/Proprietary License",
		"Topic :: System :: Hardware"
		],
	py_modules=['ses2'],
	scripts=['sestool']
)
