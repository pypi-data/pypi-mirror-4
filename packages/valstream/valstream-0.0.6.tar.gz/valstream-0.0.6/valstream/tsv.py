#!/usr/bin/env python
# -*- coding: utf-8 -*-

def tostr(*cols):
    return "\t".join(map(unicode, cols)).encode('utf8')

def spew(*cols):
    """ writes tuples to stdout as TSV"""
    print tostr(*cols)

def permuter(permutation):
    if isinstance(permutation, basestring):
        permutation=map(int,permutation.split(','))
    assert isinstance(permutation, (list,tuple))
    def _permute(*cols):
        return tuple([ cols[i] for i in permutation ])
    return _permute
