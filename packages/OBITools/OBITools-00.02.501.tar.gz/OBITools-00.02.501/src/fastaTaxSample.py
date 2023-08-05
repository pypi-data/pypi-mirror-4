#!/Library/Frameworks/Python.framework/Versions/2.6/Resources/Python.app/Contents/MacOS/Python

import sys

from obitools.fasta import fastaIterator,formatFasta
from obitools.ecopcr.taxonomy import EcoTaxonomyDB
from obitools.options import getOptionManager

def addTaxonomyOptions(optionManager):
    optionManager.add_option('-t','--taxonomy',
                             action="store", dest="taxonomy",
                             metavar="<FILENAME>",
                             type="string",
                             help="ecoPCR taxonomy Database name")

    optionManager.add_option('-r','--rank',
                             action="store", dest="rank",
                             metavar="<RANKNAME>",
                             type="string",
                             help="taxonomic rank name "
                                  "(i.e. genus, species...)")
    

if __name__=='__main__':

    optionParser = getOptionManager([addTaxonomyOptions],
                                    entryIterator=fastaIterator
                                    )
    
    (options, entries) = optionParser()

    assert options.taxonomy is not None,"You must specify a -t option"
    assert options.rank is not None,"You must specify a -r option"

    taxonomy = EcoTaxonomyDB(options.taxonomy)

    found = set()
 
    for seq in entries: 
        currenttaxid = seq['taxid']
        ranktaxid    = taxonomy.getTaxonAtRank(currenttaxid,options.rank)
        
        if ranktaxid is not None:
            if ranktaxid not in found:
                found.add(ranktaxid)
                seq[options.rank]=ranktaxid
                seq[options.rank+'_sn']=taxonomy.getScientificName(ranktaxid)
                
                print formatFasta(seq) 
