#!/usr/local/bin/python
'''
Created on 10 juin 2009

@author: coissac
'''
import re
import sys
from logging import root,DEBUG

from obitools.fasta import fastaIterator,formatFasta
from obitools.ecopcr.taxonomy import EcoTaxonomyDB
from obitools.options.taxonomyfilter import addTaxonomyFilterOptions
from obitools.options.taxonomyfilter import taxonomyFilterIteratorGenerator
from obitools.options import getOptionManager

parent = re.compile('\([^\)]+\)')
def addOutputOptions(optionManager):
    optionManager.add_option('-u','--unidentified',
                             action="store", dest="unidentified",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="File to output unmatched sequence")

def addTaxidGenerator(options):
    def addTaxid(sequences):
        global options
        for seq in sequences:
            name = parent.sub('',seq.definition)
            name = name.strip(' |')
            try:
                taxon = options.taxonomy.findTaxonByName(name)
                taxid=taxon[0]
                seq['taxid']=taxid
                yield seq
            except KeyError:
                if options.unidentified is not None:
                    print >>options.unidentified, formatFasta(seq)
                    
    return addTaxid

if __name__ == '__main__':

    optionParser = getOptionManager([addOutputOptions,addTaxonomyFilterOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()

    if options.unidentified is not None:
        options.unidentified=open(options.unidentified,"w")
        
    taxonomyFilter = taxonomyFilterIteratorGenerator(options)
    
    sequences= addTaxidGenerator(options)(entries)
    good     = taxonomyFilter(sequences)
    for seq in good:
        seq['name']=options.taxonomy.getScientificName(seq['taxid'])
        print formatFasta(seq)