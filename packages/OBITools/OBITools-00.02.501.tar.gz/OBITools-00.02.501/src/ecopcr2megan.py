#!/usr/local/bin/python
'''
Created on 6 mai 2010

@author: coissac
'''

from obitools.ecopcr import EcoPCRFile
from obitools.options import getOptionManager
import time
from obitools.options.taxonomyfilter import addTaxonomyDBOptions,\
    loadTaxonomyDatabase

if __name__=='__main__':

    optionParser = getOptionManager([addTaxonomyDBOptions],
                                    entryIterator=EcoPCRFile
                                    )
    
    (options, entries) = optionParser()
    taxonomy=loadTaxonomyDatabase(options)
#print "@Source=megan/data.blast" 
#print "@CreationDate=%s" % time.strftime("%a %b %d %H:%M:%S %Z %Y")
#print "@Creator=ecoPCR2MEGAN (obitools)" 
#print "@Format=rid tid" 

old_id = ''
seq_in_id=0
for seq in entries:
    if seq.id != old_id:
        seq_in_id=0
        old_id = seq.id
    seq_in_id+=1
    seq.id="%s_%d" % (seq.id,seq_in_id)

    print "%s, %s, %d" % (seq.id,taxonomy.getScientificName(seq['taxid']),1)
