# -*- coding: utf-8 -*-
# python setup.py register sdist upload
from distutils.core import setup
    
setup(
    name = "ipget",
    py_modules = ["ipget"], 
    scripts = ["ipget.py"], 
    version = "0.1a",
    license = "LGPL",        
    platforms = ['Linux', 'Mac'],
     description = "This package is for those that know the local ip in linux.",
    author = "Yuta Kitagami",
    author_email = "hokusin02@gmail.com",
    url = "http://kitagami.org",
    keywords = ["Linux", "ip", "ifconfig"],
    classifiers = [
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
       "Operating System :: MacOS", 
		"Operating System :: Unix", 
		"Operating System :: POSIX", 
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Topic :: Software Development",
        ],
    long_description = """\
This package is for those that know the local ip in linux.

>>> import ipget
>>> a = ipget.ipget()
>>> print a.ipaddr("eth0")
192.168.0.2/24
>>> print a.ipaddr6("eth0")
xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx/64
>>> print a.mac("eth0")
xx:xx:xx:xx:xx:xx

Thank you.
...
"""
    )


 
