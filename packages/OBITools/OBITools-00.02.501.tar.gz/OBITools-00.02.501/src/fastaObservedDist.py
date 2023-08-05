#!/usr/local/bin/python
"""\
-------------------------------------------------------
 fastaObservedDist.py
-------------------------------------------------------

fastaObservedDist.py [-h|--help] <fastafile>"

    add length data on all sequences in the fasta file.

-------------------------------------------------------
-h    --help                       : print this help
-------------------------------------------------------
"""


from obitools.align import alignmentReader
from obitools.fasta import fastaIterator
from obitools.distances.observed import PairewiseGapRemoval,Pairewise
from obitools.distances.r import writeRMatrix
from obitools.distances.phylip import writePhylipMatrix
from obitools.options import getOptionManager

def addOligoOptions(optionManager):
    
    optionManager.add_option('-g','--with_gap',
                             action="store_true", dest="distmode",
                             default=False,
                             help="Take gap in account in distance evaluation")

    optionManager.add_option('-r','--r_format',
                             action="store_true", dest="rformat",
                             default=False,
                             help="Output is formated to be read by R")


if __name__=='__main__':
    
    optionParser = getOptionManager([addOligoOptions],
                                    entryIterator=None
                                    )
    
    (options, entries) = optionParser()
    
    ali = alignmentReader(entries, fastaIterator)

    if options.distmode:
        dist= Pairewise(ali)
    else:
        dist= PairewiseGapRemoval(ali)
    
    if options.rformat:
        print writeRMatrix(dist)
    else:
        print writePhylipMatrix(dist)
    
    
    