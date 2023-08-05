#!/usr/local/bin/python

import re
import sys

from obitools.tagmatcher.parser import TagMatcherIterator,formatTagMatcher
from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions
from obitools.options.bioseqfilter import sequenceFilterIteratorGenerator

from obitools.tagmatcher.options import addTagMatcherErrorOptions
   
    
if __name__=='__main__':
    
    optionParser = getOptionManager([addSequenceFilteringOptions,addTagMatcherErrorOptions], 
                                    entryIterator=TagMatcherIterator)
    
    (options, entries) = optionParser()
    goodFasta = sequenceFilterIteratorGenerator(options)
    
#    print formatTagMatcher(entries)
    
    for seq in goodFasta(s.eminEmaxFilter(options.emin,options.emax) for s in entries):
        print formatTagMatcher(seq)
