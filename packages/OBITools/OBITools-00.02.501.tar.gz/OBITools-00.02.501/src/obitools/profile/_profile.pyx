from obitools import NucSequence
from math import log
from _profile cimport *


cdef dnaprofile_t* allocateDNAProfile(int size):
    
    cdef dnaprofile_t* profile 
    cdef int sblock
    profile = <dnaprofile_t*>malloc(sizeof(dnaprofile_t))
    profile.length = size
    profile.weight = 0
    profile.pseudo = 0
    sblock = sizeof(int)*6*size
    profile.A = <int*>malloc(sblock)
    bzero(<void*>profile.A, sblock)
    profile.C = profile.A + size
    profile.G = profile.C + size
    profile.T = profile.G + size
    profile.Og= profile.T + size
    profile.Eg= profile.Og+ size
    
    return profile
    

cdef void freeDNAProfile(dnaprofile_t *profile):
    if profile is not NULL:
        if profile.A is not NULL:
            free(profile.A)

        free(profile)

        
cdef void copyDNAProfile(dnaprofile_t* dest, dnaprofile_t *source):
    cdef int size

    assert source is not NULL and dest is not NULL
    assert source.length==dest.length
    
    size = source.length * 6 * sizeof(int)
    memcpy(dest.A,source.A,size)
    dest.weight=source.weight
    dest.pseudo=source.pseudo
        

cdef class _MemIntArray:

    cdef initialize(self, int* begin,int size):
        self.start=begin
        self.size=size
        
    cdef int normalize(self, int pos):
        if pos < 0:
            pos = self.size + pos
            
        if pos >= self.size or pos < 0:
            raise IndexError

        return pos    
        
    def __init__(self):
        self.start=NULL
        
    def __getitem__(self, int pos):
        pos = self.normalize(pos)   
        return self.start[pos]
    
    def __setitem__(self,int pos, int value):
        pos = self.normalize(pos)   
        self.start[pos]=value   
        
    def __len__(self):
        return self.size
        
    cpdef double frequency(self,int pos, int weight, double pseudo=0):
        pos = self.normalize(pos) 
        if weight==0:
            raise ZeroDivisionError
        pseudo*=weight
        return  (<double>self.start[pos]+ weight * pseudo/6) / (<double>weight + pseudo)


