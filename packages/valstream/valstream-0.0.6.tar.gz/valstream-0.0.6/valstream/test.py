#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
import json
import jss

for result,data in jss._eval([json.loads("""{ "foo": {"bar": 42} }""")], """foo["bar"]==42""", {}):
    assert result==True
    assert data=={u'foo': {u'bar': 42}}

import propify

for result,data in jss._eval([json.loads("""{ "foo": {"bar": 42} }""")], 
                             """P(foo).bar==42""", 
                             dict(P=propify.Propify)):
    assert result==True
    assert data=={u'foo': {u'bar': 42}}
