from obitools.graph import DiGraph,Node
from obitools.graph.algorithms.component import componentIterator

class DAG(DiGraph):
    def __init__(self,label='G',indexer=None,nodes=None,edges=None):
        '''
        Directed Graph constructor.

        @param label: Graph name, set to 'G' by default
        @type label: str
        @param indexer: node label indexer
        @type indexer: Indexer instance
        @param nodes: set of nodes to add to the graph
        @type nodes: iterable value
        @param edges: set of edges to add to the graph
        @type edges: iterable value
        '''
        
        self._parents={}
        DiGraph.__init__(self, label, indexer, nodes, edges)
        
    def getNode(self,node=None,index=None):
        if index is None:
            index = self._index.getIndex(node, True)
        return DAGNode(index,self)
    
    def addEdge(self,parent=None,node=None,indexp=None,index=None,**data):
        indexp=self.addNode(parent, indexp)
        index =self.addNode(node  , index)

        pindex = set(n.index 
                     for n in self.getNode(index=indexp).ancestorIterator())
        
        assert index not in pindex,'Child node cannot be a parent node'

        DiGraph.addEdge(self,index1=indexp,index2=index,**data)   

        if index in self._parents:
            self._parents[index].add(indexp)
        else:
            self._parents[index]=set([indexp])   

                                 
        return (indexp,index)
    
    def getRoots(self):
        return [self.getNode(index=cc.pop()).getRoot()
                for cc in componentIterator(self)]
            

        
    
class DAGNode(Node):
    
    def ancestorIterator(self):
        if self.index in self.graph._parents:
            for p in self.graph._parents[self.index]:
                parent = DAGNode(p,self.graph)
                yield parent
                for pnode in parent.ancestorIterator():
                    yield pnode
                    
    def getRoot(self):
        for x in self.ancestorIterator():
            pass
        return x 
                    
    def leavesIterator(self):
        if not self:
            yield self
        for n in self:
            for nn in n.leavesIterator():
                yield nn
                
    def subgraphIterator(self):
        yield self
        for n in self:
            for nn in n.subgraphIterator():
                yield nn
        
