#!/usr/bin/env python

"""Basic command-line usage for pyrels.

Test with something like:

  test_commandline.py --ns "x=1"
"""

# This needs some refactoring to remove duplication of code in
# the method CommandLineTests.test and the function main...


import os, sys, getopt, unittest

sys.path.insert(0, "../src")

from pyrels import pyrels2dot


class CommandLineTests(unittest.TestCase):
    """Generate namespaces and convert them into DOT files.
    
    For conveniance the DOT files are also converted to PDF.
    """

    outputDir = "output/"

    def test(self):
        "Test commandline invocation."

        shortOpts = ""
        longOpts = "ns= namespace=".split()
        
        sys.argv += ["--ns", "x=42"]
        opts, args = getopt.getopt(sys.argv[1:], shortOpts, longOpts)
        
        locs = {}
    
        for key, val in opts:
            if key in ("--ns",):
                # print "code:", val
                exec val in globals(), locs
        
        ns2dot = pyrels2dot.namespace2dot
        outPathDot = "CommandLineTests.test.dot"
        outPathDot = os.path.join("output", outPathDot)
        ns2dot(locs, outPathDot, gvtool="dot", format="pdf")


def main():
    shortOpts = ""
    longOpts = "ns= namespace=".split()
        
    opts, args = getopt.getopt(sys.argv[1:], shortOpts, longOpts)
    
    locs = {}

    for key, val in opts:
        if key in ("--ns", "--namespace"):
            print "code:", val
            exec val in globals(), locs

    print "namespace:", locs

    ns2dot = pyrels2dot.namespace2dot
    outPathDot = "CommandLineTests.test.dot"
    outPathDot = os.path.join("output", outPathDot)
    ns2dot(locs, outPathDot, gvtool="dot", format="pdf")


if __name__ == "__main__":
    nsIdx = -1
    try:
        nsIdx = sys.argv[1:].index("--ns")
    except:
        try:
            nsIdx = sys.argv[1:].index("--namespace")
        except:
            pass
                
    if nsIdx >= 0:
        print "sys.argv[1:]:", sys.argv[1:]
        code = sys.argv[1:][nsIdx+1]
        main()
    else:
        unittest.main()
