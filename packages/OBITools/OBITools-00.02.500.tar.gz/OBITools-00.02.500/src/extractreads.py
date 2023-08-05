'''
Created on 9 juin 2012

@author: coissac
'''
from obitools.format.options import addInOutputOption, sequenceWriterGenerator,\
    autoEntriesIterator
from obitools.fasta import formatFasta
from obitools.options import getOptionManager
from obitools.options._options import allEntryIterator
from obitools.word._readindex import ReadIndex,minword

import sys
import math
 
def addWindowsOptions(optionManager):
    
    optionManager.add_option('-l','--window-length',
                             action="store", dest="length",
                             metavar="<WORD SIZE>",
                             type="int",
                             default=90,
                             help="size of the sliding window")

    optionManager.add_option('-s','--step',
                             action="store", dest="step",
                             metavar="<STEP>",
                             type="int",
                             default=1,
                             help="position difference between two windows")
    
    optionManager.add_option('-c','--circular',
                             action="store_true", dest="circular",
                             default=False,
                             help="set for circular sequence")

    optionManager.add_option('-R','--reference',
                             action="store", dest="reffile",
                             metavar="<FILENAME>",
                             type="str",
                             default=None,
                             help="sequence file containing the reference sequences")
    
    optionManager.add_option('-r','--reverse-reads',
                             action="store", dest="reverse",
                             metavar="<FILENAME>",
                             type="str",
                             default=None,
                             help="Filename containing reverse solexa reads "
                            )
    
    optionManager.add_option('-D','--write-dump',
                             action="store", dest="wdump",
                             metavar="<FILENAME>",
                             type="str",
                             default=None,
                             help="Save the index to a dump file"
                            )

    optionManager.add_option('-d','--read-dump',
                             action="store", dest="rdump",
                             metavar="<FILENAME>",
                             type="str",
                             default=None,
                             help="Read the index from a dump file"
                            )

    optionManager.add_option('-S','--singleton',
                             action="store", dest="singleton",
                             metavar="<FILENAME>",
                             type="str",
                             default=None,
                             help="Write singleton sequence in this file"
                            )

def cutQuality(s):
    def quantile(x,q=0.1):
        y = list(x)
        y.sort()
        return y[int(q*len(y))]
    
    def cumsum0(x):
        if x[0] < 0: x[0]=0
        for i in xrange(1,len(x)):
            x[i]+=x[i-1]
            if x[i]<0: x[i]=0
        return x
    
    q = [- math.log10(a) * 10 for a in s.quality]
    mq=quantile(q)
    q = cumsum0([a - mq for a in q])
    

    mx = max(q)
    
    xmax = len(q)-1
    
    while(q[xmax] < mx):
        xmax-=1
    
    xmin=xmax
    xmax+=1
    
    while(xmin>0 and q[xmin]>0):
        xmin-=1
        
    if q[xmin]==0:
        xmin+=1
        
    return s[xmin:xmax]
    
    
    
def cutDirectReverse(entries):
    first = []
    
    for i in xrange(10):
        first.append(entries.next())
        
    lens = [len(x) for x in first]
    clen = {}
    for i in lens:
        clen[i]=clen.get(i,0)+1
    freq = max(clen.values())
    freq = [k for k in clen if clen[k]==freq]
    assert len(freq)==1,"To many sequence length"
    freq = freq[0]
    assert freq % 2 == 0, ""
    lread = freq/2
    
    seqs = chain(first,entries)
    
    for s in seqs:
        d = s[0:lread]
        r = s[lread:]
        yield(d,r)
    
def seqPairs(direct,reverse):
    for d in direct:
        r = reverse.next()
        yield(cutQuality(d),cutQuality(r))

    
def seq2words(seqs,options):
    nw=set()
    for seq in seqs:
        s=str(seq)
        
        if options.circular:
            s = s + s[0:options.length]

        ls = len(s) - options.length + 1
 
        for wp in xrange(0,ls,options.step):
            w =minword(s[wp:wp+options.length])
            if len(w)==options.length:
                nw.add(w)              

    return nw
    

if __name__ == '__main__':
    
    optionParser = getOptionManager([addWindowsOptions,addInOutputOption],progdoc=__doc__)
    
    (options, direct) = optionParser()
    
    if options.reverse is None:
        sequences=((x,) for x in direct)
    else:
        reverse = allEntryIterator([options.reverse],options.readerIterator)
        sequences=seqPairs(direct,reverse)
            
    reader = autoEntriesIterator(options)
    rfile = open(options.reffile)
    reference = reader(rfile)
    
    worddone=set()
    wordlist = seq2words(reference,options)
    
    indexer = ReadIndex(readsize=105)
 
    seqpair=0
    nbseq=0
    
    writer = sequenceWriterGenerator(options)

    if options.rdump is None:
        print >>sys.stderr,"Indexing sequences..."
        for seq in sequences:
            indexer.add(seq)

        print >>sys.stderr,"Indexing words..."
        indexer.indexWords(options.length,True)
        
        if options.wdump is not None:
            print >>sys.stderr,"Saving index to file %s..." % options.wdump
            indexer.save(options.wdump,True)
    else:
        print >>sys.stderr,"Loading index dump..."
        indexer.load(options.rdump,True)
        
        
    
    print >>sys.stderr,"Selecting sequences..."
    
    while len(wordlist)>0:
        w = wordlist.pop()
        worddone.add(w)
        
        i=0
        
        #print >>sys.stderr,"Looking for word : %s..." % w
        
        for seq in indexer.iterreads(w):
            i+=1
            #print formatFasta(seq) 
            s  = str(seq)
            sc = str(seq.complement())
            assert w in s or w in sc,'Bug !!!! sequence %s (%d) %s sans %s' % (seq.id,i,s,w)
            words = seq2words((seq,),options) - worddone
            wordlist|=words 

        seqpair+=i
        
        if i:
            print >>sys.stderr,"\rWrote extracted = %d/total = %d/word done = %d [wordlist=%d]" % (i,seqpair,len(worddone),len(wordlist)),
     
    print >>sys.stderr,"\nWriting sequences..."

    for seq in indexer.itermarkedpairs():
        print formatFasta(seq)
      
    if options.singleton is not None:
        s = open(options.singleton,'w')
        for seq in indexer.itermarkedsingleton():
            print >>s,formatFasta(seq)
        s.close()
        
            
            
                    
        
