#!/usr/local/bin/python
'''
Created on 18 sept. 2009

@author: coissac
'''

from obitools.options import getOptionManager
from obitools.format.options import addInOutputOption, sequenceWriterGenerator


if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([addInOutputOption])
                                    
    
    (options, entries) = optionParser()
    writer = sequenceWriterGenerator(options)
    
    for entry in entries:
        writer(entry)