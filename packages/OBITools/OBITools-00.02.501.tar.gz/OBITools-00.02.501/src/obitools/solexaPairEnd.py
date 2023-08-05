#!/usr/local/bin/python
'''
Created on 30 dec. 2009

@author: coissac
'''

from obitools.options import getOptionManager
from obitools.fastq import fastqSolexaIterator, formatFastq
from obitools.align import QSolexaReverseAssemble
from obitools.align import QSolexaRightReverseAssemble
from obitools.tools._solexapairend import buildConsensus

from itertools import chain

def addSolexaPairEndOptions(optionManager):
    optionManager.add_option('-r','--reverse-reads',
                             action="store", dest="reverse",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="Filename containing reverse solexa reads "
                            )
    

def cutDirectReverse(entries):
    first = []
    
    for i in xrange(10):
        first.append(entries.next())
        
    lens = [len(x) for x in first]
    clen = {}
    for i in lens:
        clen[i]=clen.get(i,0)+1
    freq = max(clen.values())
    freq = [k for k in clen if clen[k]==freq]
    assert len(freq)==1,"To many sequence length"
    freq = freq[0]
    assert freq % 2 == 0, ""
    lread = freq/2
    
    seqs = chain(first,entries)
    
    for s in seqs:
        d = s[0:lread]
        r = s[lread:]
        yield(d,r)
    
def seqPairs(direct,reverse):
    for d in direct:
        r = reverse.next()
        yield(d,r)

def checkAlignOk(ali):
    #print not (ali[0][0]=='-' or ali[1][len(ali[1])-1]=='-')
    return not (ali[0][0]=='-' or ali[1][len(ali[1])-1]=='-')
    

        
def buildAlignment(sequences):
    la = QSolexaReverseAssemble()
    ra = QSolexaRightReverseAssemble()
    
    for d,r in sequences:
        la.seqA=d 
        la.seqB=r 
        ali=la()
        ali.direction='left'
        if not checkAlignOk(ali):
#            print >>sys.stderr,"-> bad : -------------------------"
#            print >>sys.stderr,ali
#            print >>sys.stderr,"----------------------------------"
            ra.seqA=d 
            ra.seqB=r
            ali=ra()
            ali.direction='right'
#            print >>sys.stderr,ali
#            print >>sys.stderr,"----------------------------------"
        yield ali
        
        
    
    
if __name__ == '__main__':
    optionParser = getOptionManager([addSolexaPairEndOptions],
                                    entryIterator=fastqSolexaIterator
                                    )
    
    (options, direct) = optionParser()
    
    if options.reverse is None:
        sequences=cutDirectReverse(direct)
    else:
        reverse = fastqSolexaIterator(options.reverse)
        sequences=seqPairs(direct,reverse)
    
    for ali in buildAlignment(sequences):
        consensus = buildConsensus(ali)
        print formatFastq(consensus)
        
        

