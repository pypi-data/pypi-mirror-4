from distutils.core import setup

setup(
	name = "placefinder-py",
	version = "0.3",
	description = "Yahoo! BOSS PlaceFinder Python Client",
	long_description = "placefinder-py is a small Python module that provides the ability to work with Yahoo's BOSS PlaceFinder geocoding server (http://developer.yahoo.com/boss/geo/). This module provides all the basic functions needed to geocode address to latitude/longitude values as well as reverse-geocoding.",
	author = "Adam Presley",
	author_email = "adam@adampresley.com",
	url = "https://github.com/adampresley/placefinder-py",
	py_modules = [ "placefinder" ],
	requires = [ "oauth2" ],
	provides = [ "placefinder" ],
	classifiers = [
		"Environment :: Web Environment",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python",
		"Operating System :: OS Independent"
	]
)
