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
    >>> import networkx as nx
    >>> G = nx.path_graph(5)
    >>> for path in nx.all_simple_paths(G, source=0, target=4):
    ...    print(path)
    [0, 1, 2, 3, 4]
    >>> G = nx.Graph()
    >>> G.add_path([1,2,3])
    >>> G.add_path([1,20,30])
    >>> print(list(all_simple_paths(G,1,3)))
    [[1, 2, 3]]

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
    if source not in G:
        raise nx.NetworkXError('source node %s not in graph'%source)
    if target not in G:
        raise nx.NetworkXError('target node %s not in graph'%source)
    if cutoff is None:
        cutoff = len(G)-1
    if G.is_multigraph():
        return _all_simple_paths_multigraph(G, source, target, cutoff=cutoff)
    else:
        return _all_simple_paths_graph(G, source, target, cutoff=cutoff)


def _all_simple_paths_graph(G, source, target, cutoff=None):
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


def all_simple_paths_edges(G, source, target, cutoff=None):
    if source not in G:
        raise nx.NetworkXError('source node %s not in graph'%source)
    if target not in G:
        raise nx.NetworkXError('target node %s not in graph'%source)
    if cutoff is None:
        cutoff = len(G)-1
    if G.is_multigraph():
        def edge_data(G,u,v,i=0):
            return (u,v,G[u][v][i])
    else:
        def edge_data(G,u,v,i=0):
            return (u,v,G[u][v])
    #
    for path in _all_simple_paths_graph(G,source,target,cutoff=cutoff):
        edges = zip(path[:-1],path[1:])
        N = []
        for u,v in edges:
            n = len(G[u][v])
            N += [n]
        I = [0 for n in N]
        idx = [i for i in reversed(range(len(I)))]
        while True:
            path_edges = []
            for i,(u,v) in enumerate(edges):
                path_edges += [edge_data(G,u,v,I[i])]
            yield path_edges
            for i in idx:
                I[i] = (I[i] + 1) % N[i]
                if I[i] != 0:
                    break
            if i == 0 and I[0] == 0:
                break

def all_circular_paths_edges(G, cutoff=None):
    from networkx import simple_cycles
    if cutoff is None:
        cutoff = len(G)-1
    if G.is_multigraph():
        def edge_data(G,u,v,i=0):
            return (u,v,G[u][v][i])
    else:
        def edge_data(G,u,v,i=0):
            return (u,v,G[u][v])
    #
    for path in simple_cycles(G):
        edges = zip(path[:-1],path[1:])
        N = []
        for u,v in edges:
            n = len(G[u][v])
            N += [n]
        I = [0 for n in N]
        idx = [i for i in reversed(range(len(I)))]
        while True:
            path_edges = []
            for i,(u,v) in enumerate(edges):
                path_edges += [edge_data(G,u,v,I[i])]
            yield path_edges
            for i in idx:
                I[i] = (I[i] + 1) % N[i]
                if I[i] != 0:
                    break
            if i == 0 and I[0] == 0:
                break
