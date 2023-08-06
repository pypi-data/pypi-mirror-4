.. -*- mode: rst -*-

========
Pyrels
========

---------------------------------------------------------------
Explore and visualize relationships between Python objects.
---------------------------------------------------------------

:Author:  Dinu Gherman <gherman@darwin.in-berlin.de>
:Homepage: http://www.dinu-gherman.net/
:Version: Version 0.1.1
:Date: 2013-02-07
:Copyright: GNU Public Licence v3 (GPLv3)


About
-----

*Pyrels* is a tool for exploring and visualizing relationships between 
Python objects. It does so by analysing and converting Python namespaces 
into `GraphViz <http://www.graphviz.org>`_ files in the 
`DOT <http://www.graphviz.org/doc/info/lang.html>`_ format. 
That means it displays relationships like references between Python names 
and the objects they point to, as well as containment between Python 
container objects (lists, tuples and dictionaries) and the respective 
objects they contain.

At the moment *pyrels* is best used on Python data structures, but it is 
intended to develop it further so that it can also display other types of  relationships like inheritance, module imports, etc. 

One target group for *pyrels* are article and/or book authors who wish to 
illustrate Python data structures graphically without spending a lot of 
time for creating these illustrations manually. *Pyrels* can help you 
automate this process. 


Installation
------------

After downloading the file ``pyrels-0.1.1.tar.gz`` in your download
directory, change into this directory and run the following command 
to unpack *pyrels*::

  $ tar xfz pyrels-0.1.1.tar.gz

Then change into the newly created directory ``pyrels`` and install 
*pyrels* by running the following command::

  $ python setup.py install

This will install a Python package named *pyrels* in the 
``site-packages`` subfolder of your Python interpreter and a script 
tool named ``pyrels`` in your ``bin`` directory, usually in 
``/usr/local/bin``.


Dependencies
------------

Some of *pyrels'* functions call command-line tools installed 
with GraphViz, like ``dot``, ``neato``, etc. In order for these to 
work you must have GraphViz installed.


Examples
--------

From the system command-line you use ``pyrels`` e.g. like this::

  $ pyrels "L = [1, 'two', None]"
  
You can use *pyrels* also as a Python package e.g. like this::

  >>> from pyrels.pyrels2dot import namespace2dot as ns2dot
  >>> ns2dot(ns, outPathDot, gvtool="dot", format="pdf")
  

Testing
-------

The *pyrels* package comes with a Unittest test suite which 
can be run like this before (or after) building the package::
 
  $ cd test
  $ python test_all.py

After the test run you'll find some PDF files in the directory 
``test/output``.


Bug reports
-----------

Please report bugs and patches to Dinu Gherman 
<gherman@darwin.in-berlin.de>. Don't forget to include information 
about the operating system, Python and GraphViz versions being used.
