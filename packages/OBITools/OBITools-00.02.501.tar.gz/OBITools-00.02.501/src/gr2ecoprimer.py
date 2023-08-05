#!/usr/local/bin/python
'''
Created on 6 mai 2009

@author: coissac
'''

from obitools.options import getOptionManager
from obitools.options.taxonomyfilter import addTaxonomyFilterOptions,  \
                                            taxonomyFilterIteratorGenerator
from obitools.utils import ColumnFile,universalOpen
from obitools.ecopcr.taxonomy import ecoTaxonomyWriter
from obitools.ecopcr.sequence import EcoPCRDBSequenceWriter,EcoPCRDBSequenceIterator
from obitools.format.sequence.embl import emblParser
from obitools import NucSequence

import sys

from urllib2 import urlopen

def addGROptions(optionManager):
    
    optionManager.add_option('-g','--genome-reviews',
                             action="store", dest="ftp",
                             metavar="<Genome reviews FTP URL>",
                             type="string",
                             default="ftp://ftp.ebi.ac.uk/pub/databases/genome_reviews",
                             help="Genome reviews FTP URL default value to ftp://ftp.ebi.ac.uk/pub/databases/genome_reviews")

    optionManager.add_option('-n','--name',
                             action="store", dest="name",
                             metavar="PREFIX",
                             type="string",
                             default="ftp://ftp.ebi.ac.uk/pub/databases/genome_reviews",
                             help="New EcoPCR database name")

    optionManager.add_option('-s','--store-raw',
                             action="store", dest="rawfiles",
                             metavar="PREFIX",
                             type="string",
                             default=None,
                             help="Repository for raw sequences")

    optionManager.add_option('-R','--recover',
                             action="store_true", dest="recover",
                             default=False,
                             help="Set into recover mode")


if __name__=='__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([addGROptions,addTaxonomyFilterOptions])
    
    
    (options, entries) = optionParser()

    assert options.name is not None, "You must use -d options"
    writeTaxtonomy= options.taxonomy is None or options.name != options.taxonomy
    
    filter = taxonomyFilterIteratorGenerator(options)
    if writeTaxtonomy:
        ecoTaxonomyWriter(options.name, options.taxonomy)
    
    print >>sys.stderr,"download : ",options.ftp+"/gr2species.txt"
    
    gr2species = urlopen(options.ftp+"/gr2species.txt")
    gr2species = ColumnFile(gr2species, '\t', True, (str,int,str,str,int,str),
                            head=('AC','taxid','name','replicon','GRID','uniprotID')
                            )

#    a) sequence AC    
#    b) NCBI Tax ID
#    a) Species name
#    c) Chromosome/plasmid name
#    d) Genome Reviews Accession number
#    f) uniprot ornanism code


    genome={}

    for seq in filter(gr2species):
        if seq['replicon'][0:10]=='Chromosome':
            grid = seq['GRID']
            if grid not in genome:
                genome[grid]={'name':seq['name'],'AC':[],'taxid':seq['taxid'],'uniprotID':seq['uniprotID']}
            genome[grid]['AC'].append(seq['AC'])
            
    if options.recover:
        print >>sys.stderr,"Readding old library...",
        seqdb = EcoPCRDBSequenceIterator(options.name,options.taxonomy)
        seqac = set(x.id for x in seqdb)
        print >>sys.stderr," %d genomes already downloaded" % len(seqac)

        db = EcoPCRDBSequenceWriter(options.name, taxonomy=options.taxonomy,append=True)
    else:
        db = EcoPCRDBSequenceWriter(options.name, taxonomy=options.taxonomy)
        seqac=set()

    for grid in genome:
        sequence = []
        ok=True
        gac = '%s_%d' % (genome[grid]['uniprotID'],grid)
        if gac in seqac:
            print >> sys.stderr,'Skip genome [%d] : %s' % (grid,genome[grid]['name'])
        else:
            print >> sys.stderr,'Download genome [%d] : %s' % (grid,genome[grid]['name'])
            for ac in genome[grid]['AC']:
                print >> sys.stderr,'         Sequence : %s...' % ac,
                try:
                    downloaded=universalOpen("%s/dat/cellular/%s.dat.gz" % (options.ftp,ac)).read()
                    if (options.rawfiles is not None):
                        save = open("%s/%s.dat" % (options.rawfiles,ac),"w")
                        save.write(downloaded)
                        del save
                    
                    data = emblParser(downloaded)
                    sequence.append(data)
                    print >> sys.stderr,'ok'
                except:
                    print >> sys.stderr,'bad'
                    ok=False
                    
            if ok:
                sequence=('X'*40).join([str(x) for x in sequence])
                sequence=NucSequence(gac,
                                     sequence,
                                     genome[grid]['name'],taxid=genome[grid]['taxid'])
                db.put(sequence)
            
    
