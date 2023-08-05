#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import time
import panya

def ints(start=0):
    n=start
    while True:
        yield n
        n+=1

@panya.command
def read_lines(file=sys.stdin):
    """non-buffered, chomped readlines()"""
    
    while True:
        line=file.readline()
        if not line:
            break
        yield line.strip('\n')

@panya.command
def read_jsons(file=sys.stdin):
    """ """
    for line in read_lines(file):
        try:
            yield json.loads(line)
        except Exception, e:
            print >>sys.stderr, 'json-parse-error:', e, line

@panya.command
def read_tsv(file=sys.stdin):

    for line in read_lines(file):
        yield line.split('\t')

@panya.command
def repeat(n=None):
    """repeat lines read from stdin 
    up to n iterations or forever"""

    max_iterations=int(n) if n else None

    lines=[ line.strip() for line in read_lines(sys.stdin) ]

    for i in ints():

        if max_iterations and i>=max_iterations: 
            break

        for line in lines:
            print line


@panya.command
def slowly(secs, imports=''):
    """echo lines slowly

    usage:
    cat cmds | $0 slowly 3 | sh
    cat urls | $0 slowly '30+random.random()*60' --imports=random | fetch-urls
    """
    # xxx reimplement in slow.Slow
    for mod in filter(None,imports.split(',')):
        locals()[mod]=__import__(mod, fromlist=[None])
    try:
        dwell=float(secs)
    except ValueError:
        dwell=None

    for line in read_lines():
        print line
        sys.stdout.flush()
        if dwell is None:
            time.sleep(eval(secs))
        else:
            time.sleep(dwell)

