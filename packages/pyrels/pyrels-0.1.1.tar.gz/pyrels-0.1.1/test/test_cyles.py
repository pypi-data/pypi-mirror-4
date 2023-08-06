#!/usr/bin/env python

"Some test cases for pyrels with cycles."


import os, sys, unittest, re

sys.path.insert(0, "../src")

from pyrels import pyrels2dot
from testutils import sort, filterIDs


class CycleTests(unittest.TestCase):
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
        "Test tuple with cycle."
        
        aList = [11, 22]
        aList.append(aList)
        self.namespace = {"aList": aList}
        nodes, edges = pyrels2dot.ns2dot(self.namespace, debug=False)
        nodes, edges = filterIDs(nodes, edges)
        
        tid = pyrels2dot.typeID
        expNodes = map(tid, (aList, aList[0], aList[1]))
        expEdges = [
            (tid(aList)+":0", tid(aList[0])),
            (tid(aList)+":1", tid(aList[1])),
        ]

        self.assert_(set(expNodes) < set(nodes))
        self.assert_(set(expEdges) < set(edges))

        self.outPathDot = "CycleTests.test0.dot"


if __name__ == "__main__":
    unittest.main()
    