#!/usr/local/bin/python

'''
Created on 30 sept. 2011

@author: fboyer

Used to get the consensus sequence of a nucleotide fasta alignment.

Example:

ali2consensus.py -t 75 myFastaAlignedSequences.fasta

@todo: Check input/output format options to suite with the script objective
'''


from obitools.fasta import fastFastaIterator
from obitools.options import getOptionManager
from obitools.alignment import Alignment, columnIterator
from obitools import NucSequence
from obitools.format.options import sequenceWriterGenerator, addInOutputOption

def addAliOptions(optionManager):
    optionManager.add_option('-t','--threshold',
                             action="store", dest="threshold",
                             metavar="",
                             type="int",
                             default=50,
                             help="Threshold parameter for consensus building")



if __name__=='__main__':
    
    optionParser = getOptionManager([addInOutputOption, addAliOptions],
                                    entryIterator=fastFastaIterator
                                    )
    
    (options, entries) = optionParser()
 
    assert options.threshold>=0 and options.threshold<=100, 'Threshold must belong to [0, 100]'
    threshold = options.threshold/100.
 

    #taken from http://www.dna.affrc.go.jp/misc/MPsrch/InfoIUPAC.html    
    iupacDNA = dict()
    iupacDNA['-'] = ('-',)
    iupacDNA['A'] = ('A',)
    iupacDNA['C'] = ('C',)
    iupacDNA['G'] = ('G',)
    iupacDNA['T'] = ('T',)
    iupacDNA['U'] = ('T',)
    iupacDNA['M'] = ('A', 'C')
    iupacDNA['R'] = ('A','G')
    iupacDNA['W'] = ('A', 'T')
    iupacDNA['S'] = ('C', 'G')
    iupacDNA['Y'] = ('C', 'T')
    iupacDNA['K'] = ('G', 'T')
    iupacDNA['V'] = ('A', 'C', 'G')
    iupacDNA['H'] = ('A', 'C', 'T')
    iupacDNA['D'] = ('A', 'G', 'T')
    iupacDNA['B'] = ('C', 'G', 'T')
    iupacDNA['N'] = ('A', 'C', 'G', 'T')

    reverse_iupacDNA = dict(map(lambda x : (x[1],x[0]), iupacDNA.items()))

    alignedSequences = Alignment(entries)
    
    consensusNtSeq = ""
    def addCountInCol(t, columnCount):
        lt = float(len(t))
        for x in t:
            columnCount[x]+= 1/lt
    
    def cmpTuple(t1,t2):
        return cmp(t1[1],t2[1])
        
    thresholdCount = threshold*len(alignedSequences)
    for c in columnIterator(alignedSequences):
        colC = {'A':0., 'C':0., 'G':0., 'T':0., '-':0.}
        map(lambda t: addCountInCol(t, colC), map(lambda nt: iupacDNA[nt.upper()], c))
        
        
        counts = colC.items()
        counts.sort(cmpTuple, reverse=True)
        
        sumCounts = 0
        symbols = list()
        for nt, count in counts: 
            sumCounts += count
            symbols.append(nt)
            
            if sumCounts>=thresholdCount:
                symbols.sort()
                t = tuple(symbols)
                try:
                    consensusNtSeq += reverse_iupacDNA[t]
                except:
                    consensusNtSeq += '?'
                finally:
                    break
                
    consensusSeq = NucSequence('Consensus_%d'%(int(threshold*100,)),
                                consensusNtSeq,
                               'Consensus sequence done on %d aligned sequences of length %d with a threshold of %d %%'%(len(alignedSequences), 
                                                                                                                        len(alignedSequences[0]),
                                                                                                                        int(threshold*100)))
    writer = sequenceWriterGenerator(options)
    consensusSeq
    writer(consensusSeq)