cdef class DNAProfile:

    cdef void _initLetter(self):
        cdef dnaprofile_t* profile = self.profile

        self._A  = _MemIntArray()
        self._A.initialize(profile.A ,profile.length)
        self._C  = _MemIntArray()
        self._C.initialize(profile.C ,profile.length)
        self._G  = _MemIntArray()
        self._G.initialize(profile.G ,profile.length)
        self._T  = _MemIntArray()
        self._T.initialize(profile.T ,profile.length)
        self._Og = _MemIntArray()
        self._Og.initialize(profile.Og,profile.length)
        self._Eg = _MemIntArray()
        self._Eg.initialize(profile.Eg,profile.length)
                
                
    def __init__(self,sequence=None,size=None,pseudo=0):
    
        if sequence is not None:
            size = len(sequence)
            
        self.profile = allocateDNAProfile(size)
        self.profile.pseudo=pseudo
        if sequence is not None:
            if isinstance(sequence,NucSequence):
                seq = str(sequence).lower()
                self._initFromString(seq)
            elif isinstance(sequence,str):
                seq = sequence.lower()
                self._initFromString(seq)
            elif isinstance(sequence,DNAProfile):
                copyDNAProfile(self.profile,(<DNAProfile>sequence).profile)
        
        self._initLetter()

        
    def __dealloc__(self):
        freeDNAProfile(self.profile)
        
    def __hash__(self):
        return id(self)
        
    def __str__(self):
        cdef int i
        cdef int lseq = self.profile.length
        cdef list output=[]
        cdef str  line
        cdef int* A= self.profile.A
        cdef int* C= self.profile.C
        cdef int* G= self.profile.G
        cdef int* T= self.profile.T
        cdef int* Og=self.profile.Og
        cdef int* Eg=self.profile.Eg
        
        for i in range(lseq):
            line = "%6d %6d %6d %6d %6d %6d %6d " % (i,A[i],C[i],G[i],T[i],Og[i],Eg[i])
            output.append(line)
            
        line = "\n".join(output)
        return "  pos       A      C      G      T      Og     Eg\n"+line
    

    def __len__(self):
        return self.profile.length
    
    
    cpdef bint equal(DNAProfile self,DNAProfile profile):
        cdef int sblock
        cdef bint r
        cdef int size
        r=False
        if self.profile.length == profile.profile.length :
            if self.profile.weight == profile.profile.weight :
                size = self.profile.length
                sblock = sizeof(int)*6*size
                r = memcmp(<void*>self.profile.A, <void*>profile.profile.A, sblock) == 0
        return r


    def __richcmp__(DNAProfile self,DNAProfile profile,int op):
        if op==2:
            return self.equal(profile)
        else:
            return NotImplemented


    cpdef DNAProfile add(DNAProfile self,DNAProfile profile):
        cdef DNAProfile newProfile
        cdef int p
        assert self.profile.length==profile.profile.length,'Only profiles with identical length can be added'
        pc = max(self.profile.pseudo,profile.profile.pseudo)
        newProfile = DNAProfile(size=self.profile.length,pseudo=pc)
        for p in xrange(self.profile.length) :
            newProfile.profile.A[p] = self.profile.A[p] + profile.A[p]
            newProfile.profile.C[p] = self.profile.C[p] + profile.profile.C[p]
            newProfile.profile.T[p] = self.profile.T[p] + profile.profile.T[p]
            newProfile.profile.G[p] = self.profile.G[p] + profile.profile.G[p]
            newProfile.profile.Og[p] = self.profile.Og[p] + profile.profile.Og[p]
            newProfile.profile.Eg[p] = self.profile.Eg[p] + profile.profile.Eg[p]
        newProfile.profile.weight = self.profile.weight + profile.profile.weight
        return newProfile


    def __add__(DNAProfile self,DNAProfile profile):
        return self.add(profile)


    cpdef double lproba(DNAProfile self,DNAProfile profile) except 1.:
        cdef float score
        cdef float prob
        cdef int pos
        assert self.profile.length==profile.profile.length,'Only profiles with identical length can be added'
        score = 0
        for pos in xrange(self.profile.length) :
            prob = self.fA(pos)*profile.fA(pos) + \
                   self.fC(pos)*profile.fC(pos) + \
                   self.fT(pos)*profile.fT(pos) + \
                   self.fG(pos)*profile.fG(pos) + \
                   self.fOg(pos)*profile.fOg(pos) + \
                   self.fEg(pos)*profile.fEg(pos)
            #if prob != 0 :
            score += log(prob)
        return score


    cpdef double proba(DNAProfile self,DNAProfile profile) except -1.:
        return exp(self.lproba(profile))


    cdef void _initFromString(self, char *seq):
        cdef int i=0
        cdef int lseq = len(seq)
        cdef int* A= self.profile.A
        cdef int* C= self.profile.C
        cdef int* G= self.profile.G
        cdef int* T= self.profile.T
        cdef int* Og=self.profile.Og
        cdef int* Eg=self.profile.Eg
        
        for i in range(lseq):
            nuc = seq[i]
            if nuc=='a':
                A[i]=1
            elif nuc=='c':
                C[i]=1
            elif nuc=='g':
                G[i]=1
            elif nuc=='t':
                T[i]=1
            elif nuc=='-':
                if i > 0 and seq[i-1]=='-':
                    Eg[i]=1
                else:
                    Og[i]=1
                    
        self.profile.weight = 1
        
    property A:
        def __get__(self):
            return self._A
        
    property C:
        def __get__(self):
            return self._C
        
    property G:
        def __get__(self):
            return self._G
        
    property T:
        def __get__(self):
            return self._T
        
    property Og:
        def __get__(self):
            return self._Og
        
    property Eg:
        def __get__(self):
            return self._Eg
        
     
    cpdef double fA(self,int pos):
        return self.A.frequency(pos,self.profile.weight,self.profile.pseudo)
        
    cpdef double fC(self,int pos):
        return self.C.frequency(pos,self.profile.weight,self.profile.pseudo)
        
    cpdef double fG(self,int pos):
        return self.G.frequency(pos,self.profile.weight,self.profile.pseudo)
        
    cpdef double fT(self,int pos):
        return self.T.frequency(pos,self.profile.weight,self.profile.pseudo)
        
    cpdef double fOg(self,int pos):
        return self.Og.frequency(pos,self.profile.weight,self.profile.pseudo)
        
    cpdef double fEg(self,int pos):
        return self.Eg.frequency(pos,self.profile.weight,self.profile.pseudo)
    
    
    cpdef int WP(self):
        return self.profile.weight
        
