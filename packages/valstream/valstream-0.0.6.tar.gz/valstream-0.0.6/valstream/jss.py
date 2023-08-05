#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" JSS: JSon Stream
"""
import sys,os
import json
import io
import panya
import dynamic

@panya.command
def expand():
    """pretty print singleline jsons"""
    for line in sys.stdin.readlines():
        data=json.loads(line)
        print json.dumps(data, indent=4)

@panya.command
def as_tsv():
    """convert from jsons, which are lists, to tsv."""
    for line in sys.stdin.readlines():
        data=json.loads(line)
        try:
            if isinstance(data, list):
                print "\t".join([ unicode(c).encode('utf8') for c in data ])
            elif isinstance(data, basestring):
                print unicode(data).encode('utf8')
            else:
                raise RuntimeError("inappropriate val ", type(data), data)
        except IOError, e:
            if e.args[0]==32:
                pass            # broken pipe. xx do this generically
            else:
                raise

def keep(field):
    """grep by attr"""
    for line in sys.stdin.readlines():
        data=json.loads(line)
        if data.get(field):
            print json.dumps(data)

@panya.command
def flatten(arg=None):
    """flatten paths stream to json stream"""
    for path in sys.stdin.readlines():
        print json.dumps(json.loads(file(path.strip()).read()))

@panya.command
def unroll(arg=None):
    """unroll (concatenate a sequence values into stream"""
    for val in io.read_jsons():
        if isinstance(val, basestring):
            print json.dumps(val)
        else:
            for item in val:
                print json.dumps(item)

# xxxx collides
def selectx(fields):
    """select fields from stream"""

    if isinstance(fields, basestring):
        fields=fields.split(',')
    assert isinstance(fields, (list,tuple))

    for line in sys.stdin.readlines():
        data=json.loads(line)
        print json.dumps([data.get(f) for f in fields])

@panya.command
def select1(selector):
    """select nodes from json stream using jsonpath.
    http://goessner.net/articles/JsonPath/
    """
    from jsonpath import jsonpath
    for val in io.read_jsons():
        print json.dumps(jsonpath(val, selector))

def false_to_empty_list(v):
    if v==False:
        return []
    # presumaby jsonpath always returns a list when something is found, 
    # reserving the raw False for nothing found.
    assert isinstance(v, list)  
    return v

@panya.command
def select(*selectors):
    """select nodes from json stream using jsonpath.
    http://goessner.net/articles/JsonPath/
    """
    from jsonpath import jsonpath
    for val in io.read_jsons():
        found=sum([ false_to_empty_list(jsonpath(val, selector)) for selector in selectors],[])
        sys.stdout.write(json.dumps(found)+'\n')
        sys.stdout.flush()

def _eval(vals, code, env):
    """compile code into a function and apply it to the values in the stream.
    val is a dict that provides the execution environment.
    it is extended by the env dict.
    """
    # xx todo: exception handling..

    func=dynamic.function(code)

    for dd in vals:
        assert isinstance(dd, dict)
        # hack: make params available like locals.
        # todo: update the local frame in the function somehow..
        #       another hack http://stackoverflow.com/a/8028785
        frame=dd.copy()
        frame.update(env)
        func.func_globals.update(frame)
        yield func(**frame), dd

def eval_cmd(code, *imports):
    """evaluate python expression in the contexts of json stream.
    usage:
        echo "{ 'foo': { 'bar': 42 } }" | $0 'foo["bar"]==42'             ==>   True
      with imports
        echo "{ 'foo': { 'bar': 42 } }" \
             | $0 'P(foo).bar==42' "from propify import Propify as P"     ==>   True
    """

    for import_statement in imports:
        exec import_statement
    env=locals()

    # TODO: -s switch causes the result to be reflected on the exit status.
    #       -s any: true if any result is true
    #       -s all: true iff all results are true
    for result, data in _eval(io.read_jsons(), code, env):
        # xx how to present the result? echo the input?
        # { 'result':.., 'input':.. }
        # [ result, input ]
        # result \t input
        #print json.dumps([result, data])
        print json.dumps(result)
        
panya.command(eval_cmd, "eval")
