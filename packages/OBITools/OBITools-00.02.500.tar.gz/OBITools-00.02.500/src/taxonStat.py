#!/usr/local/bin/python

from obitools.ecopcr import taxonomy
from obitools.ecopcr.sequence import EcoPCRDBSequenceIterator
from obitools.format.sequence.fasta import fastaIterator
from obitools.format.sequence.genbank import genbankIterator

from obitools.options import getOptionManager



def addTaxonomyOptions(optionManager):
        
    optionManager.add_option('-d','--ecopcrdb',
                             action="store", dest="db",
                             metavar="<FILENAME>",
                             type="string",
                             help="ecoPCR Database "
                                  "name")
    
    optionManager.add_option('-f','--fasta',
                             action="store_const", dest="iterator",
                             const=fastaIterator,
                             help="input file is in fasta format")
   
    optionManager.add_option('-g','--genbank',
                             action="store_const", dest="iterator",
                             const=genbankIterator,
                             help="input file is in genbank format")
   
    optionManager.add_option('-e','--ecopcr',
                             action="store_const", dest="iterator",
                             const=EcoPCRDBSequenceIterator,
                             help="input file is in ecopcr format")
   

if __name__=='__main__':

    optionParser = getOptionManager([addTaxonomyOptions]
                                    )
    
    (options, entries) = optionParser()
    
    tax = taxonomy.EcoTaxonomyDB(options.db)
    if options.iterator==EcoPCRDBSequenceIterator:
        seqd= options.iterator(options.db)
    else:
        seqd= options.iterator(entries)
    
    ranks = set(x for x in tax.rankIterator())
    
    listtaxonbyrank = {}
    
    for seq in seqd:
        seq.extractTaxon()

        for rank,rankid in ranks:
            if rank != 'no rank':
                t = tax.getTaxonAtRank(seq['taxid'],rankid)
                if t is not None:
                    if rank in listtaxonbyrank:
                        listtaxonbyrank[rank].add(t)
                    else:
                        listtaxonbyrank[rank]=set([t])
                        
    stats = dict((x,len(listtaxonbyrank[x])) for x in listtaxonbyrank)
    
    listtaxonbyrank = {}
        
    ranknames = [x[0] for x in ranks]
    ranknames.sort()
    
    print '%-20s\t%10s' % ('rank','db')
    
    for r in ranknames:
        if  r in stats and stats[r]:
            print '%-20s\t%10d' % (r,stats[r])
            
     

