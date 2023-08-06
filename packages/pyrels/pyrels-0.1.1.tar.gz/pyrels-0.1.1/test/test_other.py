#!/usr/bin/env python

"Test cases for pyrels"


import os, sys, unittest, time, pprint, re

sys.path.insert(0, "../src")

from pyrels import pyrels2dot
from testutils import filterIDs


def trace(frame, event, arg):
    print "traced"
    

def namespace2dot_delay(ns, path):
    "Call namespace2dot() and wait a short while."
    
    pyrels2dot.namespace2dot(ns, path)
    time.sleep(3)
            

class StandardLibraryTests(unittest.TestCase):
    "Tests for various modules and packages of the Python standard library."

    outputDir = "output/"

    def setUp(self):
        if not os.path.exists(self.outputDir):
            os.mkdir(self.outputDir)


    def test_stdlib(self):
        "Test on some modules in the std. library."
        
        # problems: tokenize
        modNames = "md5 sha glob keyword functools commands this atexit math os sys re urllib colorsys platform decimal unittest warnings".split()
        for mn in modNames:
            mod = __import__(mn)
            path = self.outputDir + "StdLib.%s.dot" % mn
            pyrels2dot.namespace2dot(mod.__dict__, path, 
                gvtool="neato", format="pdf")


    def _test_md5(self):
        "Test on module md5 in the std. library."
        
        # problems: tokenize
        modNames = "md5".split()
        for mn in modNames:
            mod = __import__(mn)
            path = self.outputDir + "StdLib.%s.dot" % mn
            print "#############", mod.__dict__
            pyrels2dot.namespace2dot(mod.__dict__, path, 
                gvtool="neato", format="pdf")


    def test_md5_test(self):
        "Test on module md5 in the std. library."
        
        from pprint import pprint

        modNames = "md5".split()
        for mn in modNames:
            mod = __import__(mn)
            del mod.__builtins__
            pprint(mod.__dict__.keys())
            path = self.outputDir + "StdLib.%s.dot" % mn
            # print "#############", mod.__dict__
            pyrels2dot.namespace2dot(mod.__dict__, path, 
                gvtool="neato", format="pdf")


    def test_misc_test(self):
        "Test misc. modules in the std. library."
        
        from pprint import pprint

        modNames = "sha md5 this".split()
        modNames = "md5 sha glob keyword functools commands this atexit math os sys re urllib colorsys platform decimal unittest warnings".split()
        modNames = "decimal unittest warnings atexit functools commands glob keyword sha md5 platform".split()
        for mn in modNames:
            mod = __import__(mn)
            if 0:
                try:
                    del mod.__builtins__
                except AttributeError:
                    continue
                pprint(mod.__dict__.keys())
            path = self.outputDir + "StdLib.%s.dot" % mn
            # print "#############", mod.__dict__
            pyrels2dot.namespace2dot(mod.__dict__, path, 
                gvtool="neato", format="pdf")


class PackageTests(unittest.TestCase):
    "Test namespaces for other installed packages."
    
    outputDir = "output/"

    def setUp(self):
        if not os.path.exists(self.outputDir):
            os.mkdir(self.outputDir)


    def test0(self):
        "Test a series of third party packages."
        
        modNames = "fileinfo reportlab pylint alterparagraphs pyPdf numpy".split()
        for mn in modNames:
            try:
                mod = __import__(mn)
            except ImportError:
                continue
            path = self.outputDir + "Packages.%s.dot" % mn
            pyrels2dot.namespace2dot(mod.__dict__, path, 
                gvtool="neato", format="pdf")


    def test1(self):
        "Test."
        
        from alterparagraphs import simpleparagraph
        path = self.outputDir + "Packages.simpleparagraph.dot"
        pyrels2dot.namespace2dot(simpleparagraph.__dict__, path, 
            gvtool="neato", format="pdf")


class EvolutionTests(unittest.TestCase):
    "Test namespaces changing over time."
    
    outputDir = "output/"

    def setUp(self):
        if not os.path.exists(self.outputDir):
            os.mkdir(self.outputDir)


    def _test_evolution(self):
        "Test a namespace with incremental changes."
        
        # sys.settrace(trace)
        
        path = self.outputDir + "test_evolution.dot"
        
        namespace2dot_delay(locals(), path)    
        anInt = 123
        namespace2dot_delay(locals(), path)    
        aFloat = 3.14
        namespace2dot_delay(locals(), path)    
        aComplex = 3j    
        namespace2dot_delay(locals(), path)    
        ndComplex = aComplex    
        namespace2dot_delay(locals(), path)    
    
        sys.settrace(None)


class StandardTests(unittest.TestCase):

    outputDir = "output/"

    def setUp(self):
        if not os.path.exists(self.outputDir):
            os.mkdir(self.outputDir)


    def test0(self):
        "Preliminary standard test."
            
        if True:
            aString = "abc"
            anotherString = "abc"
            unicodeString = u"abc"
                
            anInt = 123
            aLong = 99999L
            aFloat = 3.14
            aComplex = 3j
        
            aList = [1, 2]
            aTuple = (11, (22, (33, aList)))

            mtList = []
            ndMtList = []
            mtTuple = tuple([])
            ndMtTuple = tuple([])
            aDict = {1:True, 2:None}
            a = None
            t = True
            t1 = True
            f = lambda x:x
            l = len
            rng = range(10)
            xrng = xrange(10)
            myFile = open(__file__, "r")
            o = object()

            class C: 
                pass
            c = C()

        import unittest
        dd = {"unit":unittest}
        aList = [1, 2]
        aTuple = (11, (22, (33, aList)))
                    
        namespace = locals()
        del namespace['self']
            
        path = self.outputDir + "StandardTests.test0.dot"
        pyrels2dot.namespace2dot(namespace, path, 
            gvtool="neato", format="pdf")


    def _test1(self):
        "Preliminary records test."
            
        def rec(date, desc, amount, **kwdict):
            record = {"date": date, "desc": desc, "amount": amount}
            record.update(kwdict)
            return record
            
        all = [
          rec('2007-01-02', 'Restauration', 25.00, curr='EUR'),
          rec('2007-01-02', 'Food',         10.93, curr='EUR',),
          rec('2007-01-02', 'Car',          50.29, curr='EUR',),
          rec('2007-01-02', 'Books',        10.00, curr='EUR',),
        ]

        path = self.outputDir + "StandardTests.test1.dot"
        pyrels2dot.namespace2dot(locals(), path, 
            gvtool="neato", format="pdf")


if __name__ == "__main__":
    unittest.main()
    