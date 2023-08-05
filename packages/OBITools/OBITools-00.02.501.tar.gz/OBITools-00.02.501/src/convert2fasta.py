#!/usr/local/bin/python
'''
Created on 18 sept. 2009

@author: coissac
'''

from obitools.options import getOptionManager
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.utils import deprecatedScript


if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    deprecatedScript('obiconvert')
    
    optionParser = getOptionManager([addInOutputOption])
                                    
    
    (options, entries) = optionParser()
    writer = sequenceWriterGenerator(options)
    
    for entry in entries:
        print writer(options,entry)