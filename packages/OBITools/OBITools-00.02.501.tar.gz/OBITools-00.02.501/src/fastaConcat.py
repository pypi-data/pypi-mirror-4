#!/usr/local/bin/python
'''
Created on 22 janv. 2010

@author: coissac
'''

from obitools.options import getOptionManager
from obitools.fasta import fastaIterator
from obitools.fasta import formatFasta
from obitools.options.taxonomyfilter import addTaxonomyDBOptions
from obitools.options.taxonomyfilter import loadTaxonomyDatabase
from obitools import NucSequence

def addConcatOptions(optionManager):
    optionManager.add_option('-s','--spacer',
                             action="store", dest="spacer",
                             type=str,
                             default='x'*40,
                             help="spacer inserted between sequences, 40 'x' by default"
                             )


if __name__ == '__main__':
    optionParser = getOptionManager([addConcatOptions,addTaxonomyDBOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()

    taxonomy=loadTaxonomyDatabase(options)

    data=[]
    taxid=set()
    count=0
    
    for seq in entries:
        count+=1
        data.append(str(seq))
        if 'taxid' in seq:
            taxid.add(seq['taxid'])

    seq=NucSequence(seq.id,options.spacer.join(data),seq.definition)
    seq['concat']=count
    
    if taxid:
        taxid = taxonomy.lastCommonTaxon(*list(taxid))
        scientific_name= taxonomy.getScientificName(taxid)
        seq['taxid']=taxid
        seq['scientific_name']=scientific_name
        
    print formatFasta(seq)
    
    
