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
from obitools.word import wordIterator

acgt=re.compile('[acgt]*')

if __name__ == '__main__':
    
    optionParser = getOptionManager([addTaxonomyFilterOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()
       
    taxonomyFilter = taxonomyFilterIteratorGenerator(options)
    
    good     = taxonomyFilter(entries)

    dico={}
    i=0
    
    for seq in good:
        sseq = str(seq)
        for word in (sseq[p:p+15] for p in xrange(0,len(sseq)-15)): 
            word = str(word)
            if word in dico:
                dico[word].append(seq['taxid'])
            else:
                dico[word]=[seq['taxid']]
        i+=1
        print >>sys.stderr,"Counted words : %10d/%d\r" % (len(dico),i),
        
    dnakey = dico.keys()
    dnakey.sort()
    
    for word in dnakey:
        l = len(dico[word])
        if l > 1:
            lca = options.taxonomy.lastCommonTaxon(dico[word])[0]
            print word,l,lca,options.taxonomy.getRank(lca),options.taxonomy.getScientificName(lca)
            
         