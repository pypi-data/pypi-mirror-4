#!/usr/local/bin/python

import re
import sys

from obitools.fasta import fastaIterator,formatFasta
from obitools.options import getOptionManager
from obitools.options.taxonomyfilter import addTaxonomyDBOptions
from obitools.options.taxonomyfilter import loadTaxonomyDatabase
from obitools.ecopcr.taxonomy import ecoTaxonomyWriter

def addTaxonomyOptions(optionManager):
        
    optionManager.add_option('-u','--undefined',
                             action="store", dest="undefined",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file used to store unidentified sequences")

    optionManager.add_option('-T','--tag-name',
                             action="store", dest="tagname",
                             metavar="<tagname>",
                             type="string",
                             default='species',
                             help="file containing tag used")

if __name__=='__main__':

    optionParser = getOptionManager([addTaxonomyOptions,addTaxonomyDBOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()


    
    tax=loadTaxonomyDatabase(options)
    
        
    
    if options.undefined is not None:
        options.undefined=open(options.undefined,'w')
        
    
    for s in entries:
        if options.tagname in s:
            sp = s[options.tagname]
            try:
                taxon = tax.findTaxonByName(sp)
                s['taxid']=taxon[0]
                print formatFasta(s)
            except KeyError:
                if options.undefined is not None:
                    print >> options.undefined,formatFasta(s)
            