'''
Created on 25 mai 2009

@author: coissac
'''

from obitools.options import getOptionManager

from obitools.options.taxonomyfilter import addTaxonomyFilterOptions,  \
                                            taxonomyFilterIteratorGenerator

from obitools.ecopcr.taxonomy import EcoTaxonomyDB
from obitools.ecopcr.sequence import EcoPCRDBSequenceIterator

def addRankOptions(optionManager):
    
    optionManager.add_option('--rank',
                             action="store", dest="rank",
                             metavar="<taxonomic rank>",
                             type="string",
                             default="species",
                             help="Taxonomic rank")


def cmptax(taxonomy):
    def cmptaxon(t1,t2):
        return cmp(taxonomy.getScientificName(t1),
                   taxonomy.getScientificName(t2))
    return cmptaxon

if __name__=='__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([addRankOptions,addTaxonomyFilterOptions])
    
    
    (options, entries) = optionParser()


    filter = taxonomyFilterIteratorGenerator(options)
    seqdb = EcoPCRDBSequenceIterator(options.ecodb,options.taxonomy)

    stats = {}
    i=0
    tot=0
    for seq in filter(seqdb):
        tot+=1
        t = options.taxonomy.getTaxonAtRank(seq['taxid'],options.rank)
        if t is not None:
            i+=1
            stats[t]=stats.get(t,0)+1
       
    print "#sequence count : %d" % tot
    print "#considered sequences : %d" % i     
    print "# %s : %d" % (options.rank,len(stats))
    taxons = stats.keys()
    taxons.sort(cmptax(options.taxonomy))
    
    for t in taxons:
        print "%s\t%d" % (options.taxonomy.getScientificName(t),stats[t])
    