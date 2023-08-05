from obitools.graph.dag import DAG,DAGNode

class RootedTree(DAG):
    
    def addEdge(self,parent=None,node=None,indexp=None,index=None,**data):
        indexp=self.addNode(parent, indexp)
        index =self.addNode(node  , index)
        
        assert index not in self._parents or indexp in self._parents[index], \
                'Child node cannot have more than one parent node'
            
        return DAG.addEdge(self,indexp=indexp,index=index,**data)   

    def getNode(self,node=None,index=None):
        if index is None:
            index = self._index.getIndex(node, True)
        return RootedTreeNode(index,self)
    

    
class RootedTreeNode(DAGNode):

    def subTreeSize(self):
        n=1
        for subnode in self:
            n+=subnode.subTreeSize()
        return n
    
    def subTreeLeaves(self):
        if not self:
            return 1
        n=0
        for subnode in self:
            n+=subnode.subTreeLeaves()
        return n
    
                
def nodeWriter(node,deep=0,label=None,distance="distance", bootstrap="bootstrap",cartoon=None,collapse=None):

    ks = node.keys()

    
    if label is None:
        name=node.label
    elif callable(label):
        name=label(node)
    elif isinstance(label, str) and label in node:
        name=node[label]
        ks.remove(label)
    else:
        name=''
        
    if distance in node:
        dist=':%6.5f' % node[distance]
        ks.remove(distance)
    else:
        dist=''
                
    ks = ["%s=%s" % (k,node[k]) for k in ks]
    
    if cartoon is not None and cartoon(node):
        ks.append("!cartoon={%d,0.0}" % node.subTreeLeaves())
     
    if collapse is not None and collapse(node):
        ks.append('!collapse={"collapsed",0.0}')
    
    if ks:
        ks="[&"+",".join(ks)+"]"
    else:
        ks=''
        
               
    nodeseparator = ',\n' + ' ' * (deep+1)     
        
    subnodes = nodeseparator.join([nodeWriter(x, deep+1,label,distance,bootstrap,cartoon=cartoon,collapse=collapse) 
                                   for x in node])
    if subnodes:
        subnodes='(\n' + ' ' * (deep+1) + subnodes + '\n' + ' ' * deep + ')'
        
    return '%s"%s"%s%s' % (subnodes,name,ks,dist)


def nexusFormat(tree,startnode=None,label=None,blocks="",cartoon=None,collapse=None):
    head="#NEXUS\n"
    
    tx = []
    
    for n in tree:
        if label is None:
            name=n.label
        elif callable(label):
            name=label(n)
        elif isinstance(label, str) and label in n:
            name=n[label]
        else:
            name=''
            
        if name:
            tx.append('"%s"' % name)

    taxa = "begin taxa;\n\tdimensions ntax=%d;\n\ttaxlabels\n\t" % len(tx)
            
    taxa+="\n\t".join(tx)

    taxa+="\n;\nend;\n\n"
    
    

    if startnode is not None:
        roots =[startnode]
    else:
        roots = tree.getRoots()
    trees = nodeWriter(roots[0],0,label,cartoon=cartoon,collapse=collapse)
    trees = "begin trees;\n\ttree tree_1 = [&R] "+ trees +";\nend;\n\n"
    return head+taxa+trees+"\n\n"+blocks+"\n"
