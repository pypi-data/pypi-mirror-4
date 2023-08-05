#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
import json
import io

def select(fields):
    """select fields from stream"""

    if isinstance(fields, basestring):
        fields=fields.split(',')
    assert isinstance(fields, (list,tuple))

    for line in sys.stdin.readlines():
        data=json.loads(line)
        print json.dumps([data.get(f) for f in fields])

def expand():
    """pretty print singleline jsons"""
    for line in sys.stdin.readlines():
        data=json.loads(line)
        print json.dumps(data, indent=4)

def as_tsv():
    """convert from jsons, which are lists, to tsv."""
    for line in sys.stdin.readlines():
        data=json.loads(line)
        assert isinstance(data, list)
        print "\t".join([ unicode(c).encode('utf8') for c in data ])

def keep(field):
    """grep by attr"""
    for line in sys.stdin.readlines():
        data=json.loads(line)
        if data.get(field):
            print json.dumps(data)

def flatten(arg=None):
    """flatten paths stream to json stream"""
    for path in sys.stdin.readlines():
        print json.dumps(json.loads(file(path.strip()).read()))

def select(selector):
    """select nodes from json stream"""
    from jsonpath import jsonpath
    for val in io.read_jsons():
        print json.dumps(jsonpath(val, selector))

def register_commands(baker=None):

    if not baker:
        import baker

    baker.command(as_tsv, 'as_tsv')
    baker.command(expand, 'expand')
    baker.command(expand, 'pretty')
    baker.command(flatten, 'flatten')
    baker.command(select, 'select')

    return baker

def main():
    
    register_commands().run()
