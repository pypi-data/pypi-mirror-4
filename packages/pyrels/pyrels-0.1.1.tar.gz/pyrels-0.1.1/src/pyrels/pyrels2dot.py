#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"A tool for visualizing Python namespaces as GraphViz DOT files."

# TODO:
#   - make proper node class generating DOT description for __str__
#   - handle cyclic datastructures


import re
import sys
import os
from cStringIO import StringIO
from types import *

# make sure we have decimal package
try:
    import decimal
except ImportError:
    raise


from utils import uniq


__version__ = "0.1.1"
__license__ = "GPL 3"
__author__ = "Dinu Gherman"
__date__ = "2013-02-07"


RECURSION_COUNT = 0


class PyName(object):
    def __init__(self, name):
        self.name = name


# helpers

def typeID(obj):
    "Return type name from description returned by type() plus obj ID."
    
    # e.g. typeID(12) -> "int123456"
    
    if obj is None:
        return "none"
    typ = re.search("'(.*)'", str(type(obj))).groups()[0]
    typ = typ.replace(".", "_")
    typ = typ.replace("-", "_")
    if type(obj) == BooleanType:
        return typ
    else:
        return "%s%d" % (typ, id(obj))


def addObject(ns, name, obj, nodes, edges, debug=False):
    "Add objects (recursively) to a list of nodes and a list of edges."
    
    global RECURSION_COUNT
    RECURSION_COUNT += 1
    if RECURSION_COUNT > 1000:
        return nodes, edges

    refString = ""
    compositionString = ""
    
    if debug:
        print "handling name '%s'" % name

    typ = re.search("'(.*)'", str(type(obj))).groups()[0]
    ID = typeID(obj)
    # if "." in typ or "-" in typ:
    #    ID = '"%s"' % ID
    objType = type(obj)

    # add node for name
    if name in ns.keys():
        nodes.append((typeID(name).replace("str", "name"), name))
        edges.append((typeID(name).replace("str", "name"), ID))

    # handle objects
    # None
    if objType == NoneType:
        nodes.append((ID, obj))
    # booleans
    elif objType == BooleanType:
        nodes.append((ID, obj))
    # numbers
    elif objType in (IntType, FloatType, ComplexType, LongType):
        nodes.append((ID, obj))
    # strings
    elif objType in (StringType, UnicodeType):
        nodes.append((ID, obj))
    # decimals
    elif isinstance(obj, decimal.Decimal):
        nodes.append((ID, obj))

    # compositions
    # lists and tuples
    elif objType in (ListType, TupleType):
        nodes.append((ID, obj))
        # add list/tuple content from record
        for i in range(len(obj)):
            addObject(ns, None, obj[i], nodes, edges, debug=debug)
    # dictionaries (DictProxyType, DictionaryType?)
    elif objType == DictType:
        # make dict record
        nodes.append((ID, obj))
        # add dict content from dict record
        for i in range(len(obj.keys())):
            k, v = obj.keys()[i], obj[obj.keys()[i]]
            addObject(ns, None, k, nodes, edges, debug=debug)
            addObject(ns, None, v, nodes, edges, debug=debug)
    # sets and frozensets
    elif sys.version_info[:2] >= (2, 4) and type(obj) in (set, frozenset):
        nodes.append((ID, obj))
        # add set content from record
        for ob in obj:
            addObject(ns, None, ob, nodes, edges, debug=debug)

    # xranges
    elif objType == XRangeType:
        nodes.append((ID, obj))
    # slices
    elif objType == type(slice(1,10)):
        nodes.append((ID, obj))
    # ellipsis
    elif objType == EllipsisType:
        nodes.append((ID, obj))

    # files
    elif objType == FileType:
        nodes.append((ID, obj))

    # iterators
    elif objType in map(type, map(iter, [{}, [], (1,)])):
        nodes.append((ID, obj))

    # modules, functions, classes
    elif objType in (FunctionType, BuiltinFunctionType, ModuleType, 
        ClassType, MethodType):
        nodes.append((ID, obj))
    # new style classes
    elif objType == TypeType and hasattr(obj, "__class__"):
        nodes.append((ID, obj))
    # instances
    elif objType in (InstanceType, ObjectType):
        nodes.append((ID, obj))
    # exceptions
    elif objType == TypeType and issubclass(obj, Exception):
        nodes.append((ID, obj))
    # generators
    elif objType == GeneratorType:
        nodes.append((ID, obj))
    # code
    elif objType == CodeType:
        nodes.append((ID, obj))

    # regular expressions
    elif objType == type(re.compile("a+")):
        nodes.append((ID, obj))
    else:
        msg = "cannot handle type:"
        args = tuple([msg] + map(repr, [name, obj, ID, objType]))
        print "%s: name: %s, obj: %s, ID: %s, objType: %s" % args
        
    if False:
        print "nodes:" 
        for n in nodes:
            print n

    return nodes, edges


