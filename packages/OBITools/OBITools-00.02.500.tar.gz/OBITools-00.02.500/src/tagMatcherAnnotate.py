#!/usr/local/bin/python

import sys


from obitools.utils import ColumnFile
from obitools.utils import universalOpen
from obitools.location import locationGenerator

from obitools.format.sequence.embl import emblIterator


from obitools.options import getOptionManager



def addAnnotateOptions(optionManager):
        
    optionManager.add_option('-i','--input-data',
                             action="store", dest="data",
                             type="string",
                             metavar="<FILENAME>",
                             help="file containing tagMatcher data in tabulated format")
    
    optionManager.add_option('-f','--feature',
                             action="append", dest="feature",
                             type="string",
                             metavar="<FT_TYPE>",
                             help="feature types to take into account in mapping process")
    
    optionManager.add_option('-q','--qualifier',
                             action="append", dest="qualifier",
                             type="string",
                             metavar="<QUALIFIER>",
                             help="qualifier to report into the output file")
    
def locationEndCmp(l1,l2):    
    if l1.end > l2.end:
        return -1
    if l1.end < l2.end:
        return 1
    return 0

if __name__=='__main__':

    optionParser = getOptionManager([addAnnotateOptions],
                                    entryIterator=emblIterator
                                    )
    
    (options, entries) = optionParser()
    
    annotations = {}
    
    print >>sys.stderr,"Read ensembl embl file..."
    
    j=0
    
    print >>sys.stderr,"================================="
    for s in entries:
        j+=1
        id = s.id
        features = [x for x in s.getFeatureTable()
                    if x.ftType in options.feature]
        
        for f in features:
            qs = f.keys()
            for q in qs:
                if q not in options.qualifier:
                    del f[q]

        fd = [x for x in features if x.isDirect()]
        fr = [x for x in features if not x.isDirect()]
        
        fd.sort()
        fr.sort(locationEndCmp)
        
        print >>sys.stderr,"seq : %s (%d)                               \r" % (id,j),
        annotations[id]=(fd,fr)
    
    print >>sys.stderr,"\n================================="

    
    print >>sys.stderr,"Read tagMatcher tab file...",
    datafile = universalOpen(options.data)   
    data = ColumnFile(datafile, '\t', True, (str,))
    colunmName = data.next()

    colunmName = colunmName[0:3]+['ftype','locus','distance','in_feature']+options.qualifier+colunmName[3:]   
    
    print '\t'.join(colunmName)

    data = ColumnFile(datafile, '\t', True, (str,str,str,locationGenerator,int))
    
    for match in data:
        l = match[3]
        match[3]=str(l)
        id=match[2]
        good=None
        dist=None
        if l.isDirect():
            fd = annotations[id][0]
            for f in fd:
                if f.begin <= l.begin :
                    good = f
            if good is not None:
                dist = l.begin - good.end
        elif not l.isDirect():
            fr = annotations[id][1]
            for f in fr:
                if (f.end - l.end) > 0  :
                    good=f
            if good is not None:
                dist= good.begin - l.end
        
        if good is None:
            fttype='--'
            locus ='--'
            dist  ='NULL'
            descr =['--'] * len(options.qualifier)
            infeat='NULL'
        else:
            fttype=good.ftType
            locus=good.locStr()
            dist =str(dist)
            descr = []
            infeat = {True:'TRUE',False:'FALSE'}[(l.begin >= good.begin and l.end <= good.end)]
            
            for q in options.qualifier:
                if q in good:
                    descr.append(' ; '.join([str(x) for x in good[q]]))
                else:
                    descr.append('--')
            
        match = match[0:3]+[fttype,locus,dist,infeat]+descr+match[3:]
        match = [str(x) for x in match]
        print '\t'.join(match)
                    
    print >>sys.stderr,"  Ok"
        
        
