#!/usr/bin/env python

"Basic test cases for pyrels, mostly with individual Python objects."


import os, sys, decimal, re, unittest

sys.path.insert(0, "../src")

from pyrels import pyrels2dot


# sample code to be used in the tests below

def foo():
    return
    
    
class Klass():
    def method(self):
        pass
    

# real tests
    
class BasicTests(unittest.TestCase):
    """Generate namespaces and convert them into DOT files.
    
    For conveniance the DOT files are also converted to PDF.
    """

    outputDir = "output/"

    def test(self):
        "Test individual objects."
        
        ns2dot = pyrels2dot.namespace2dot
        namespaces = [
            {"aNone": None},
            {"aBool": True},
            {"anInt": 11},
            {"anOct": 0123},
            {"aHex": 0x123},
            {"aFloat": 3.14},
            {"aComplex": 3+4j},
            {"aLong": 10000000L},
            {"aStr": "myString"},
            {"anUnicodeStr": u"myUnicodeString"},
            {"aDecimal": decimal.Decimal("2.0")},

            {"anEmptyList": []},
            {"anOneElementList": [1]},
            {"aList": [1, 2, 3]},
            {"anEmptyTuple": tuple([])},
            {"anOneElementTuple": (1,)},
            {"aTuple": (1, 2, 3)},
            {"anEmptyDict": {}},
            {"aDict": {2: 4}},
            {"aSet": set([1,2,3])},
            {"aFrozenSet": frozenset([1,2,3])},

            {"anXrange": xrange(1, 10, 2)},
            {"aSlice": slice(0, 10, 2)},
            {"anEllipsis": Ellipsis},

            {"aFile": open(__file__, "r")},

            {"aListIterator": iter([])},
            {"aTupleIterator": iter((1,))},
            {"aDictKeyIterator": iter({})},

            {"aFunction": foo},
            {"aBuiltinFunction": len},
            {"aModule": os},
            {"aClass": Klass},
            {"aMethod": Klass.method},
            {"anInstance": Klass()},

            {"anExecption": IndexError},
            {"aRegExPat": re.compile("a+")},

            {"aGenerator": (x for x in [1, 2, 3])},
            {"aCode": foo.func_code},

        ]
        namespaces2 = [
        ]
        
        # BufferType, BuiltinMethodType, DictProxyType, FrameType, GetSetDescriptorType, LambdaType, MemberDescriptorType, NotImplementedType, ObjectType, StringTypes, TracebackType, TypeType, UnboundMethodType
        
        for ns in namespaces:
            outPathDot = "BasicTests.test.%s.dot" % ns.keys()[0]
            outPathDot = os.path.join(self.outputDir, outPathDot)
            ns2dot(ns, outPathDot, gvtool="dot", format="pdf")
    

if __name__ == "__main__":
    unittest.main()
    