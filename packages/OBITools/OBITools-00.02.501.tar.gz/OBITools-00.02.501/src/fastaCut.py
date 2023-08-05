#!/usr/local/bin/python


from obitools.fasta import fastaIterator,formatFasta

from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions, sequenceFilterIteratorGenerator
                                          
from obitools.options.bioseqcutter import addSequenceCuttingOptions, cutterIteratorGenerator

if __name__=='__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass

    optionParser = getOptionManager([addSequenceFilteringOptions,
                                     addSequenceCuttingOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()

    filter = sequenceFilterIteratorGenerator(options)
    cutter = cutterIteratorGenerator(options)
    
    
    for seq in cutter(filter(entries)):
        print formatFasta(seq) 
