from itertools import imap
from _binary import *

def wordCount(liste):
    count = {}
    
    for e in liste:
        count[e]=count.get(e,0) + 1
    
    return count


def wordIterator(sequence,lword,step=1,endIncluded=False,circular=False):
    
    assert not (endIncluded and circular), \
      "endIncluded and circular cannot not be set to True at the same time"
      
    L = len(sequence)
    sequence = str(sequence)
    if circular:
        sequence += sequence[0:lword]
        pmax=L
    elif endIncluded:
        pmax=L
    else:
        pmax = L - lword + 1
    
    pos = xrange(0,pmax,step)
    
    for x in pos:
        yield encodeWord(sequence[x:x+lword])

def filterIterator(sequence,step=32,maxword=50,wordsize=4,circular=False):
    
    assert step < 64
    
    wi = wordIterator(sequence, wordsize, circular=circular)
    
    lfilter=0
    winfilter=0
    filter=0
    buffer=[]
    pos=0
    
    for w in wi:
        code = 1 << w
        buffer.append(code)
        if len(buffer)>step:
            buffer.pop(0)
        lfilter+=1
        if not filter & code:
            filter |=code
            winfilter+=1
            if winfilter>=maxword:
                yield (sequence.id,pos,lfilter,filter)
                pos = pos + lfilter - len(buffer)
                filter=0
                lfilter=0
                winfilter=0
                for code in buffer:
                    lfilter+=1
                    if not filter & code:
                        filter |=code
                        winfilter+=1
                buffer=[]
                
    yield (sequence.id,pos,lfilter,filter)
   
def filterDict(sequence,step=32,maxword=50,wordsize=4,circular=False,filters=None):  
    fi = filterIterator(sequence, step, maxword,wordsize, circular)  

    if filters is None:
        r = {}
    else:
        r = filters
        
    for f in fi:
        lseq = r.get(f[2],{})
        r[f[3]]=lseq
        lpos = lseq.get(f[0],[])
        lseq[f[0]]=lpos
        lpos.append((f[1],f[2]))
        
    return r
    
def primerWordMin(lprimer,error=2,lword=4):
    parts = error+1
    match = lprimer - error
    mparts= (match / parts) + 1
    
    if mparts < lword:
        return 0
        
    remains = mparts * parts - match
    
    return (mparts - lword + 1) * parts - remains

def wordSelector(words,accept=None,reject=None):
    '''
    Filter over a DNA word iterator.
    
    @param words: an iterable object other a list of DNA words
    @type words: an iterator
    @param accept: a list of predicate. Each predicate is a function
                   accepting one str parametter and returning a boolean
                   value.
    @type accept: list
    @param reject: a list of predicat. Each predicat is a function
                   accepting one str parametter and returning a boolean
                   value.
    @type reject: list
    
    @return: an iterator on DNA word (str)
    @rtype: iterator
    '''
    if accept is None:
        accept=[]
    if reject is None:
        reject=[]
    for w in words:
#        print [bool(p(w)) for p in accept]
        accepted = reduce(lambda x,y: bool(x) and bool(y),
                          (p(w) for p in accept),
                          True)
#        print [(p.__name__,bool(p(w))) for p in reject]
        rejected = reduce(lambda x,y:bool(x) or bool(y),
                          (p(w) for p in reject),
                          False)
#        print decodeWord(w,5),accepted,rejected,
        if accepted and not rejected:
#            print " conserved"
            yield w
#        else:
#            print

