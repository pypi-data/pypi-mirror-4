#!/usr/local/bin/python

from obitools.fasta import fastaIterator,formatFasta
from obitools.ecopcr.taxonomy import EcoTaxonomyDB
from obitools.options import getOptionManager

import sys
import re
from logging import root,DEBUG


def addTaxonomyOptions(optionManager):
        
    optionManager.add_option('-t','--taxonomy',
                             action="store", dest="taxonomy",
                             metavar="<FILENAME>",
                             type="string",
                             help="ecoPCR taxonomy Database "
                                  "name")

if __name__=='__main__':
    
    optionParser = getOptionManager([addTaxonomyOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()

    taxonomy = EcoTaxonomyDB(options.taxonomy)

    for seq in entries:
        taxid = int(seq['taxid'])
        species = taxonomy.getSpecies(taxid)
        if species is not None:
            print formatFasta(seq)
            
            