'''
Created on 01 Feb. 2011

@author: celine
'''
#@PydevCodeAnalysisIgnore

from _profilenws cimport *
from obitools.profile._profile import DNAProfile


cdef alignProfile* allocateProfile(object profile, alignProfile* prof=NULL):
    cdef int i,j
    cdef int buffsize
    cdef double* freq
    
    if prof is NULL:
        prof = <alignProfile*>malloc(sizeof(alignProfile))
        prof.length=0
        prof.buffsize=0
        prof.frequency=NULL
    
    prof.length=len(profile)
    buffsize = 6 * prof.length * sizeof(double)
    if buffsize > prof.buffsize:
        prof.frequency = <double*>realloc(prof.frequency,buffsize)
        prof.buffsize = buffsize
      
    freq = prof.frequency
    for i in range(prof.length):
        freq[i]              = profile.fA(i)
        freq[i+prof.length]  = profile.fC(i)
        freq[i+prof.length*2]= profile.fG(i)
        freq[i+prof.length*3]= profile.fT(i)
        freq[i+prof.length*4]= profile.fOg(i)
        freq[i+prof.length*5]= profile.fEg(i)
        
    return prof

cdef void freeProfile(alignProfile* prof):
    if prof is not NULL:
        if prof.frequency is not NULL:
            free(<void*>prof.frequency)
        free(prof)

cdef class ProfileNWS(NWS):
            
    def __init__(self,match=4,mismatch=-6,opengap=-8,extgap=-2):
        DynamicProgramming.__init__(self,opengap,extgap)
        self._match=match
        self._mismatch=mismatch
        self.hProf=NULL
        self.vProf=NULL
        
    cdef double matchScore(self,int h, int v):
        cdef double pmatch
        cdef double* hp = self.hProf.frequency
        cdef double* vp = self.vProf.frequency
        cdef int     hl = self.hProf.length
        cdef int     vl = self.vProf.length
        
        h-=1
        v-=1
        pmatch =  hp[h]*vp[v] + hp[h+hl]*vp[v+vl] + hp[h+2*hl]*vp[v+2*vl] + hp[h+3*hl]*vp[v+3*vl]        
        return self._match * pmatch + (1-pmatch) * self._mismatch

    cdef int _vlen(self):
        return self.vProf.length
        
    cdef int _hlen(self):
        return self.hProf.length
        
        
    property seqA:
            def __get__(self):
                return self.horizontalSeq
            
            def __set__(self, seq):
                self.sequenceChanged=True
                if not isinstance(seq,DNAProfile):
                    seq=DNAProfile(seq)
                self.horizontalSeq=seq
                self.hProf=allocateProfile(seq,self.hProf)
               
    property seqB:
            def __get__(self):
                return self.verticalSeq
            
            def __set__(self, seq):
                self.sequenceChanged=True
                if not isinstance(seq,DNAProfile):
                    seq=DNAProfile(seq)
                self.verticalSeq=seq
                self.vProf=allocateProfile(seq,self.vProf)
                
    cdef void clean(self):
        freeProfile(self.hProf)
        freeProfile(self.vProf)
        freeMatrix(self.matrix)
        freePath(self.path)


    def __call__(self):
        cdef list hgaps=[]
        cdef list vgaps=[]
        cdef list b
        cdef int  hp
        cdef int  vp
        cdef int  rp
        cdef int  lenh=0
        cdef int  lenv=0
        cdef int  h,v,p
        cdef int  i
        cdef object ali
        cdef double score
        cdef DNAProfile newProfile
        cdef DNAProfile horizontalSeq=self.horizontalSeq
        cdef DNAProfile verticalSeq=self.verticalSeq
        
        if self._needToCompute():
            
            score = self.doAlignment()
            self.backtrack()
            
            sum = 0
            for p in xrange(self.path.length) :
                v = self.path.path[p]
                if v == 0 :
                    sum += 1
                else :
                    sum += abs(v)
                    
            newProfile = DNAProfile(size=sum)
            newProfile.profile.weight = horizontalSeq.profile.weight+verticalSeq.profile.weight

            hp=horizontalSeq.profile.length-1
            vp=verticalSeq.profile.length-1
            rp=newProfile.profile.length-1
            
            for i in range(self.path.length):
                p=self.path.path[i]
            
            for i in range(self.path.length):
                p=self.path.path[i]
                
                if p==0:
                    
                    newProfile.A[rp] = horizontalSeq.A[hp] + verticalSeq.A[vp]
                    newProfile.C[rp] = horizontalSeq.C[hp] + verticalSeq.C[vp]
                    newProfile.G[rp] = horizontalSeq.G[hp] + verticalSeq.G[vp]
                    newProfile.T[rp] = horizontalSeq.T[hp] + verticalSeq.T[vp]
                    newProfile.Og[rp] = horizontalSeq.Og[hp] + verticalSeq.Og[vp]
                    newProfile.Eg[rp] = horizontalSeq.Eg[hp] + verticalSeq.Eg[vp]
                
                    hp-=1
                    vp-=1
                    rp-=1
                
                elif p>0:

                    for x in xrange(abs(p)-1) :
                        
                        newProfile.A[rp] = horizontalSeq.A[hp]
                        newProfile.C[rp] = horizontalSeq.C[hp]
                        newProfile.G[rp] = horizontalSeq.G[hp]
                        newProfile.T[rp] = horizontalSeq.T[hp]
                        newProfile.Og[rp] = horizontalSeq.Og[hp]
                        newProfile.Eg[rp] = horizontalSeq.Eg[hp] + verticalSeq.profile.weight
                    
                        hp-=1
                        rp-=1
              
                    newProfile.A[rp] = horizontalSeq.A[hp]
                    newProfile.C[rp] = horizontalSeq.C[hp]
                    newProfile.G[rp] = horizontalSeq.G[hp]
                    newProfile.T[rp] = horizontalSeq.T[hp]
                    newProfile.Og[rp] = horizontalSeq.Og[hp] + verticalSeq.profile.weight
                    newProfile.Eg[rp] = horizontalSeq.Eg[hp]
                    
                    hp-=1
                    rp-=1
              
                else:
                    
                    for x in xrange(abs(p)-1) :
            
                        newProfile.A[rp] = verticalSeq.A[vp]
                        newProfile.C[rp] = verticalSeq.C[vp]
                        newProfile.G[rp] = verticalSeq.G[vp]
                        newProfile.T[rp] = verticalSeq.T[vp]
                        newProfile.Og[rp] = verticalSeq.Og[vp]
                        newProfile.Eg[rp] = verticalSeq.Eg[vp] + horizontalSeq.profile.weight
                        
                        vp-=1
                        rp-=1  
                    
                    newProfile.A[rp] = verticalSeq.A[vp]
                    newProfile.C[rp] = verticalSeq.C[vp]
                    newProfile.G[rp] = verticalSeq.G[vp]
                    newProfile.T[rp] = verticalSeq.T[vp]
                    newProfile.Og[rp] = verticalSeq.Og[vp] + horizontalSeq.profile.weight
                    newProfile.Eg[rp] = verticalSeq.Eg[vp]
                    
                    vp-=1
                    rp-=1
            
            self.alignment = newProfile
                
        ali=DNAProfile(self.alignment)
    
        return ali
