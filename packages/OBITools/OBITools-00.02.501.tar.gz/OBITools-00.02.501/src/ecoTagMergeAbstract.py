#!/usr/local/bin/python

import sys
import re

from obitools.options import getOptionManager
from obitools.options import currentInputFileName
from obitools.ecotag.parser import EcoTagAbstractIterator
from obitools.ecotag.parser import ecoTagAbstractFilter

def addAbstractOptions(optionManager):
    
    optionManager.add_option('-c','--count-mode',
                             action="store_true", dest="count",
                             default=False,
                             help="Matrix with sequence count")

    optionManager.add_option('-n','--name',
                             action="store", dest="name",
                             metavar="<REGEX>",
                             type="string",
                             default='(.*)',
                             help="")

if __name__=='__main__':
    
    optionParser = getOptionManager([addAbstractOptions],
                                    entryIterator=EcoTagAbstractIterator
                                    )
    
    (options, entries) = optionParser()
    
    namematcher = re.compile(options.name)
    
    results = {}
    current = None

    fulltaxon = set()

    
    for r in ecoTagAbstractFilter(entries):
        name = namematcher.findall(currentInputFileName())[0]
        
        if name != current:
            print >>sys.stderr,"Reading sample : %s" % name
            current=name
            
        if name in results:
            results[name][r['scientific_name']]=r
        else:
            results[name]={r['scientific_name']:r}
            
        fulltaxon.add(r['scientific_name'])
        
    samples=results.keys()
    samples.sort()
    fulltaxon = list(fulltaxon)
    fulltaxon.sort()
    
    header = '\t'.join(fulltaxon)   
    print  header
    
    for s in samples:
        data = []
        for t in fulltaxon:
            if options.count:
                if t in results[s]:
                    data.append(str(results[s][t]['count']))
                else:
                    data.append('0')
            else:
                if t in results[s]:
                    data.append('TRUE')
                else:
                    data.append('FALSE')
        print '\t'.join([s]+data) 

            
        
    
