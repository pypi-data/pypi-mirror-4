#!/bin/env/python
# -*- coding: utf-8 -*-

"Run all available test cases in this directory."


import sys
import unittest
import os
from os.path import splitext
from glob import glob


# for some reason test_multi.py fails when run from here...
def main0():
    "Run all available test cases from test modules in this directory."

    # get modules names    
    pyFiles = glob("test_*.py")
    modNames = [splitext(fn)[0] for fn in pyFiles if fn != __file__]

    # import modules and build test suite
    loader = unittest.TestLoader()    
    for mn in modNames:
        mod = __import__(mn)
        if mod:
            suite = loader.loadTestsFromModule(mod)
            unittest.TextTestRunner().run(suite)
    

def main():
    "Run all available test cases from test modules in this directory."

    # get modules names    
    testFiles = glob("test_*.py")
    testFiles = [fn for fn in testFiles if fn != __file__]

    # execute test modules individually
    for fn in testFiles:
        cmd = "%s %s" % (sys.executable, fn)
        os.system(cmd)
            

if __name__ == "__main__":
    main()
