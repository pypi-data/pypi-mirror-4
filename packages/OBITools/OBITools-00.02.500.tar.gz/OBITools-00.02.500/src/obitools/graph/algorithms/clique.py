import time
import sys



_maxsize=0
_solution=0
_notbound=0
_sizebound=0
_lastyield=0
_maxclique=None

def cliqueIterator(graph,minsize=1,node=None,timeout=None):
    global _maxsize,_solution,_notbound,_sizebound,_lastyield
    _maxsize=0
    _solution=0
    _notbound=0
    _sizebound=0
    starttime = time.time()  
    
    if node:
        node = graph.getNode(node)
        index = node.index
        clique= set([index])
        candidates= set(graph.neighbourIndexSet(index=index))
    else:
        clique=set()
        candidates = set(x.index for x in graph)
        
    
#    candidates = set(x for x in candidates
#                     if len(graph.neighbourIndexSet(index=x) & candidates) >= (minsize - 1))
            
    _lastyield=time.time()  
    for c in _cliqueIterator(graph,clique,candidates,set(),minsize,start=starttime,timeout=timeout):
        yield c




        
def _cliqueIterator(graph,clique,candidates,notlist,minsize=0,start=None,timeout=None):
    global _maxsize,_maxclique,_solution,_notbound,_sizebound,_lastyield

                            # Speed indicator
    lclique     = len(clique)
    lcandidates = len(candidates)
    notmin = lcandidates
    notfix = None
    
    for n in notlist:
        nnc = candidates - graph.neighbourIndexSet(index=n) 
        nc = len(nnc)
        if nc < notmin:
            notmin=nc
            notfix=n
            notfixneib = nnc
                
    if lclique > _maxsize or not _solution % 1000 :   
        if start is not None:
            top   = time.time()
            delta = top - start
            if delta==0:
                delta=1e-6
            speed = _solution / delta
            start = top
        else:
            speed = 0
        print >>sys.stderr,"\rCandidates : %-5d Maximum clique size : %-5d Solutions explored : %10d   speed = %5.2f solutions/sec  sizebound=%10d notbound=%10d          " % (lcandidates,_maxsize,_solution,speed,_sizebound,_notbound),
        sys.stderr.flush()
        if lclique > _maxsize:
            _maxsize=lclique

#   print >>sys.stderr,'koukou'        

    timer = time.time() - _lastyield
    
    if not candidates and not notlist:
        if lclique==_maxsize:
            _maxclique=set(clique)
        if lclique >= minsize:
            yield set(clique)
        if timeout is not None and timer > timeout and _maxclique is not None:
            yield _maxclique
            _maxclique=None
        
    else:                        
        while notmin and candidates and ((lclique + len(candidates)) >= minsize or (timeout is not None and timer > timeout)):
                    # count explored solution
            _solution+=1
            
            if notfix is None:
                nextcandidate = candidates.pop()
            else:
                nextcandidate = notfixneib.pop()
                candidates.remove(nextcandidate)
                
            clique.add(nextcandidate)     

            neighbours = graph.neighbourIndexSet(index=nextcandidate)   

            nextcandidates = candidates & neighbours
            nextnot        = notlist    & neighbours
            
            nnc = candidates - neighbours
            lnnc=len(nnc)
            
            for c in _cliqueIterator(graph, 
                                     set(clique), 
                                     nextcandidates,
                                     nextnot,
                                     minsize,
                                     start,
                                     timeout=timeout):
                yield c
    
                        
            clique.remove(nextcandidate)
            
            notmin-=1
            
            if lnnc < notmin:
                notmin = lnnc
                notfix = nextcandidate
                notfixneib = nnc
                            
            if notmin==0:
                _notbound+=1
                
            notlist.add(nextcandidate)
        else:
            if (lclique + len(candidates)) < minsize:
                _sizebound+=1

