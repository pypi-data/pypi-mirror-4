#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
from random import random as random_f
from time import sleep

class Slow(object):
    def __init__(self, secs=None, random=None, debug=False):
        self.debug=debug
        if secs:
            secs=float(secs)
            self.dwell=lambda : secs
        else:
            rand_spec=random
            rand_spec_doc="""
                "scale:offset"
                scale
                (scale,offset)
            """
            if isinstance(rand_spec, basestring):
                scale,offset=map(float,rand_spec.split(':'))
            elif isinstance(rand_spec, (list,tuple)):
                scale,offset=rand_spec
            elif isinstance(rand_spec, (int,float)):
                scale,offset=rand_spec,0
            else:
                raise RuntimeError("invalid random sleep specification. 'random' must be one of:\n" \
                                       + rand_spec_doc)
            self.dwell=lambda : scale*random_f()+offset

    def sleep(self):
        secs=self.dwell()
        if self.debug:
            print >>sys.stderr, 'sleeping:', secs
        sleep(secs)
    def slowly(self, arg):
        self.sleep()
        return arg
