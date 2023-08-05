'''
Created on 9 juin 2012

@author: coissac
'''
from esm import Index
from obitools.format.options import addInOutputOption, sequenceWriterGenerator,\
    autoEntriesIterator
from obitools.options import getOptionManager
from obitools.options._options import allEntryIterator

def addWindowsOptions(optionManager):
    
    optionManager.add_option('-l','--window-length',
                             action="store", dest="length",
                             metavar="<WORD SIZE>",
                             type="int",
                             default=None,
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
                             metavar="<STEP>",
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
        yield(d,r)

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
    
    words = Index()
    
    for rs in reference:
        ft = str(rs)
        rt = str(rs.complement())
        
        if options.circular:
            ft = ft + ft[0:options.length]
            rt = rt + rt[0:options.length]
        
        for x in xrange(0,len(ft),options.step):
            w = ft[x:(x+options.length)]
            if len(w)==options.length:
                words.enter(w)
            w = rt[x:(x+options.length)]
            if len(w)==options.length:
                words.enter(w)
    
    words.fix()
            

    writer = sequenceWriterGenerator(options)
    
    for seq in sequences:
        t = "".join([str(x) for x in seq])
        r = words.query(t)
        if r:
            writer(seq)
