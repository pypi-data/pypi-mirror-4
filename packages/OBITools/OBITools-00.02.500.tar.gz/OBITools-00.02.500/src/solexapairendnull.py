#!/usr/local/bin/python
'''
:py:mod:`solexaPairEnd` : align overlapping pair-end solexa reads and return the consensus sequence together with its quality
=============================================================================================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`solexaPairEnd` aims at aligning the two reads of a pair-end library sequenced using a Solexa.

The program takes for arguments one or two fastq solexa sequences reads files. 

In the case where two files are given one should be associated with the -r option. Sequences corresponding to the same read pair must have the same line number in the two files.
In the case where one file is provided, sequences, which are supposed to be all of the same length, are considered to be the concatenation of the two pair end reads. Hence
the first half of a sequence is considered one extremity of the pair-end and the second half the other one.


:py:mod:`solexaPairEnd` align the first sequence with the reverse complement of the second sequence and report the consensus sequence of the alignment (taking into account
the base qualities) together with the qualities for each base of the reported consensus sequence.

.. code-block:: bash

   > solexaPairEnd -r seq3P.fasta seq5P.fasta > seq.fasta

'''

from obitools.options import getOptionManager, allEntryIterator
from obitools.fastq import fastqSolexaIterator, formatFastq
from obitools.align import QSolexaReverseAssemble
from obitools.align import QSolexaRightReverseAssemble
from obitools.tools._solexapairend import buildConsensus
from obitools.format.options import addInputFormatOption,addOutputFormatOption,\
    sequenceWriterGenerator

from itertools import chain
import cPickle
import sys

def addSolexaPairEndOptions(optionManager):
    optionManager.add_option('-r','--reverse-reads',
                             action="store", dest="reverse",
                             metavar="<FILENAME>",
                             type="str",
                             default=None,
                             help="Filename containing reverse solexa reads "
                            )
    optionManager.add_option('--sanger',
                             action="store_const", dest="seqinformat",
                             default=None,
                             const='sanger',
                             help="input file is in sanger fastq nucleic format (standard fastq)")

    optionManager.add_option('--solexa',
                             action="store_const", dest="seqinformat",
                             default=None,
                             const='solexa',
                             help="input file is in fastq nucleic format produced by solexa sequencer")

    optionManager.add_option('--illumina',
                             action="store_const", dest="seqinformat",
                             default=None,
                             const='illumina',
                             help="input file is in fastq nucleic format produced by old solexa sequencer")
    
    optionManager.add_option('--ascii',
                             action="store_true", dest="ascii",
                             default=False,
                             help="output in ascii format")

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
    
    old=None
    for s in seqs:
        d = s[0:lread]
        r = s[lread:]
        if old is not None:
            yield(d,old)
        old=r
    
def seqPairs(direct,reverse):
    d = direct.next()
    for d in direct:
        r = reverse.next()
        yield(d,r)
    
la = QSolexaReverseAssemble()
ra = QSolexaRightReverseAssemble()

def buildAlignment(direct,reverse):
    
    if len(direct)==0 or len(reverse)==0:
        return None
        
    la.seqA=direct 
    la.seqB=reverse 
    ali=la()
    
    ra.seqA=direct
    ra.seqB=reverse
    rali=ra()
    
    return ali.score,rali.score
        
def alignmentIterator(sequences):
    
    for d,r in sequences:
        ali = buildAlignment(d,r)
        if ali is None:
            continue
        yield ali
        
        
    
    
if __name__ == '__main__':
    optionParser = getOptionManager([addSolexaPairEndOptions,addOutputFormatOption],checkFormat=True
                                    )
    
    (options, direct) = optionParser()
    
    if options.reverse is None:
        sequences=cutDirectReverse(direct)
    else:
        reverse = allEntryIterator([options.reverse],options.readerIterator)
        sequences=seqPairs(direct,reverse)
        
    writer = sequenceWriterGenerator(options)
    
    old=None
    ba = alignmentIterator(sequences)
    distnullLeft=[]
    distnullRight=[]
            
    
    for l,r in ba:
        distnullLeft.append(l)
        distnullRight.append(r)
        
    distnullLeft.sort()
    distnullRight.sort()
    
    protocol = 0 if options.ascii else 2
    cPickle.dump(distnullLeft, sys.stdout, protocol=protocol)
    cPickle.dump(distnullRight, sys.stdout, protocol=protocol)
        
        
        
        

