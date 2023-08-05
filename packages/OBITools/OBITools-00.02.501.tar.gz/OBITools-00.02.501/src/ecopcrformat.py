#!/usr/local/bin/python
'''
Created on 26 sept. 2010

@author: coissac
'''
from obitools.options.taxonomyfilter import addTaxonomyDBOptions,loadTaxonomyDatabase
from obitools.options import getOptionManager
from obitools.format.options import addInOutputOption
from obitools.ecopcr.sequence import EcoPCRDBSequenceWriter


if __name__ == '__main__':
    
    optionParser = getOptionManager([addTaxonomyDBOptions,addInOutputOption])

    (options, entries) = optionParser()
    
    loadTaxonomyDatabase(options)
    
    writer = EcoPCRDBSequenceWriter(options.ecodb, 1, options.taxonomy)
    
    for s in entries:
        writer.put(s)
        
    del writer
    