def toDot(nodes, edges, debug=False):
    "Convert nodes/edges to DOT format."
    
    nameNodeFormat = '''    %s [label="%s", shape="ellipse"];'''
    objNodeFormat = '''    %s [label="%s", shape="box"];'''
    listNodeFormat = '''    %s [label="list: | %s", shape="record"];'''
    tupleNodeFormat = '''    %s [label="tuple: | %s", shape="Mrecord"];'''
    dictNodeFormat = '''    %s [label="%s", shape="record"];'''
    setNodeFormat = '''    %s [label="set: | %s", shape="record"];'''
    fsetNodeFormat = '''    %s [label="frozenset: | %s", shape="record"];'''
    edgeFormat = '''    %s -> %s [label="%s"];'''

    refString = "ref"
    compositionString = ""

    dotNodes, dotEdges = [], []    
    # handle nodes
    for (ID, obj) in nodes:
        if 0 and ID == None:
            # None
            dotNodes.append(objNodeFormat % (ID, ID))
            continue
        
        try:
            prefix = re.search("^([a-zA-Z_]+)", ID).group()
        except:
            print "raising", ID
            raise

        # Python names
        if ID.startswith("name"):
            dotNodes.append(nameNodeFormat % (ID, obj))
        # None
        elif ID.startswith("none"):
            label = str(obj)
            dotNodes.append(objNodeFormat % (ID, label))
        # booleans
        elif ID.startswith("bool"):
            label = "%s: %s" % (ID, str(obj))
            dotNodes.append(objNodeFormat % (ID, label))
        # numbers
        elif prefix in ("int", "float", "complex", "long"):
            label = "%s: %s" % (prefix, obj)
            dotNodes.append(objNodeFormat % (ID, label))
        # strings
        elif prefix in ("str", "unicode"):
            label = "%s: %s" % (prefix, repr(obj))
            dotNodes.append(objNodeFormat % (ID, label))
        # decimals
        elif ID.startswith("decimal_Decimal"):
            label = '%s: \\"%s\\"' % ("decimal", str(obj))
            dotNodes.append(objNodeFormat % (repr(ID).replace("'", '"'), label))

        # compositions
        # lists and tuples
        if prefix in ("list", "tuple"):
            # make list/tuple record
            structLabel = "|".join(["<%d> %d" % (i, i) for i in range(len(obj))])
            lnf, tnf = [listNodeFormat, tupleNodeFormat]
            format = {True:lnf}.get(prefix=="list", tnf)
            dotNodes.append(format % (ID, structLabel))
            # add list/tuple connections from record
            for i in range(len(obj)):
                args = ("%s:%d" % (ID, i), typeID(obj[i]), compositionString)
                if not edgeFormat % args in dotEdges:
                    dotEdges.append(edgeFormat % args)
        # dictionaries (DictProxyType, DictionaryType?)
        elif prefix == "dict":
            # make dict record
            label = "%s: %s" % (prefix, obj)
            items = range(len(obj.items()))
            structEntries = ["{<k%d>|<v%d>}" % (i, i) for i in items]
            structLabel = "|".join(["dict: | {keys|vals}"] + structEntries)
            dotNodes.append(dictNodeFormat % (ID, structLabel))
            # add dict connections from dict record
            for i in range(len(obj.keys())):
                k, v = obj.keys()[i], obj[obj.keys()[i]]
                args = ("%s:k%d" % (ID, i), typeID(k), compositionString)
                dotEdges.append(edgeFormat % args)
                args = ("%s:v%d" % (ID, i), typeID(v), compositionString)
                dotEdges.append(edgeFormat % args)
        # sets and frozensets
        elif prefix in ("set", "frozenset"):
            # make record
            structLabel = "|".join(["<%d> %d" % (i, i) for i in range(len(obj))])
            snf, fsnf = [setNodeFormat, fsetNodeFormat]
            format = {True:snf}.get(type(obj) is set,fsnf)
            dotNodes.append(format % (ID, structLabel))
            # add set connections from record
            for i in range(len(obj)):
                sobj = sorted(obj)
                args = ("%s:%d" % (ID, i), typeID(sobj[i]), compositionString)
                dotEdges.append(edgeFormat % args)

        # xranges
        elif prefix == "xrange":
            label = "%s: %s" % (prefix, str(obj))
            dotNodes.append(objNodeFormat % (ID, label))
        # slices
        elif prefix == "slice":
            label = "%s: %s" % (prefix, str(obj))
            dotNodes.append(objNodeFormat % (ID, label))
        # ellipsis
        elif prefix == "ellipsis":
            label = "%s: %s" % (prefix, id(obj))
            dotNodes.append(objNodeFormat % (ID, label))
        # files
        elif prefix == "file":
            label = "%s: %s" % (prefix, obj.name)
            dotNodes.append(objNodeFormat % (ID, label))
        # iterators
        elif prefix in ("listiterator", "tupleiterator", "dictionary_keyiterator"):
            label = "%s: %s" % (prefix, str(obj))
            dotNodes.append(objNodeFormat % (ID, label))

        # modules, functions, classes
        if prefix in ("function", "builtin_function_or_method", "module", 
            "classobj", "instancemethod"):
            label = "%s: %s" % (prefix, obj.__name__)
            dotNodes.append(objNodeFormat % (ID, label))
        # new style classes
        if prefix == "type" and hasattr(obj, "__class__"):
            label = "%s: %s" % ("new style class", obj.__name__)
            dotNodes.append(objNodeFormat % (ID, label))
        # instances
        elif prefix in ("instance", "__main__"):
            label = "%s (%s): %s" % (prefix, obj.__class__.__name__, id(obj))
            dotNodes.append(objNodeFormat % (ID, label))

        # exceptions
        if prefix == "type" and issubclass(obj, Exception):
            label = "%s: %s" % ("exception", obj.__name__)
            dotNodes.append(objNodeFormat % (ID, label))
        # regular expressions
        elif prefix == "_sre_SRE_Pattern":
            label = "%s: %s" % ("regexPattern", str(obj))
            dotNodes.append(objNodeFormat % (ID, label))

        # generators
        elif prefix == "generator":
            label = "%s: %s" % (prefix, id(obj))
            dotNodes.append(objNodeFormat % (ID, label))
        # code
        elif prefix == "code":
            label = "%s: %s" % (prefix, id(obj))
            dotNodes.append(objNodeFormat % (ID, label))

    # handle edges
    for (start, end) in edges:
        startTag = start
        endTag = end
        dotEdges.append(edgeFormat % (startTag, endTag, refString))

    return dotNodes, dotEdges
    

    if 1:
        pass
    else:
        msg = "cannot handle type:"
        args = tuple([msg] + map(repr, [name, obj, ID, objType]))
        print "%s: name: %s, obj: %s, ID: %s, objType: %s" % args
        
    if False:
        print "nodes:" 
        for n in nodes:
            print n

    return nodes, edges


