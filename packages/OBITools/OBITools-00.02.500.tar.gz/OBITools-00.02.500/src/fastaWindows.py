#!/usr/local/bin/python

"""
   fastaWindows.py
"""

import fileinput
import getopt
import sys


import obitools
from obitools.fasta import fastaIterator,formatFasta
from obitools.word import wordIterator


from obitools.options import getOptionManager



def addWindowsOptions(optionManager):
    
    optionManager.add_option('-l','--window-length',
                             action="store", dest="length",
                             metavar="<WORD SIZE>",
                             type="int",
                             default=None,
                             help="size of the sliding window")

    optionManager.add_option('-s','--step',
                             action="store", dest="step",
                             metavar="<STEP>",
                             type="int",
                             default=1,
                             help="position difference between two windows")

    optionManager.add_option('-p','--phase',
                             action="store", dest="phase",
                             metavar="phase",
                             type="int",
                             default=1,
                             help="phase of returned word")

    optionManager.add_option('-P','--phase-size',
                             action="store", dest="phasesize",
                             metavar="###",
                             type="int",
                             default=None,
                             help="For phased windows indiquate the length of one element")
    
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
    
    optionParser = getOptionManager([addWindowsOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()
    
    if options.phasesize is not None:
         assert options.phase <= options.phasesize
         options.phasesize-=1
         
    for seq in entries:
        id = seq.id
        de = seq.definition
        fragment = 0
        for word in wordIterator(seq, options.length, options.step, circular=options.circular):
            if options.phasesize is not None:
                word = word[options.phase::options.phasesize]
            wid = "%s_%05d" % (id,fragment)
            ws = obitools.NucSequence(wid,word,de,word=fragment,wordsize=options.length,wordstep=options.step)
            print formatFasta(ws)
            fragment+=1
            
            
