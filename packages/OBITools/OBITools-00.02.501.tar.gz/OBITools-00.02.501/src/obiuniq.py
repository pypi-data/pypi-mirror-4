#!/usr/local/bin/python


from obitools.format.options import addInputFormatOption
from obitools.fasta import formatFasta
from obitools.utils.bioseq import uniqSequence,uniqPrefixSequence
from obitools.options import getOptionManager
from obitools.options.taxonomyfilter import addTaxonomyDBOptions
from obitools.options.taxonomyfilter import loadTaxonomyDatabase

def addUniqOptions(optionManager):
    optionManager.add_option('-m','--merge',
                             action="append", dest="merge",
                             metavar="<TAG NAME>",
                             type="string",
                             default=[],
                             help="attributes to merge")
    
    optionManager.add_option('-c','--category-attribute',
                             action="append", dest="categories",
                             metavar="<Attribute Name>",
                             default=[],
                             help="Add one attribute to the list of"
                                  " attribute used for categorizing sequences")

    optionManager.add_option('-i','--merge-ids',
                             action="store_true", dest="mergeids",
                             default=False,
                             help="don't add the merged id data to output")
    
    optionManager.add_option('-p','--prefix',
                             action="store_true", dest="prefix",
                             default=False,
                             help="two sequences are identical if the shortest one"
                                  " is a prefix of the longest")
    
    
progdoc = "essais"

if __name__=='__main__':
#    try:
#        import psyco
#        psyco.full()
#    except ImportError:
#        pass

#    root.setLevel(DEBUG)

    optionParser = getOptionManager([addUniqOptions,addTaxonomyDBOptions,addInputFormatOption])
    
    (options, entries) = optionParser()

    taxonomy=loadTaxonomyDatabase(options)
    
    if options.prefix:
        usm = uniqPrefixSequence
    else:
        usm= uniqSequence

    uniqSeq=usm(entries,taxonomy,options.merge,options.mergeids,options.categories)
 
    for seq in uniqSeq:         
        print formatFasta(seq) 
