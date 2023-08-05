#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" sql --> row dicts
"""
import sys,os
from pprint import pprint
import json
from urlparse import urlparse
import datetime

# xxx do this once and for all.
class CustomJsonEncoder(json.JSONEncoder):

    def default(self, obj):

        if isinstance(obj, (datetime.datetime, datetime.date) ):
            return str(obj)

        return json.JSONEncoder.default(self, obj)

#json.dumps(row, cls=CustomJsonEncoder)

# dbd module loaders
def dbd_mysql():
    import MySQLdb
    return MySQLdb

this_module=locals()

# xx util
def unstr(x):
    """convert raw string to unicode.
    if not a str, just return it.
    Ideally, deocoding should happen at the point the string enters the system 
    with charset specified.
    """
    
    if not isinstance(x, str):
        return x

    # convert raw string to unicode.
    try:
        return x.decode('utf-8')
    except UnicodeDecodeError:
        return x.decode('iso-8859-1')
    except UnicodeDecodeError:
        raise

def main():

    import baker

    @baker.command
    def query(db_url):
        """read sql from stin. spew row dicts.
        url: jdbc style db url like: mysql://user:password@host[:port]/database?prop=val&...
        """

        u=urlparse(db_url)
        host,user,password,dbname=u.hostname,u.username,u.password,u.path.lstrip('/')

        dbd_name='dbd_'+u.scheme.lower()
        dbd_module=this_module[dbd_name]()

        db = dbd_module.connect(host, user, password, dbname)
        cur = db.cursor()
        cols = None

        for line in sys.stdin.readlines():
            sql,vals_json=(line.strip().split('\t')+[None])[:2]
            try:
                vals=None if vals_json is None else json.loads(vals_json) 
            except ValueError, e:
                e.args+=(vals_json)
                raise
            cur.execute(sql, vals)
            if not cols:
                cols=[ d[0] for d in cur.description ]
            for row in cur.fetchall():
                # decode raw str as db.character_set_name()
                normalized=[ db.string_decoder(v) if isinstance(v,str) else v for v in row ]
                print json.dumps(dict(zip(cols,normalized)), cls=CustomJsonEncoder)
                sys.stdout.flush()

        db.close()

    baker.run()

        
