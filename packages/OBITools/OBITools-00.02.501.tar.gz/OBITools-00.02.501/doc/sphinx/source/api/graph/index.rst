Graph representation
====================


.. toctree::
   :maxdepth: 2
   
   dag
   unrooted
   algorithms/index
   layout/index
   
.. automodule:: obitools.graph

Classes
^^^^^^^

Basic graph
...........
    
    .. autoclass:: Graph
        :members:

Directed graph
..............
    
    .. autoclass:: DiGraph
        :members:

Undirected graph
................
    
    .. autoclass:: UndirectedGraph
        :members:

The nodes or vertice of a graph
...............................
    
    .. autoclass:: Node
        :members:

The edges of a graph
....................
    
    .. autoclass:: Edge
        :members:
        
The Indexer utility class
.........................

    .. autoclass:: Indexer
        :members:
        
        .. automethod:: __getitem__
        .. automethod:: __equal__
