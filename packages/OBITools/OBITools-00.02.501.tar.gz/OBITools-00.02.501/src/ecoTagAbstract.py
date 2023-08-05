#!/usr/local/bin/python

import sys

from obitools.options import getOptionManager
from obitools.ecotag.parser import EcoTagFileIterator
from obitools.ecotag.parser import ecoTagIdentifiedFilter

from obitools.ecopcr.taxonomy import EcoTaxonomyDB


def addAbstractOptions(optionManager):
    
    optionManager.add_option('-r','--rank',
                             action="store", dest="rank",
                             metavar="<TAXONOMIC RANK>",
                             type="string",
                             help="")

    optionManager.add_option('-t','--taxonomy',
                             action="store", dest="taxonomy",
                             metavar="<FILENAME>",
                             type="string",
                             help="ecoPCR taxonomy Database "
                                  "name")
    
    optionManager.add_option('-f','--min-frequency',
                             action="store", dest="frequency",
                             metavar="#.##",
                             type="float",
                             default=0.01,
                             help="minimal frequency to take into account a sequence")
    
def cmpTaxonAbstract(t1,t2):
    return cmp(abstract[t2]['count'],abstract[t1]['count'])
    
if __name__=='__main__':
    
    optionParser = getOptionManager([addAbstractOptions],
                                    entryIterator=EcoTagFileIterator
                                    )
    
    (options, entries) = optionParser()
    
    print >>sys.stderr,"Reading taxonomy...",
    taxonomy = EcoTaxonomyDB(options.taxonomy)
    rankid = taxonomy.findRankByName(options.rank)
    print >>sys.stderr,"Ok"
    
    total = 0
    ids   = []
    
    print >>sys.stderr,"Reading ecoTag file...",
    for r in ecoTagIdentifiedFilter(entries):
        total+=r['count']
        ids.append(r)
    print >>sys.stderr,"Ok"
        
    ids = [x for x in ids if float(x['count'])/total >= options.frequency]
    
    abstract = {}
    
    for r in ids:
        taxon = taxonomy.getTaxonAtRank(r['taxid'], rankid)
        if taxon is not None:
            scientific_name = taxonomy.getScientificName(taxon)
        else:
            scientific_name = '--'
            taxon=-1
        if taxon in abstract:
            abstract[taxon]['count']+=r['count']
            if r['max_identity'] > abstract[taxon]['best_hit']:
                abstract[taxon]['best_hit']=r['max_identity']
            if r['max_identity'] < abstract[taxon]['worst_hit']:
                abstract[taxon]['worst_hit']=r['max_identity']
        else:
            abstract[taxon]= {'count':r['count'],
                              'scientific_name':scientific_name,
                              'best_hit':r['max_identity'],
                              'worst_hit':r['max_identity']}
            
    
    taxonlist = abstract.keys()
    taxonlist.sort(cmpTaxonAbstract)
    
    for taxon in taxonlist:
        t = abstract[taxon]
        print "%s\t%d\t%s\t%d\t%4.3f\t%4.3f\t%4.3f" % (t['scientific_name'],
                                                   taxon,
                                                   options.rank,
                                                   t['count'],
                                                   float(t['count'])/total,
                                                   t['best_hit'],
                                                   t['worst_hit'])
        
        
