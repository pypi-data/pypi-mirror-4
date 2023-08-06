# -*- coding: utf-8 -*-
#    Copyright (C) 2012 by
#    Sergio Nery Simoes <sergionery@gmail.com>
#    All rights reserved.
#    BSD license (see second license in LICENSE.txt).

import networkx as nx
__author__ = """\n""".join(['Sérgio Nery Simões <sergionery@gmail.com>',
                             'Aric Hagberg <aric.hagberg@gmail.com>'])
__all__ = ['all_simple_paths']

def all_simple_paths(G, source, target, cutoff=None):
    """Generate all simple paths in the graph G from source to target.

    A simple path is a path with no repeated nodes.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    target : node
       Ending node for path

    cutoff : integer, optional
        Depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    path_generator: generator
       A generator that produces lists of simple paths.  If there are no paths
       between the source and target within the given cutoff the generator
       produces no output.

    Examples
    --------
    >>> G = nx.complete_graph(4)
    >>> for path in nx.all_simple_paths(G, source=0, target=3):
    ...     print(path)
    ...
    [0, 1, 2, 3]
    [0, 1, 3]
    [0, 2, 1, 3]
    [0, 2, 3]
    [0, 3]
    >>> paths = nx.all_simple_paths(G, source=0, target=3, cutoff=2)
    >>> print(list(paths))
    [[0, 1, 3], [0, 2, 3], [0, 3]]

    Notes
    -----
    This algorithm uses a modified depth-first search to generate the
    paths [1]_.  A single path can be found in `O(V+E)` time but the
    number of simple paths in a graph can be very large, e.g. `O(n!)` in
    the complete graph of order n.

    References
    ----------
    .. [1] R. Sedgewick, "Algorithms in C, Part 5: Graph Algorithms",
       Addison Wesley Professional, 3rd ed., 2001.

    See Also
    --------
    shortest_path
    """
    if G.is_multigraph():
        return _all_simple_paths_multigraph(G, source, target, cutoff=cutoff)
    else:
        return _all_simple_paths_graph(G, source, target, cutoff=cutoff)


def _all_simple_paths_graph(G, source, target, cutoff=None):
    if source not in G:
        raise nx.NetworkXError('source node %s not in graph'%source)
    if target not in G:
        raise nx.NetworkXError('target node %s not in graph'%source)
    if cutoff is None:
        cutoff = len(G)-1
    #
    if cutoff < 1:
        return
    visited = [source]
    stack = [iter(G[source])]
    while stack:
        children = stack[-1]
        child = next(children, None)
        if child is None:
            stack.pop()
            visited.pop()
        elif len(visited) < cutoff:
            if child == target:
                yield visited + [target]
            elif child not in visited:
                visited.append(child)
                stack.append(iter(G[child]))
        else: #len(visited) == cutoff:
            if child == target or target in children:
                yield visited + [target]
            stack.pop()
            visited.pop()


def _all_simple_paths_multigraph(G, source, target, cutoff=None):
    for path in _all_simple_paths_graph(G,source,target,cutoff):
        n = 1
        for u,v in zip(path[:-1],path[1:]):
            n *= len(G[u][v])
        for i in range(n):
            yield path


def all_simple_paths_edges(G, source, target, cutoff=None, data=False):
    if data == True:
        edge_data = lambda u,v,n,E,I: (u,v,dict([E[n][I[n]]]))
    else:
        edge_data = lambda u,v,n,E,I: (u,v)
    for path in _all_simple_paths_graph(G,source,target,cutoff=cutoff):
        edges = zip(path[:-1],path[1:])
        E = []  # list: items of each edge
        N = []  # list: number of items of each edge
        for u,v in edges:
            edge_items = G[u][v].items()
            E += [edge_items]
            N += [len(edge_items)]
        I = [0 for n in N]
        idx = [i for i in reversed(range(len(I)))]
        while True:
            path_edges = []
            for n,(u,v) in enumerate(edges):
                path_edges += [edge_data(u,v,n,E,I)]
            yield path_edges
            for i in idx:
                I[i] = (I[i] + 1) % N[i]
                if I[i] != 0:
                    break
            if i == 0 and I[0] == 0:
                break


if __name__=='__main__':
    G = nx.MultiDiGraph()
    G.add_edge('a','b',weight=0.1)
    G.add_edge('a','b',weight=1.0)
    G.add_edge('b','c',weight=0.2)
    G.add_edge('b','c',weight=2.0)
    G.add_edge('c','d',weight=0.3)
    G.add_edge('c','d',weight=3.0)
    G.add_edge('a','c',weight=10,key='77')

    source = 'a'
    target = 'd'

    # MULTIDIGRAPH
    print 'MULTIDIGRAPH (data=False)'
    for path in all_simple_paths_edges(G, source, target):
        print path

    print
    print 'MULTIDIGRAPH (data=True)'
    for path in all_simple_paths_edges(G, source, target, data=True):
        #print path
        total_weight = sum([(I.values()[0]['weight']) for u,v,I in path])
        print total_weight, '\t', path

    print
    # DIGRAPH
    H = nx.DiGraph(G)
    print 'DIGRAPH (data=False)'
    for path in all_simple_paths_edges(H, source, target):
        print path

    print
    print 'DIGRAPH (data=True)'
    for path in all_simple_paths_edges(H, source, target, data=True):
        total_weight = sum([w['weight'] for u,v,w in path])
        print total_weight, '\t', path

