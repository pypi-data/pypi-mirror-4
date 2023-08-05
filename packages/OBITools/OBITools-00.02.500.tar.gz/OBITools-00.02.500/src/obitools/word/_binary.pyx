'''
Created on 2 juil. 2009

@author: coissac
'''


maxword = sizeof(unsigned long int) * 8 /2

cdef import from "math.h":
    double ceil(double x)
    double log(double x)

cdef int binarywordsize(unsigned long int x):
    return <int>ceil(log(x)/log(2))

cpdef str bin2str(unsigned long int x):
    cdef str rep=''
    cdef unsigned long int i
    cdef int ws = binarywordsize(x)
    
    for i in range(ws):
        if x & (1 << i):
            rep = '1' + rep
        else:
            rep = '0' + rep
    return rep
    


cdef class WordPattern :
    cdef public unsigned long int a 
    cdef public unsigned long int c 
    cdef public unsigned long int g 
    cdef public unsigned long int t 
    
    
    def __init__(self, unsigned long int a,
                       unsigned long int c,
                       unsigned long int g,
                       unsigned long int t):
        self.a=a
        self.c=c 
        self.g=g 
        self.t=t 
        
    def __str__(self):
        return b"(a:%s,c:%s,g:%s,t:%s)" % (bin2str(self.a),
                                           bin2str(self.c),
                                           bin2str(self.g),
                                           bin2str(self.t))
        
cdef unsigned int bitCount(unsigned long int x):
    cdef unsigned int i=0
    while(x):
        i+=1
        x&=x-1
    return i
        
def allDNAWordIterator(size):
    '''
    Iterate thought the list of all DNA word of
    size `size`.
    
    @param size: size of the DNA word
    @type size: int
    
    @return: an iterator on DNA word (int)
    @rtype: iterator
    '''
    
    maxi=4**size
    return xrange(maxi)

cpdef int wordDist(unsigned long int w1,unsigned long int w2):
    '''
    estimate Hamming distance between two words of the same size.
    
    @param w1: the first word
    @type w1:  str
    @param w2: the second word
    @type w2:  str
    
    @return: the count of difference between the two words
    @rtype: int
    '''
    cdef unsigned long int diff
    cdef unsigned long int dist
    
    diff = (~(w1 & w2) & (w1 | w2))
    diff = (diff | (diff >> 1)) & 0x55555555 
    dist = bitCount(diff)
    return dist

cpdef int homoMax(unsigned long int word,unsigned int size):
    cdef unsigned long int mask
    cdef unsigned long int good
    cdef unsigned long int maxi
    cdef unsigned long int shift
    
    mask = (1 << (size << 1))-1
    good = 0x55555555
    maxi=0
    shift = word
    while good:
        maxi+=1
        shift>>=2
        mask>>=2
        id = (word & shift) | (~word & ~shift)
        good&= id & (id>>1) & mask
    return maxi

cpdef int countA(unsigned long int word,unsigned int size):
    cdef unsigned long int mask
    cdef unsigned long int id
    cdef unsigned long int good
    mask = (1 << (size << 1))-1
    id = ~word
    good= id & (id>>1) & 0x55555555 & mask
    return bitCount(good)

cpdef int countT(unsigned long int word,unsigned int size):
    cdef unsigned long int good
    
    good= word & (word>>1) & 0x55555555
    return bitCount(good)

cpdef int countAT(unsigned long int word,unsigned int size):
    cdef unsigned long int mask
    cdef unsigned long int shift
    cdef unsigned long int good
    
    mask = (1 << (size << 1))-1
    shift = word >> 1
    good  = ((word & shift) | (~word & ~shift)) & 0x55555555 & mask
    return bitCount(good)

cpdef int countC(unsigned long int word,unsigned int size):
    cdef unsigned long int mask
    cdef unsigned long int good
    
    mask = (1 << (size << 1))-1
    good = ((word & 0x55555555) | (~word & 0xAAAAAAAA)) 
    good &= (good >> 1) & 0x55555555 & mask
    return bitCount(good)

cpdef int countG(unsigned long int word,unsigned int size):
    cdef unsigned long int mask
    cdef unsigned long int good
    
    mask = (1 << (size << 1))-1
    good  = ((word & 0xAAAAAAAA) | (~word & 0x55555555))  
    good &= (good >> 1) & 0x55555555 & mask
    return bitCount(good)

cpdef int countCG(unsigned long int word,unsigned int size):
    cdef unsigned long int mask
    cdef unsigned long int shift
    cdef unsigned long int good
    
    mask = (1 << (size << 1))-1
    shift = word >> 1
    good  = ((word & ~shift) | (~word & shift)) & 0x55555555 & mask
    return bitCount(good)
    
    
cpdef str decodeWord(unsigned long int word,unsigned int size):
    return ''.join(['acgt'[(word >> i) & 3] for i in xrange(size*2-2,-1,-2)])

cpdef int encodeWord(word) except -1:
    assert len(word)<=32,"Word length should be less or equal to 32"
    w=0
    word=word.lower()
    for l in word:
        w<<=2
        if l=='c' :
            w|=1
        elif l=='g':
            w|=2
        elif l=='t':
            w|=3
        elif l!='a':
            raise RuntimeError,"word should only contain a, c, g or t (%s)" % word
    return w
    
def encodePattern(pattern):
    a=0
    c=0
    g=0
    t=0
    
    pattern=pattern.lower()
    
    for l in pattern:
        a<<=2
        c<<=2
        g<<=2
        t<<=2
        if l in 'armwdhvn':
            a|=1
        if l in 'cymsbhvn':
            c|=1
        if l in 'grksbdvn':
            g|=1
        if l in 'tykwbdhn':
            t|=1
            
    return WordPattern(a,c,g,t)

cpdef bint matchPattern(unsigned long int word,pattern):
    all   = pattern.a|pattern.c|pattern.g|pattern.t
    eq    = ~word
    match = eq & (eq >> 1) & pattern.a
    eq    = (word & 0x55555555 | ~word & 0xAAAAAAAA)
    match|= eq & (eq >> 1) & pattern.c
    eq    = (word & 0xAAAAAAAA | ~word & 0x55555555) 
    match|= eq & (eq >> 1) &  pattern.g
    eq    = word
    match|= eq & (eq >> 1) &  pattern.t        
    return match == all

cdef class ErrorPositionIterator:
        
    cdef int _wsize
    cdef int _errors
    cdef unsigned long int _mask
    cdef int _errorpos[32]
    cdef bint _end
    
    def __init__(self,wordsize,errorcount):
        self._wsize=wordsize
        self._errors=errorcount
        self._mask=0
        for i in range(errorcount):
            self._errorpos[i]=i
        self._end=False
            
    def __iter__(self):
        return self
    
    def next(self):
        cdef unsigned long int rep
        cdef bint move=False
        cdef int i
        if self._end:
            raise StopIteration
        
        rep = 0
        for i in range(self._errors):
            rep |= 1 << self._errorpos[i]
            print bin2str(rep)
            
        move=False
        i=0
        while (not move):
            if self._errorpos[i]<self._errorpos[i+1]-1:
                 self._errorpos[i]+=1
                 move=True
                 i=0
                 print "pos %d/%d moved" % (i,self._wsize)
            else:
                self._errorpos[i]=i
                i+=1
            if i==self._errors-1 and self._errorpos[i]==self._wsize:
                self._end=True
                move=True
                
        return rep
    