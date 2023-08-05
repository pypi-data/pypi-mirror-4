#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
### todo
* replace lengthy pipe with a single point-free composition
    * from this
	| ./ds.py json keep series_id \
	| ./ds.py json select _table \
	| ./ds.py json as_tsv \
    * to
        | ./ds.py json keep('series_id') select('_table') as_tsv
    * or
        | ./ds.py json keep=series_id select=_table as_tsv
    * imp
    inline code or spec gets compiled into point-level funcs and are composed into a 
    stream processor.

"""
import sys,os
import json

def read_tsvs():
    for line in sys.stdin.readlines():
        yield line.strip('\n').split('\t')

####

def json_select(fields):
    """select fields from stream"""

    if isinstance(fields, basestring):
        fields=fields.split(',')
    assert isinstance(fields, (list,tuple))

    for line in sys.stdin.readlines():
        data=json.loads(line)
        print json.dumps([data.get(f) for f in fields])

def json_expand():
    for line in sys.stdin.readlines():
        data=json.loads(line)
        print json.dumps(data, indent=4)

def json_as_tsv():
    """convert from jsons, which are lists, to tsv."""
    for line in sys.stdin.readlines():
        data=json.loads(line)
        assert isinstance(data, list)
        print "\t".join([ unicode(c).encode('utf8') for c in data ])

def json_keep(field):
    """grep by attr"""
    for line in sys.stdin.readlines():
        data=json.loads(line)
        if data.get(field):
            print json.dumps(data)

def graph_edge_to_dot(name='hoge'):
    """generate graphviz dot input from edges expressed as tsv pairs.
foo TAB bar --> 
digraph hoge {
	Foo [label="foo"]
	Bar [label="Bar"]
	Foo->Bar [label="edge"]
}
    """
    for line in _graph_edge_to_dot(name):
        print line

def _graph_edge_to_dot(name, edge_label=lambda s,d: ""):

    edges=[[s,d] for s,d in read_tsvs()]
    nodes=set(sum(edges,[]))

    yield 'digraph %s {' % name

    for node in nodes:
        yield '\t{node} [label="{node}"]'.format(node=node) 

    yield ''

    for s,d in edges:
        yield '\t{s}->{d} [label="{edge_label}"]'.format(s=s, d=d, edge_label=edge_label(s,d))

    yield '}'

dispatch=dict(
    json=dict(select=json_select,
              as_tsv=json_as_tsv,
              expand=json_expand,
              keep=json_keep,
              ),
    graph=dict(edge_to_dot=graph_edge_to_dot,
               ),
)

if __name__=='__main__':

    _,major,minor=sys.argv[:3]
    dispatch[major][minor](*sys.argv[3:])
