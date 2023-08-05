#!/usr/local/bin/python

import sys
import re
from time import time
from logging import root,DEBUG

from obitools.options import getOptionManager,currentInputFileName

from obitools.solexa import SolexaFile


def addMergeOptions(optionManager):
    
    optionManager.add_option('-n','--name',
                             action="store", dest="name",
                             metavar="<REGEX>",
                             type="string",
                             default='.+',
                             help="regex used to extract condition name from filename")

    optionManager.add_option('-1','--condition_1',
                             action="store", dest="c1",
                             metavar="<CONDITION NAME>",
                             type="string",
                             default=None,
                             help="Name of condition 1")

    optionManager.add_option('-2','--condition_2',
                             action="store", dest="c2",
                             metavar="<CONDITION NAME>",
                             type="string",
                             default=None,
                             help="Name of condition 2")

    optionManager.add_option('-3','--condition_3',
                             action="store", dest="c3",
                             metavar="<CONDITION NAME>",
                             type="string",
                             default=None,
                             help="Name of condition 3")

    optionManager.add_option('-4','--condition_4',
                             action="store", dest="c4",
                             metavar="<CONDITION NAME>",
                             type="string",
                             default=None,
                             help="Name of condition 4")

    optionManager.add_option('-5','--condition_5',
                             action="store", dest="c5",
                             metavar="<CONDITION NAME>",
                             type="string",
                             default=None,
                             help="Name of condition 5")

    optionManager.add_option('-6','--condition_6',
                             action="store", dest="c6",
                             metavar="<CONDITION NAME>",
                             type="string",
                             default=None,
                             help="Name of condition 6")

    optionManager.add_option('-7','--condition_7',
                             action="store", dest="c7",
                             metavar="<CONDITION NAME>",
                             type="string",
                             default=None,
                             help="Name of condition 7")

    optionManager.add_option('-8','--condition_8',
                             action="store", dest="c8",
                             metavar="<CONDITION NAME>",
                             type="string",
                             default=None,
                             help="Name of condition 8")

    optionManager.add_option('-9','--condition_9',
                             action="store", dest="c9",
                             metavar="<CONDITION NAME>",
                             type="string",
                             default=None,
                             help="Name of condition 9")

if __name__=='__main__':

    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([addMergeOptions],
                                    entryIterator=SolexaFile
                                    )
    
    (options, entries) = optionParser()
    
    condname=['',
              options.c1,
              options.c2,
              options.c3,
              options.c4,
              options.c5,
              options.c6,
              options.c7,
              options.c8,
              options.c9,
              ]
    
    
    if options.name:
        options.name=re.compile(options.name)
        
    tags = {}
    cfn=None
    newtags=0
    readseq=0
    readcond=0
    conditions=[]
    start = time()
    for s in entries:
        readseq+=1
        seq = str(s)
        if cfn!=currentInputFileName():
            readcond+=1
            cfn = currentInputFileName()
            if readcond < 10 and condname[readcond]:
                condition=condname[readcond]
            else:
                condition = options.name.findall(cfn)
                if condition:
                    condition=condition[0]
                else:
                    condition=cfn
            conditions.append(condition)
            
        if seq in tags:
            data = tags[seq]
        else:
            newtags+=1
            data={}
            tags[seq]=data
            
        if not readseq % 1000:
            speed = readseq/float(time()-start)
            print >> sys.stderr,"\rReaded : %10d  Tags : %10d  %6.1f tags/s conditions : %2d => %s      " % (readseq,newtags,speed,readcond,condition),
        data[condition]=data.get(condition,0)+1
    print >> sys.stderr
    print >> sys.stderr
    
    title = '\t'.join(['tag'] + conditions)
    
    print title
    
        
    for s in tags:
        print '\t'.join([str(s)]+ ["%-8d" % tags[s].get(x,0) for x in conditions])
        
        
    
    
