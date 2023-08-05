"""
Iterate through the connected components of a graph
---------------------------------------------------

the module :py:mod:`obitools.graph.algorithm.component` provides
two functions to deal with the connected component of a graph
represented as a :py:class:`obitools.graph.Graph` instance.

The whole set of connected component of a graph is a partition of this graph.
So a node cannot belongs to two distinct connected component.

Two nodes are in the same connected component if it exits a path through 
the graph edges linking them.

TODO: THere is certainly a bug with DirectedGraph

"""

def componentIterator(graph,nodePredicat=None,edgePredicat=None):
    '''
    Build an iterator over the connected component of a graph.
    Each connected component returned by the iterator is represented 
    as a `set` of node indices.
    
    :param graph: the graph to partitionne
    :type graph:  :py:class:`obitools.graph.Graph`
    
    :param predicate: a function allowing edge selection. Default value
                      is **None** and indicate that all edges are selected.
    :type predicate:  a function returning a boolean value
                      and accepting one argument of class :py:class:`Node`
                      
    :param predicate: a function allowing node selection. Default value
                      is **None** and indicate that all nodes are selected.
    :type predicate:  a function returning a boolean value
                      and accepting one argument of class :py:class:`Edge`
                      
    :return: an iterator over the connected component set
    :rtype: an iterator over `set` of `int`
    
    .. seealso::
        the :py:meth:`obitools.graph.Graph.componentIndexSet` method
        on which is based this function.
    '''
    seen = set()
    for n in graph.nodeIterator(nodePredicat):
        if n.index not in seen:
            cc=n.componentIndexSet(nodePredicat, edgePredicat)
            yield cc
            seen |= cc
            
def componentCount(graph,nodePredicat=None,edgePredicat=None):
    '''
    Count the connected componnent in a graph.
    
    :param graph: the graph to partitionne
    :type graph:  :py:class:`obitools.graph.Graph`
    
    :param predicate: a function allowing edge selection. Default value
                      is **None** and indicate that all edges are selected.
    :type predicate:  a function returning a boolean value
                      and accepting one argument of class :py:class:`Node`
                      
    :param predicate: a function allowing node selection. Default value
                      is **None** and indicate that all nodes are selected.
    :type predicate:  a function returning a boolean value
                      and accepting one argument of class :py:class:`Edge`
                      
    :return: an iterator over the connected component set
    :rtype: an iterator over `set` of `int`
    
    .. seealso::
        the :py:func:`componentIterator` function
        on which is based this function.
    '''
    n=0
    for c in componentIterator(graph,nodePredicat, edgePredicat):
        n+=1
    return n

 
        