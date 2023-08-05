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

from obitools import NucSequence
from obitools.options import getOptionManager, allEntryIterator
from obitools.align import QSolexaReverseAssemble
from obitools.align import QSolexaRightReverseAssemble
from obitools.tools._solexapairend import buildConsensus
from obitools.format.options import addInputFormatOption,addOutputFormatOption,\
    sequenceWriterGenerator

from itertools import chain
import cPickle
import math

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

    optionManager.add_option('--proba',
                             action="store", dest="proba",
                             metavar="<FILENAME>",
                             type="str",
                             default=None,
                             help="null ditribution data file")
    
    optionManager.add_option('--score-min',
                             action="store", dest="smin",
                             metavar="#.###",
                             type="float",
                             default=None,
                             help="minimum score for keeping aligment")

    optionManager.add_option('--pvalue',
                             action="store", dest="pvalue",
                             metavar="#.###",
                             type="float",
                             default=None,
                             help="maximum pvalue for keeping aligment")
    
    optionManager.add_option('-j','--junction-length',
                             action="store", dest="junction",
                             metavar="###",
                             type="int",
                             default=10,
                             help="length of the N junction between both the reads (default=10)"
                            )
    optionManager.add_option('-n','--n-quality',
                             action="store", dest="nqual",
                             metavar="###",
                             type="int",
                             default=10,
                             help="quality assign to the N of the junction (default=10)"
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
    
la = QSolexaReverseAssemble()
ra = QSolexaRightReverseAssemble()

def buildAlignment(direct,reverse):
    
    if len(direct)==0 or len(reverse)==0:
        return None
        
    la.seqA=direct 
    la.seqB=reverse 
    ali=la()
    ali.direction='left'
    
    ra.seqA=direct
    ra.seqB=reverse
    rali=ra()
    rali.direction='right'
    
    if ali.score < rali.score:
        ali=rali

    return ali
        
def alignmentIterator(sequences):
    
    for d,r in sequences:
        ali = buildAlignment(d,r)
        if ali is None:
            continue
        yield ali
        
      
def buildJoinedSequence(ali,options):
    d = ali[0].getRoot()
    r = ali[1].getRoot()

    nqual = 10.**-(options.nqual/10.)
    junction = options.junction
    
    r=r.complement()
    
    s = str(d) + 'n' * junction + str(r)
    
    seq = NucSequence(d.id + '_Join',s,d.definition,**d)
    
    withqual = hasattr(d, 'quality') or hasattr(r, 'quality')
    
    if withqual:
        if hasattr(d, 'quality'):
            quality = d.quality
        else:
            quality = [10**-4] * len(d)
            
        quality.extend([nqual] * junction)
        
        if hasattr(r, 'quality'):
            quality.extend(r.quality)
        else:
            quality.extend([10**-4] * len(r))
            
        seq.quality=quality
        
    seq['score']=ali.score
    seq['direction']=ali.direction
    seq['mode']='join'
    
    return seq

    
    
if __name__ == '__main__':
    optionParser = getOptionManager([addSolexaPairEndOptions,addOutputFormatOption],checkFormat=True
                                    )
    
    (options, direct) = optionParser()

    options.sminL = None
    options.sminR = None

    
    if options.proba is not None and options.smin is None:
        p = open(options.proba)
        options.nullLeft  = cPickle.load(p)
        options.nullRight = cPickle.load(p)
        
        assert options.pvalue is not None, "You have to indicate a pvalue or an score min"
        
        i = int(math.floor((1.0 - options.pvalue) * len(options.nullLeft)))
                           
        if i == len(options.nullLeft):
            i-=1
        options.sminL = options.nullLeft[i]
        
        i = int(math.floor((1.0 - options.pvalue) * len(options.nullRight)))
        if i == len(options.nullRight):
            i-=1
        options.sminR = options.nullRight[i]
        
    if options.smin is not None:
        options.sminL = options.smin
        options.sminR = options.smin
        
        
    if options.reverse is None:
        sequences=cutDirectReverse(direct)
    else:
        reverse = allEntryIterator([options.reverse],options.readerIterator)
        sequences=seqPairs(direct,reverse)
        
    writer = sequenceWriterGenerator(options)
    
    ba = alignmentIterator(sequences)
                
    for ali in ba:
        
        if options.sminL is not None:
            if (   (ali.direction=='left' and ali.score > options.sminL) 
                or (ali.score > options.sminR)):
                consensus = buildConsensus(ali)
            else:
                consensus = buildJoinedSequence(ali, options)
                
            consensus['sminL']=options.sminL
            consensus['sminR']=options.sminR
        else:
            consensus = buildConsensus(ali)
                        
        writer(consensus)
        
        
        
        

