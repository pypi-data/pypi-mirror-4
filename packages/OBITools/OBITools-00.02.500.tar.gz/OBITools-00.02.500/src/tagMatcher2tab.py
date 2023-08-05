#!/usr/local/bin/python

import re
import sys

from obitools.tagmatcher.parser import TagMatcherIterator,formatTagMatcher
from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions
from obitools.options.bioseqfilter import sequenceFilterIteratorGenerator

from obitools.tagmatcher.options import addTagMatcherErrorOptions

def addTagMatcherDistanceOptions(optionManager):
    optionManager.add_option('-C','--cluster',
                             action='store',
                             metavar="<##>",
                             type="int",dest="cluster",
                             default=0,
                             help="max distance to be put in the same cluster")

def distmatch(l1,l2):
    if l1.isDirect()==l2.isDirect():
        return abs(l2.begin - l1.begin)
    return None

if __name__=='__main__':
    
    optionParser = getOptionManager([addTagMatcherDistanceOptions,
                                     addSequenceFilteringOptions,
                                     addTagMatcherErrorOptions], 
                                    entryIterator=TagMatcherIterator)
    
    (options, entries) = optionParser()
    goodFasta = sequenceFilterIteratorGenerator(options)
    
#    print formatTagMatcher(entries)

    results = {}
    
    for seq in goodFasta(s.eminEmaxFilter(options.emin,options.emax) for s in entries):
        for l in seq['locations']:
            l['tm']=seq['tm']
            l['cd']=seq['conditions']
            l['tag']=seq
            c = l['contig']
            if c in results:
                results[c].append(l)
            else:
                results[c]=[l]
                
    contigs = results.keys()
    contigs.sort()
    
    cluster = 0
    
    conditions=seq['conditions'].keys()
    conditions.sort()
    tconditions = '\t'.join(conditions)
    
    print "tag\tmatch\tcontig\tlocation\tcluster\ttag_match_count\terror\t"+tconditions
    
    for c in contigs:
        results[c].sort()
        lold=None
        for l in results[c]:
            if lold is None :
                cluster+=1
            else:
                d=distmatch(lold, l)
                if d is None or d > options.cluster:
                    cluster+=1
            exp = ('\t%6d' * len(conditions)) % tuple([l['cd'][cd] for cd in conditions])
                
            print "%s\t%s\t%s\t%s\t%5d\t%2d\t%2d%s" % (str(l['tag']),l['match'],c,l.locStr(),cluster,l['tm'],l['error'],exp)
            lold=l

