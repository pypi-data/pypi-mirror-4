#!/usr/bin/env python

"Basic test cases for pyrels, with some more complex cases."


import os, sys, unittest, re

sys.path.insert(0, "../src")

from pyrels import pyrels2dot
from testutils import sort, filterIDs


class MultiTests(unittest.TestCase):
    """Generate a namespace, create and verify nodes and edges for it.
    
    The generated DOT files are not tested but meant only for rapid 
    eye-ball checks.
    """

    outputDir = "output/"

    def tearDown(self):
        "Save nodes and edges as DOT and PDF files, if possible."

        ns2dot = pyrels2dot.namespace2dot
        outPathDot = os.path.join(self.outputDir + self.outPathDot)
        ns2dot(self.namespace, outPathDot, gvtool="dot", format="pdf")


    def test0(self):
        "Test tuple with constant integers inside."
        
        self.outPathDot = "MultiTests.test0.dot"

        aTuple = (11, 22)
        self.namespace = {"aTuple": aTuple}
        nodes, edges = pyrels2dot.ns2dot(self.namespace, debug=False)
        nodes, edges = filterIDs(nodes, edges)
        
        tid = pyrels2dot.typeID
        expNodes = map(tid, (aTuple, aTuple[0], aTuple[1]))
        expEdges = [
            (tid(aTuple)+":0", tid(aTuple[0])),
            (tid(aTuple)+":1", tid(aTuple[1])),
        ]

        self.assert_(set(expNodes) < set(nodes))
        self.assert_(set(expEdges) < set(edges))


    def test1(self):
        "Test tuple with nested tuple with constant integers inside."
        
        self.outPathDot = "MultiTests.test1.dot"

        aTuple = (11, (22, 33))
        self.namespace = {"aTuple": aTuple}
        nodes, edges = pyrels2dot.ns2dot(self.namespace, debug=False)
        nodes, edges = filterIDs(nodes, edges)
        
        tid = pyrels2dot.typeID
        expNodes = map(tid, (aTuple, aTuple[0], aTuple[1], aTuple[1][0], aTuple[1][1]))
        expEdges = [
            (tid(aTuple)+":0", tid(aTuple[0])),
            (tid(aTuple)+":1", tid(aTuple[1])),
            (tid(aTuple[1])+":0", tid(aTuple[1][0])),
            (tid(aTuple[1])+":1", tid(aTuple[1][1])),
        ]

        self.assert_(set(expNodes) < set(nodes))
        self.assert_(set(expEdges) < set(edges))


    def test2(self):
        "Test tuple with constant integers inside, one named seperately."
        
        self.outPathDot = "MultiTests.test2.dot"

        anInt = 22
        aTuple = (11, anInt)
        self.namespace = {"aTuple": aTuple, "anInt": anInt}
        nodes, edges = pyrels2dot.ns2dot(self.namespace, debug=False)
        nodes, edges = filterIDs(nodes, edges)
        
        tid = pyrels2dot.typeID
        expNodes = map(tid, (aTuple, aTuple[0], aTuple[1]))
        expEdges = [
            (tid(aTuple)+":0", tid(aTuple[0])),
            (tid(aTuple)+":1", tid(aTuple[1])),
        ]

        self.assert_(set(expNodes) < set(nodes))
        self.assert_(set(expEdges) < set(edges))


    def test3(self):
        "Test dict with constant integers inside."
        
        self.outPathDot = "MultiTests.test3.dot"

        aDict = {1:True}
        self.namespace = {"aDict": aDict}
        nodes, edges = pyrels2dot.ns2dot(self.namespace, debug=False)
        nodes, edges = filterIDs(nodes, edges)
        
        tid = pyrels2dot.typeID
        expNodes = map(tid, (aDict, 1, aDict[1]))
        expEdges = [
            (tid(aDict)+":k0", tid(1)),
            (tid(aDict)+":v0", tid(aDict[1])),
        ]

        self.assert_(set(expNodes) < set(nodes))
        self.assert_(set(expEdges) < set(edges))


    def test4(self):
        "Test multiple None values."
        
        self.outPathDot = "MultiTests.test4.dot"

        none1 = None
        none2 = None
        aList = [None]
        aTuple = (None, None)
        aDict = {None:None}
        self.namespace = {
            "aList": aList, "aTuple": aTuple, "aDict": aDict, 
            "none1": none1, "none2": none2, 
        }
        nodes, edges = pyrels2dot.ns2dot(self.namespace, debug=False)
        nodes, edges = filterIDs(nodes, edges)
        
        tid = pyrels2dot.typeID
        expNodes = tid(None)
        expEdges = [
            # (tid(aDict)+":k0", tid(1)),
            # (tid(aDict)+":v0", tid(aDict[1])),
        ]

        # self.assert_(set(expNodes) < set(nodes))
        # self.assert_(set(expEdges) < set(edges))


if __name__ == "__main__":
    unittest.main()
    