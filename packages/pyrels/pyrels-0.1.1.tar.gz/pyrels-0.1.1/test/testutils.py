#!/usr/bin/env python

"Utilities for test cases for pyrels"


import re, copy


def sort(seq):
    res = copy.copy(seq)
    res.sort()
    return res
    

def filterIDs(nodes, edges):
    pat = "([\w\d\:]+)"
    nodes = [re.search(pat, n).groups()[0] for n in nodes]
    edges = [tuple(re.findall(pat, e)[:2]) for e in edges]
    return nodes, edges
    