#!/usr/local/bin/python
'''
Created on 13 oct. 2009

@author: coissac
'''

from obitools.options.taxonomyfilter import addTaxonomyDBOptions,loadTaxonomyDatabase
from obitools.options import getOptionManager
from obitools.ecopcr.taxonomy import ecoTaxonomyWriter

 
def editTaxonomyOptions(optionManager):
    optionManager.add_option('-a','--add-taxon',
                             action="append", dest="newtaxon",
                             metavar="<taxon_name>:rank:parent",
                             default=[],
                             help="Add a new taxon to the taxonomy. The new taxon "
                                  "is described by tree values separated by colon. "
                                  "the scientific name, the rank of the new taxon, "
                                  "the taxid of the parent taxon")
    
    optionManager.add_option('-D','--delete-local-taxon',
                             action="append", dest="deltaxon",
                             metavar="<taxid>",
                             default=[],
                             help="Erase a local taxon")

    optionManager.add_option('-s','--add-species',
                             action="append", dest="newspecies",
                             metavar="<species name>",
                             default=[],
                             help="Add a new species to the taxonomy. The new species "
                                  "is described by its scientific name")
    
    optionManager.add_option('-f','--add-favorite-name',
                             action="append", dest="newname",
                             metavar="<taxon_name>:taxid",
                             default=[],
                             help="Add a new favorite name to the taxonomy. The new name "
                                  "is described by two values separated by colon. "
                                  "the new favorite name and the taxid of the taxon")
                             
    optionManager.add_option('-m','--min-taxid',
                             action="store", dest="taxashift",
                             type="int",
                             metavar="####",
                             default=10000000,
                             help="minimal taxid for the newly added taxid")
                             

if __name__ == '__main__':
    
    optionParser = getOptionManager([addTaxonomyDBOptions,editTaxonomyOptions])

    (options, entries) = optionParser()
    
    loadTaxonomyDatabase(options)
    
    localdata=False
    
    for t in options.newtaxon:
        tx = t.split(':')
        taxid = options.taxonomy.addLocalTaxon(tx[0].strip(),tx[1],tx[2],options.taxashift)
        taxon = options.taxonomy.findTaxonByTaxid(taxid)
        parent= options.taxonomy._taxonomy[taxon[2]]
        print "added : %-40s\t%-15s\t%-8d\t->\t%s [%d] (%s)" % (taxon[3],options.taxonomy._ranks[taxon[1]],
                                                     taxon[0],
                                                     parent[3],parent[0],options.taxonomy._ranks[parent[1]])
        localdata=True
    
#    for t in options.deltaxon:
#        tx = int(t)
#        taxon = options.taxonomy.removeLocalTaxon(tx)
#        print "removed : %-40s\t%-15s\t%-8d" % (taxon[3],options.taxonomy._ranks[taxon[1]],
#                                                     taxon[0])
#        localdata=True
        
    for t in options.newspecies:
        genus,species = t.split(" ",1)
        parent = options.taxonomy.findTaxonByName(genus)
        taxid = options.taxonomy.addLocalTaxon(t,'species',parent[0],options.taxashift)
        taxon = options.taxonomy.findTaxonByTaxid(taxid)
        parent= options.taxonomy._taxonomy[taxon[2]]
        print "added : %-40s\t%-15s\t%-8d\t->\t%s [%d] (%s)" % (taxon[3],options.taxonomy._ranks[taxon[1]],
                                                     taxon[0],
                                                     parent[3],parent[0],options.taxonomy._ranks[parent[1]])
        localdata=True

    for n in options.newname:
        tx = t.split(t,':')
        taxid = options.taxonomy.addPreferedName(tx[0].strip(),tx[1])
        print "name : %8d\t->\t%s" % (taxid,options.taxonomy.getPreferedName(taxid))
             
    ecoTaxonomyWriter(options.ecodb,options.taxonomy,onlyLocal=True)
    