#!/usr/bin/env python
"""FrankenCircuits: Setuptools based installation script.

Created: 2013-03-18 by Justin Giorgi

Use the python-setuptools package to install to the Python path.
"""

# Standard library imports
from os.path import join, dirname
from setuptools import setup

def read(fname):
	"""Open a file, read it, close it and return the entire contents of the
	file.
	"""
	f = open(join(dirname(__file__), fname))
	ret = f.read()
	f.close()
	return ret

setup(
    name = "FrankenCircuits",
    version = read("VERSION"),
    author = "Justin Giorgi",
    author_email = "justin@justingiorgi.com",
    maintainer = "Justin Giorgi",
    maintainer_email = "justin@justingiorgi.com",
    download_url = "http://bitbucket.org/jgiorgi/frankencircuits/downloads",
	requires = "Circuits",
    description = "Plugin library for Circuits and Circuits.Web",
    license = "GPLv3",
    keywords = "plugin, library, circuits, framework, circuits.web, web",
    url = "http://bitbucket.org/jgiorgi/frankencircuits",
    packages=['frankencircuits'],
    long_description=read("README"),
    classifiers=[
	"Development Status :: 3 - Alpha",
	"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
	"Natural Language :: English",
	"Operating System :: OS Independent",
	"Programming Language :: Python :: 2.6",
	"Programming Language :: Python :: 2.7",
	"Topic :: Software Development :: Libraries"
    	],
)


