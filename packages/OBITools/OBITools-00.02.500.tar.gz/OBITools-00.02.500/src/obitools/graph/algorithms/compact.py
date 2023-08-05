
def compactGraph(graph,nodeSetIterator):
    compact = graph.newEmpty()
    for ns in nodeSetIterator(graph):
        nlabel = "\n".join([str(graph.getNode(index=x).label) for x in ns])
        compact.addNode(nlabel)
        print 
        print compact
