#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
import ast

def function(body):
    """returns a function that executes the body python code"""

    # source
    defun_src="""
def surrogate(**params):    
    return None
"""

    # ast
    defun_ast=ast.parse(defun_src, mode='single')
    body_ast=ast.parse(body, mode='single')

    # surgery

    # allow shorthand where 'return' can be omitted.
    # is the last node an expr? if so, wrap the expr in Return node
    if isinstance(body_ast.body[-1], ast.Expr):
        assert len(defun_ast.body)==1
        return_st=defun_ast.body[0].body[-1]
        return_st.value=body_ast.body[-1].value 
        body_ast.body[-1]=return_st

    # graft the body
    defun_ast.body[0].body=defun_ast.body[0].body[:-1]+body_ast.body

    # compile
    defun_code=compile(defun_ast, '<string>', 'single')

    # extract the function
    locals={}
    eval(defun_code, {}, locals)
    return locals['surrogate']

def test(body, **params):

    print "body:", body

    f=function(body)
    # make the params available as local vars
    f.func_globals.update(params)

    ret=f(**params)
    print 'returned:', ret
    print '-------------------'

if __name__=='__main__':

    cases="""
print 42; return 33
return 42
42
foo
"""
    for case in filter(None, cases.split('\n')):
        test(case, foo=42)
