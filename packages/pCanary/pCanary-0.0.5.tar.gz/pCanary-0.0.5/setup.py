# Work around mbcs bug in distutils.
# http://bugs.python.org/issue10945
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc=ascii: {True: enc}.get(name=='mbcs')
    codecs.register(func) 

import os
from setuptools import setup

# Utility function to read the README.txt file.  
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pCanary",
    version = "0.0.5",
    author = "Jeremiah O'Neal",
    author_email = "we6jbo@gmail.com",
    description = ("pCanary is a opensource recipe and ore lookup"
				   "application for Minecraft"),
    license = "GNU GPL3",
    keywords = "minecraft recipe ore graphical",
    url = "http://tinyurl.com/pCanary81",
    packages=['pCanary', 'canary'],
    long_description=read('README.txt'),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Environment :: X11 Applications",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
