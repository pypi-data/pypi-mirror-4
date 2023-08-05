'''
Created on 30 oct. 2011

@author: coissac
'''

from obitools.ecopcr.options import addTaxonomyDBOptions


def addMetabarcodingOption(optionManager):
    
    addTaxonomyDBOptions(optionManager)
    
    optionManager.add_option('--dcmax',
                             action="store", dest="dc",
                             metavar="###",
                             type="int",
                             default=0,
                             help="Maximum confusion distance considered")
    
    optionManager.add_option('--ingroup',
                             action="store", dest="ingroup",
                             metavar="###",
                             type="int",
                             default=1,
                             help="ncbi taxid delimitation the in group")

    optionManager.add_option('--rank-thresold',
                             action="store", dest="rankthresold",
                             metavar="#.##",
                             type="float",
                             default=0.5,
                             help="minimum fraction of the ingroup sequences "
                                  "for concidering the rank")
