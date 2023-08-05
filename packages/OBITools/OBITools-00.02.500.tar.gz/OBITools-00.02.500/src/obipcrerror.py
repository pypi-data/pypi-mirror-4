#!/usr/local/bin/python
'''
Created on 14 oct. 2010

@author: coissac
'''
from obitools.options import getOptionManager
from obitools.format.options import addInOutputOption
from obitools.align import LCS
from obitools.align import isLCSReachable
from obitools.utils import progressBar
from obitools.graph import Graph
from obitools.graph.algorithms.component import componentIterator

import sys

def addPCRErrorOptions(optionManager):
    optionManager.add_option('-d','--distance',
                             action="store", dest="dist",
                             metavar="###",
                             type="int",
                             default=1,
                             help="Maximum distance between two sequences")
    


def cmpseqcount(s1,s2):
    if 'count' not in s1:
        s1['count']=1
    if 'count' not in s2:
        s2['count']=1
    
    return cmp(s2['count'],s1['count'])

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([addPCRErrorOptions,addInOutputOption])
    (options, entries) = optionParser()
    
    db = [s for s in entries]
    
    graph = Graph("error",directed=True)
    for s in db:
        graph.addNode(s.id,color="blue",mode="s",connection=False,shape='circle')

    
    db.sort(cmp=cmpseqcount)
    
    sdb = len(db)
    
    path={}
    
    aligner = LCS()
    
    seqmax=0
    while (seqmax < sdb and db[seqmax]['count']>1):
        seqmax+=1 
    
    print >>sys.stderr
    edge=0
    connect=0
    head=0
    progressBar(1, seqmax, True, 
                "Aligning sequence egdes=%-6d connection=%-6d head=%-5d" % (edge,connect,head))
    for x in xrange(seqmax-1):
        progressBar(x+1, seqmax, False, 
                    "Aligning sequence egdes=%-6d connection=%-6d head=%-5d" % (edge,connect,head))
        xnode=graph[db[x].id]
        ishead=xnode['mode']=='s'
        if db[x].id not in path:
            lpath=1
            path[db[x].id]=lpath
        else:
            lpath=path[db[x].id]
        lx = len(db[x])
        aligner.seqA=db[x]
        s=x+1
        while (s < sdb and db[x]['count']==db[s]['count']):
            s+=1
        for y in xrange(s,sdb):
            lsmax=max(lx,len(db[y]))
            lcsmin = lsmax - options.dist
            if isLCSReachable(db[x],db[y],lcsmin):
                aligner.seqB=db[y]
                ali = aligner()
                llcs=ali.score
                lali = len(ali[0])
                obsdist = lali-llcs
                if obsdist >= 1 and obsdist <= options.dist:
                    ynode=graph[db[y].id]
                    
                    if ynode['mode']!='s':
                        connect+=1
                        ynode['connection']=True
                        ynode['shape']='square'
                    else:
                        path[db[y].id]=lpath+1
                        
                    ynode['mode']='t'
                    ynode['color']='red'

                    lali = len(ali[0])
                    if obsdist==1:
                        p=0
                        while (p<lali and ali[0][p]==ali[1][p]):
                            p+=1
                        c1 = ali[0][p]
                        c2 = ali[1][p]
                        
                        if c1!='-' and c2!='-':
                            m='s'
                            mt = "%s->%s" % (c1,c2)
                        elif c1=='-':
                            m='i'
                            lh = 1
                            h=p-1
                            while(h > 0 and ali[1][h]==c2):
                                h+=1
                                lh+=1
                            h=p+1
                            while(h < lali and ali[1][h]==c2):
                                h+=1
                                lh+=1
                            mt="%s(%d)" % (c2,lh-1)
                                    
                        else:
                            m='d'
                            lh = 1
                            h=p-1
                            while(h > 0 and ali[0][h]==c1):
                                h+=1
                                lh+=1
                            h=p+1
                            while(h < lali and ali[0][h]==c1):
                                h+=1
                                lh+=1
                            mt="%s(%d)" % (c1,lh)                           
                    else:
                        p='--'
                        m='--'
                        mt='--'
                        
                    if ishead:
                        xnode['mode']='h'
                        xnode['color']='green'
                        xnode['shape']='doublecircle'
                        head+=1
    
                    edge+=1
                    graph.addEdge(xnode.label, ynode.label)
                    print '>',xnode['mode'],db[x].id,db[y].id,db[x]['count'],db[y]['count'],lpath,int(obsdist),p,m,mt
                    print ali
                    