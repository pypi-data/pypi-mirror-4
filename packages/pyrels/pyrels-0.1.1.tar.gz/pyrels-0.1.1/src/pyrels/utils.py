#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"Utilities for pyrels."


def uniq(aList):
    "Make all elements in a list unique."
    
    set = {}
    return [set.setdefault(e, e) for e in aList if e not in set]
