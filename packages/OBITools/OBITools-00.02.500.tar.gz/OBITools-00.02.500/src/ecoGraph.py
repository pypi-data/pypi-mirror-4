from obitools.utils import ColumnFile
from obitools.utils import progressBar
from obitools.graph import Graph
from obitools.graph import selectEdgeAttributeFactory
from obitools.graph.algorithms.component import componentIterator
from obitools.graph.algorithms.compact import compactGraph
from obitools import NucSequence

from obitools.options import getOptionManager

import sys


def addGraphOptions(optionManager):
        
    optionManager.add_option('-d','--ecopcrdb',
                             action="store", dest="db",
                             metavar="<FILENAME>",
                             type="string",
                             help="ecoPCR Database "
                                  "name")
    
def ColIterator(stream):
    return ColumnFile(stream, strip=True, types=(str,str,str,str,
                                                 int,
                                                 float,float,
                                                 float,float,
                                                 float,float,
                                                 int,int,float),
                                                 
                                                  skip="primer_1")
    
def deltaEqual(d,p1,p2):
    if d < 0:
        pn=p1[-d:]
        pp=p2[:d]
    elif d > 0:
        pn=p2[d:]
        pp=p1[:-d]
    else:
        pn=p1
        pp=p2
    return pn==pp

def linkPrimerNode(delta,g,complement=False,**data):
    word={}
    nn = len(g)
    pn = 0

    print >> sys.stderr,"Indexing nodes..."
    progressBar(1, nn, True)
    
    
    for n in g:
        pn+=1
        progressBar(pn, nn)
        for i in xrange(delta+1):
            p = n.label[i:]
            if p in word:
                word[p].add(n.index)
            else:
                word[p]=set([n.index])
            if i:
                p = n.label[:-i]
                if p in word:
                    word[p].add(n.index)
                else:
                    word[p]=set([n.index])
                
    print >> sys.stderr,"\nLook for related primers"
 
    pn = 0
    progressBar(1, nn, True)
    for n in g:
        if complement:
            cp = str(NucSequence('x',n.label).complement()).lower()
        else:
            cp=n.label
        cc=set()
        pn+=1
        progressBar(pn, nn)
        for i in xrange(delta+1):
            p = cp[i:]
            if p in word:
                cc|=word[p]
            if i:
                p = cp[:-i]
                if p in word:
                    cc|=word[p]
        for i in cc:
            if complement or i!=n.index:
                g.addEdge(index1=n.index,index2=i,**data)
            #print >> sys.stderr, g.addEdge(index1=n.index,index2=i,color="red"), " ==> Complement(",n.label,":",cp,g.getNode(index=i).label,")" 

    print >>sys.stderr,""
    
   
def greenComponentIterator(g):
    greenPredicat = selectEdgeAttributeFactory("color", "green")
    return componentIterator(g,edgePredicat=greenPredicat)



if __name__=='__main__':
    
    

    optionParser = getOptionManager([],
                                    entryIterator=ColIterator
                                    )
    
    (options, entries) = optionParser()
    
    G = Graph('primers')
    
    print >>sys.stderr,"Read ecoPrimer result file...",
    
    for amp in entries:
        p1 = amp[1]
        p2 = amp[3]
        count=amp[4]
        family_spe,family_sens = amp[5],amp[6]
        genus_spe,genus_sens = amp[7],amp[8]
        species_spe,species_sens = amp[9],amp[10]
        avg_l=amp[13]
        
        
        G.addEdge(p1, p2, count=count ,
                  species_spe=species_spe,species_sens=species_sens,
                  avg_l=avg_l,
                  color="blue")
        
    print >> sys.stderr,"  %d primers and %d amplifia" % (len(G),G.edgeCount())
    
    
    print >>sys.stderr,"Look for complementary primers..."

    linkPrimerNode(2,G,True,color="red")
    print >> sys.stderr,"Ok"


    
    for C in componentIterator(G):
        sub = G.subgraph(C)

        linkPrimerNode(2, sub,color="green")

        compactGraph(sub, greenComponentIterator)

     
        