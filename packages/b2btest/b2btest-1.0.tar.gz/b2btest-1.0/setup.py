#!/usr/bin/python
from distutils.core import setup

readme = """\
This software is helpfull to prepare and manage a set
of back2back test scripts over any piece of software
that can be called and controlled by command line and
produces output files that can be compared against
some other reference files.

You can define the tests in a simple Python script,
and the framework will help you initializing the
reference data, spotting differences with results,
and managing the aceptance of new references.
"""

setup(
	name = "b2btest",
	version = "1.0",
	requires=['wavefile'],
	description = "Light framework to setup back-to-back test scripts",
	author = "David Garcia Garzon",
	author_email = "voki@canvoki.net",
	url = 'https://github.com/vokimon/back2back',
	long_description = readme,
	license = 'GNU General Public License v3 or later (GPLv3+)',
	packages=[
		'b2btest',
		],
	classifiers = [
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Intended Audience :: Developers',
		'Development Status :: 5 - Production/Stable',
		'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
		'Operating System :: OS Independent',
	],
	)

