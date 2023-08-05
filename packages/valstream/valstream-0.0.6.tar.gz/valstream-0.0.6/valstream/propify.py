#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""dictionay access via property
"""

def wrap_val(val):

    if isinstance(val, dict):
        return Propify(val)
    elif isinstance(val, list):
        return map(Propify, val)
    elif isinstance(val, tuple):
        return tuple(map(Propify, val))
    else:
        return val


def yodawg(method):
    """yo dawg, I herd you like property so I put a prop in your prop
    so you can Propify while you Propify.
    """
    def wrapped(instance, *args, **kw):
        return wrap_val(method(instance, *args, **kw))
    return wrapped

class Propify(object):

    def __init__(self, d):
        self.d=d

    def __repr__(self):
        return "Propify(%s)" % repr(self.d)

    @yodawg
    def __getslice__(self, i, j):
        return self.d.__getslice__(i, j)

    @yodawg
    def __getitem__(self, index):
        return self.d.__getitem__(index)

    @yodawg
    def __getattr__(self, name):

        if self.d.has_key(name):
            val=self.d[name]
        else:
            val=object.__getattribute__(self, name)
        return val

def test():
    assert Propify( { 'foo': { 'bar': 42 } } ).foo.bar==42
    assert Propify( { 'foo': { 'bar': { 'baz': 42 } } } ).foo.bar.baz==42
    assert Propify( [ { 'bar': 42 } ] )[0].bar==42
    assert Propify( ( { 'bar': 42 }, ) )[0].bar==42

if __name__=='__main__':

    test()