def ns2dot(ns, skipNames=["__builtins__"], debug=False):
    "Calculate and return nodes and edges for some namespace."
    
    nodes, edges = [], []
    
    for name, obj in ns.items():
        if obj == ns:
            continue
        if name in skipNames:
            continue
        if name in ns.keys():
            addObject(ns, name, obj, nodes, edges, debug=debug)

    # nodes = uniq(nodes)
    # edges = uniq(edges)
    
    # return nodes, edges
    # print nodes
    # print edges
    nodes, edges = toDot(nodes, edges)
    return nodes, edges
    

def namespace2dot_str(ns):
    "Generate GraphViz DOT string for a given namespace." 
    
    nodes, edges = ns2dot(ns)

    # create DOT file
    f = StringIO()
    write = lambda line: f.write("%s\n" % line)
    write("digraph G {")
    write("    overlap=false;")
    # write("    concentrate=true;")
    # write("    nodesep=1.0;")
    write("")
    for n in nodes: 
        write(n)
    write("")
    for e in edges: 
        write(e)
    write("")
    write("}")

    f.seek(0)
    return f.read()


def namespace2dot(ns, path=None, gvtool=None, format="pdf", debug=False):
    "Generate GraphViz DOT file for a given namespace." 
    
    nodes, edges = ns2dot(ns, debug=debug)

    # create DOT file
    if type(path) == str:
        f = open(path, "w")
    else: 
        f = path
    write = lambda line: f.write("%s\n" % line)
    write("digraph G {")
    write("    overlap=false;")
    # write("    concentrate=true;")
    # write("    nodesep=1.0;")
    write("")
    for n in nodes: 
        write(n)
    write("")
    for e in edges: 
        write(e)
    write("")
    write("}")
    if type(path) == str:
        f.close()
    
    # convert resulting DOT file into another format
    if type(gvtool) == str:
        main = os.path.splitext(path)[0]
        args = (gvtool, format, main+"."+format, path)
        cmd = '''%s -T%s -o "%s" "%s"''' % args
        # print "running '%s'" % cmd
        os.popen(cmd)


def _main(ns, path=None, gvtool=None, format="pdf", debug=False):
    "Generate GraphViz DOT file for a given namespace." 

    namespace2dot(ns, path=path, gvtool=gvtool, format=format, debug=debug)


if __name__ == "__main__":
    _main()
