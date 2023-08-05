#!/usr/local/bin/python
'''
Created on 30 dec. 2009

@author: coissac
'''

from obitools.options import getOptionManager

from itertools import chain
from obitools import NucSequence
from obitools.format.options import sequenceWriterGenerator, autoEntriesIterator,\
    addInOutputOption
from obitools.utils import universalOpen

def addPairEndOptions(optionManager):
    optionManager.add_option('-r','--reverse-reads',
                             action="store", dest="reverse",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="Filename containing reverse solexa reads "
                            )
    optionManager.add_option('-j','--junction-length',
                             action="store", dest="junction",
                             metavar="###",
                             type="int",
                             default=10,
                             help="length of the N junction between both the reads (default=10)"
                            )
    optionManager.add_option('-n','--n-quality',
                             action="store", dest="nqual",
                             metavar="###",
                             type="int",
                             default=10,
                             help="quality assign to the N of the junction (default=10)"
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


        
def buildJoinedSequence(sequences,options):
    nqual = 10.**-(options.nqual/10.)
    junction = options.junction
    
    for d,r in sequences:
        r=r.complement()
        
        s = str(d) + 'n' * junction + str(r)
        
        seq = NucSequence(d.id + '_Join',s,d.definition,**d)
        
        withqual = hasattr(d, 'quality') or hasattr(r, 'quality')
        
        if withqual:
            if hasattr(d, 'quality'):
                quality = d.quality
            else:
                quality = [10**-4] * len(d)
                
            quality.extend([nqual] * junction)
            
            if hasattr(r, 'quality'):
                quality.extend(r.quality)
            else:
                quality.extend([10**-4] * len(r))
                
            seq.quality=quality
            
        yield seq
        
    
    
if __name__ == '__main__':
    optionParser = getOptionManager([addPairEndOptions,addInOutputOption])
    
    (options, direct) = optionParser()
    
    if options.reverse is None:
        sequences=cutDirectReverse(direct)
    else:
        reader = autoEntriesIterator(options)
        reverse = reader(universalOpen(options.reverse))
        sequences=seqPairs(direct,reverse)
    
    writer = sequenceWriterGenerator(options)

    for seq in buildJoinedSequence(sequences,options):
        writer(seq)
        
        

