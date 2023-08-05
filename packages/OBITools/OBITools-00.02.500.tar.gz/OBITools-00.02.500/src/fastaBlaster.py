#!/usr/local/bin/python
'''
Created on 15 oct. 2009

@author: coissac
'''


from obitools.format.sequence.fasta import fastaNucIterator
from obitools.options import getOptionManager


if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([],
                                    entryIterator=fastaNucIterator
                                    )
    
    (options, entries) = optionParser()
    
    for seq in entries:
        pass
