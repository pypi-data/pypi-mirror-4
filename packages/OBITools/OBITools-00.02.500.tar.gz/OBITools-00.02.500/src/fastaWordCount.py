#!/usr/local/bin/python

"""
   fastaWordCount.py
"""

import fileinput
import getopt
import sys


import obitools
from obitools.fasta import fastaIterator,formatFasta
from obitools.word import wordIterator
from obitools.word import wordCount,allDNAWordIterator,decodeWord


from obitools.options import getOptionManager



def addCountWordOptions(optionManager):
    
    optionManager.add_option('-l','--word-length',
                             action="store", dest="length",
                             metavar="<WORD SIZE>",
                             type="int",
                             default=1,
                             help="size of the sliding window")

    optionManager.add_option('-s','--step',
                             action="store", dest="step",
                             metavar="<STEP>",
                             type="int",
                             default=1,
                             help="position difference between two words")

    optionManager.add_option('-p','--phase',
                             action="store", dest="phase",
                             metavar="phase",
                             type="int",
                             default=1,
                             help="phase of counted words")

    optionManager.add_option('-c','--circular',
                             action="store_true", dest="circular",
                             default=False,
                             help="set for circular sequence")



if __name__=='__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([addCountWordOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()

    options.phase-=1
    allword = [x for x in allDNAWordIterator(options.length)]
    allword.sort()
    
    print "%20s" % 'id',
    wformat = "%%%ds" % (options.length+2)
    
    for w in allword:
        print wformat % decodeWord(w,options.length),
        
    print
    
    for seq in entries:
        if options.phase:
            seq = seq[options.phase:]
        wc = wordCount(wordIterator(seq, options.length, options.step, circular=options.circular))
        print "%20s" % seq.id,
        for w in allword:
            
            count = str(wc.get(w,0))
            print wformat % count,
        print
        
            