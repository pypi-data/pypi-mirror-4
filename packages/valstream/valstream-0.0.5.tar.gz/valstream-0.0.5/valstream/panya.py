#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

class CmdFunc(object):

    def __init__(self, func, name, module, doc):
        self.func=func
        self.name=name
        self.module=module
        self.doc=doc

    def __repr__(self):
        return "%s(%s.%s)" % (self.__class__.__name__, self.module, self.name)

class Panya(object):

    def __init__(self, baker=None):
        self.funcs=[]
        # print >>sys.stderr, 'Panya:', self
        if not baker:
            import baker
        self.baker=baker
    
    def register_command(self, f):
        """deocrate command function, like baker.command"""
        self.funcs.append(CmdFunc(f, f.func_name, f.__module__, f.func_doc))
        return f

    def register(self):
        for cf in self.funcs:
            self.baker.command(cf.func, '.'.join([cf.module.split('.')[-1], cf.name])) 

    def dump(self):
        for f in self.funcs:
            print f

panya=Panya()
command=panya.register_command
