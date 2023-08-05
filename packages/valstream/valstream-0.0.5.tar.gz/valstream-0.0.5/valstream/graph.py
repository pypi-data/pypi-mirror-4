#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io

def dot(name='hoge'):
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

    edges=[[s,d] for s,d in io.read_tsv()]
    nodes=set(sum(edges,[]))

    yield 'digraph %s {' % name

    for node in nodes:
        yield '\t{node} [label="{node}"]'.format(node=node) 

    yield ''

    for s,d in edges:
        yield '\t{s}->{d} [label="{edge_label}"]'.format(s=s, d=d, edge_label=edge_label(s,d))

    yield '}'

def register_commands(baker=None):

    if not baker:
        import baker

    baker.command(dot, 'dot')

    return baker

def main():
    
    register_commands().run()
