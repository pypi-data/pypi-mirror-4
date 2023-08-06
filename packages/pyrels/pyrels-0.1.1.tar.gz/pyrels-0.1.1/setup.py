#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
from distutils.core import setup

sys.path.insert(0, "src")

from pyrels import __version__, __date__, __license__, __author__


setupCommand = sys.argv[1]


# first try converting README from ReST to HTML, if Docutils is installed
# (else issue a warning)

if setupCommand in ("sdist", "build"):
    toolName = "rst2html.py"
    res = os.popen("which %s" % toolName).read().strip()
    if res.endswith(toolName):
        cmd = "%s '%s' '%s'" % (res, "README.txt", "README.html")
        print "running command %s" % cmd
        cmd = os.system(cmd)
    else:
        print "Warning: No '%s' found. 'README.{txt|html}'" % toolName,
        print "might be out of synch."


# description for Distutils to do its business

baseURL = "http://www.dinu-gherman.net/"

setup(
    name = "pyrels",
    version = __version__,
    description = "A tool for displaying relationships between Python objects.",
    long_description = """\
A tool for displaying relationships between Python objects. 
Currently pyrels takes Python namespaces and generates graphs 
in the GraphViz DOT format that describe Python datastructures 
and references from names to objects.""",
    date = __date__,
    author = __author__,
    author_email = "gherman@darwin.in-berlin.de",
    maintainer = __author__,
    maintainer_email = "gherman@darwin.in-berlin.de",
    license = __license__,
    platforms = ["Posix", "Windows"],
    keywords = ["visualizing", "Python", "relationships", "references", "namespaces"],
    url = baseURL,
    download_url = baseURL + "tmp/pyrels-%s.tar.gz" % __version__,
    package_dir = {"pyrels": "src/pyrels"},
    packages = ["pyrels"],
    scripts = ["scripts/pyrels"],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Education",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)

