#!/usr/local/bin/python

'''
:py:mod:`obiclean` : Clean a set of sequences for PCR/sequencing errors (sequence variants) 
===========================================================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obiclean` is a command that allows to tag sequences either as :
    - ``head`` : there exists sequences in the dataset that are close to this sequence (set by the `-d option`) *but* there exists *no* sequence in the dataset that are
      close to this sequence (set by the `-d option`) *and* that have a *greater* count than this sequence, *the sequence is probably a real sequence and should be kept for 
      further analysis*
    - ``internal`` : there exist *one or more* sequences in the dataset being close to this sequence (set by the `-d option`) and 
      having a *greater* count than this sequence, *the sequence is probably a PCR/sequencing error and should not be kept for further analysis*
    - ``singleton`` : there exist *no* sequence in the dataset being close to this sequence (set by the `-d option`), *the sequence is probably
      a chimera and should not be kept for further analysis*
'''

from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager
from obitools.graph import Graph
from obitools.utils import progressBar
from obitools.align import LCS
from obitools.align import isLCSReachable


import sys
import math


def addCleanOptions(optionManager):
    optionManager.add_option('-d','--distance',
                             action="store", dest="dist",
                             metavar="###",
                             type="int",
                             default=1,
                             help="Maximum numbers of errors between two variant sequences [default: 1]")
    optionManager.add_option('-s','--sample',
                             action="store", dest="sample",
                             metavar="<TAGNAME",
                             type="str",
                             default=None,
                             help="Tag containing sample descriptions")
     
    optionManager.add_option('-r','--ratio',
                             action="store", dest="ratio",
                             metavar="<TAGNAME",
                             type="float",
                             default=1,
                             help="Minimum ratio between counts of two sequences so that the less abundant one is considered as a variant [default: 1, i.e. all less abundant sequences are variant]")
    
    optionManager.add_option('-H','--head',
                             action="store_true", dest="head",
                             default=False,
                             help="Look for head corresponding sequence")
    
def lookforFather(node,sample):
    father=set()
    
    for neighbour in node.neighbourIterator():
        if sample in neighbour['_sample']:
            if neighbour['_sample'][sample] > node['_sample'][sample]:
                gdfather = lookforFather(neighbour, sample)
                father|=gdfather
    if not father:
        father.add(node)
        
    return father

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
    
    optionParser = getOptionManager([addCleanOptions,addInOutputOption], progdoc=__doc__)
    (options, entries) = optionParser()
    
    db = [s for s in entries]
  
    writer = sequenceWriterGenerator(options)
  
    graph = Graph("error",directed=False)
    for s in db:
        if options.sample is None:
            sample = {"XXX":s['count'] if 'count' in s else 1}
        else:
            sample = s[options.sample]
        graph.addNode(s.id,shape='circle',_sequence=s,_sample=sample)
    
    ldb = len(db)    
    digit = int(math.ceil(math.log10(ldb)))
    aligncount = ldb*(ldb+1)/2
    edgecount = 0
    print >>sys.stderr
    
    header = "Alignment  : %%0%dd x %%0%dd -> %%0%dd " % (digit,digit,digit)
    progressBar(1,aligncount,True,"Alignment  : %s x %s -> %s " % ('-'*digit,'-'*digit, '0'*digit))
    pos=1
    aligner = LCS()
    

    for i in xrange(ldb):

        inode = graph[db[i].id]
        aligner.seqA = db[i]
        li = len(db[i])
        
        for j in xrange(i+1,ldb):
            progressBar(pos,aligncount,head=header % (i,j,edgecount))
            pos+=1
            
            lj = len(db[j])
            
            lm = max(li,lj)
            lcsmin = lm - options.dist
            
            if isLCSReachable(db[i],db[j],lcsmin):
                aligner.seqB=db[j]
                ali = aligner()
                llcs=ali.score
                lali = len(ali[0])
                obsdist = lali-llcs
                if obsdist >= 1 and obsdist <= options.dist:
                    jnode = graph[db[j].id]
                    graph.addEdge(inode.label, jnode.label)
                    edgecount+=1               
            
    print >>sys.stderr
    
    ratio = []
    for node in graph.nodeIterator():
        puu=str(node['_sequence'])=='aggggtgtaaagcaccgccaagtcctttgagttttaagctgttgctagtagttctctggcggatagttttgtttgagctaactatctaggtttagggctaa'
        for sample in node['_sample']:
            lratio = []
            for neighbour in node.neighbourIterator():
                if sample in neighbour['_sample'] :
                    if neighbour['_sample'][sample] > node['_sample'][sample]:
                        lratio.append((neighbour['_sample'][sample],node['_sample'][sample]))
            llratio=len(lratio)
            
            for r in lratio:
                ratio.append(r + (llratio,puu))
                        
    rfile = open('ratio.txt','w')
    for r in ratio:
        print >>rfile,"%-8d %-8d %-8d %s"  % r
    rfile.close()
    
    gfile = open('obiclean.dot','w')
    print >>gfile,graph
    gfile.close()
    
    for node in graph.nodeIterator():
        status={}
        fathers={}
        common={}
        for sample in node['_sample']:
            son=False
            father=False
            for neighbour in node.neighbourIterator():
                if sample in neighbour['_sample'] :
                    c = cmp(neighbour['_sample'][sample],node['_sample'][sample])
                    if c > 0:
                        son|=True
                    if c < 0:
                        father|=True
            if father and not son:
                status[sample]='h'
            elif not father and not son:
                status[sample]='s'
            else:
                status[sample]='i'
            
            if options.head:  
                if status[sample]=='i':
                    fathers[sample]=[x['_sequence'].id for x in lookforFather(node, sample)]
                else:
                    fathers[sample]=[node['_sequence'].id]
                
        if options.head:  
            for sa in fathers:
                fathers[sa]=list(set(fathers[sa]))
                for s in fathers[sa]:
                    common[s]=common.get(s,0)+1
            
        i=0
        h=0
        s=0
        o=0
        
        
        for sample in status:
            o+=1
            if   status[sample]=='i':
                i+=1
            elif status[sample]=='s':
                s+=1
            elif status[sample]=='h':
                h+=1
        
        node['_sequence']['clean']=status
        node['_sequence']['head']=h
        node['_sequence']['internal']=i
        node['_sequence']['singleton']=s
        node['_sequence']['occurrence']=o

        if options.head:
            node['_sequence']['father']=fathers
            node['_sequence']['fathers']=common

        writer(node['_sequence'])
                
            
            
            

            
    

