'''
Created on 16 Feb. 2011

@author: celine
'''
#@PydevCodeAnalysisIgnore

from _gprofilenws cimport *


cdef class GProfileNWS(ProfileNWS):
        
    cdef double matchScore(self,int h, int v):
        cdef double pmatch
        cdef double* hp = self.hProf.frequency
        cdef double* vp = self.vProf.frequency
        cdef int     hl = self.hProf.length
        cdef int     vl = self.vProf.length
        
        h-=1
        v-=1
        pmatch =  hp[h]*vp[v] + \
                  hp[h+hl]*vp[v+vl] + \
                  hp[h+2*hl]*vp[v+2*vl] + \
                  hp[h+3*hl]*vp[v+3*vl] + \
                  hp[h+4*hl]*vp[v+4*vl] + \
                  hp[h+5*hl]*vp[v+5*vl]
        return self._match * pmatch + (1-pmatch) * self._mismatch


    def __call__(self,pseudocounts=0):

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
        cdef DNAProfile newProfile1
        cdef DNAProfile newProfile2
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
                    
            newProfile1 = DNAProfile(size=sum,pseudo=pseudocounts)
            newProfile1.profile.weight = horizontalSeq.profile.weight
            
            newProfile2 = DNAProfile(size=sum,pseudo=pseudocounts)
            newProfile2.profile.weight = verticalSeq.profile.weight

            hp=horizontalSeq.profile.length-1
            vp=verticalSeq.profile.length-1
            rp1=newProfile1.profile.length-1
            rp2=newProfile2.profile.length-1
            
            for i in range(self.path.length):
                p=self.path.path[i]
            
            for i in range(self.path.length):
                p=self.path.path[i]
                
                if p==0:
                    
                    newProfile1.A[rp1] = horizontalSeq.A[hp]
                    newProfile1.C[rp1] = horizontalSeq.C[hp]
                    newProfile1.G[rp1] = horizontalSeq.G[hp]
                    newProfile1.T[rp1] = horizontalSeq.T[hp]
                    newProfile1.Og[rp1] = horizontalSeq.Og[hp]
                    newProfile1.Eg[rp1] = horizontalSeq.Eg[hp]
                    
                    newProfile2.A[rp2] = verticalSeq.A[vp]
                    newProfile2.C[rp2] = verticalSeq.C[vp]
                    newProfile2.G[rp2] = verticalSeq.G[vp]
                    newProfile2.T[rp2] = verticalSeq.T[vp]
                    newProfile2.Og[rp2] = verticalSeq.Og[vp]
                    newProfile2.Eg[rp2] = verticalSeq.Eg[vp]
                
                    hp-=1
                    vp-=1
                    rp1-=1
                    rp2-=1
                
                elif p>0:

                    for x in xrange(p-1) :
                        
                        newProfile1.A[rp1] = horizontalSeq.A[hp]
                        newProfile1.C[rp1] = horizontalSeq.C[hp]
                        newProfile1.G[rp1] = horizontalSeq.G[hp]
                        newProfile1.T[rp1] = horizontalSeq.T[hp]
                        newProfile1.Og[rp1] = horizontalSeq.Og[hp]
                        newProfile1.Eg[rp1] = horizontalSeq.Eg[hp]
                        
                        newProfile2.Eg[rp2] = verticalSeq.profile.weight
                    
                        hp-=1
                        rp1-=1
                        rp2-=1
              
                    newProfile1.A[rp1] = horizontalSeq.A[hp]
                    newProfile1.C[rp1] = horizontalSeq.C[hp]
                    newProfile1.G[rp1] = horizontalSeq.G[hp]
                    newProfile1.T[rp1] = horizontalSeq.T[hp]
                    newProfile1.Og[rp1] = horizontalSeq.Og[hp]
                    newProfile1.Eg[rp1] = horizontalSeq.Eg[hp]
                    
                    newProfile2.Og[rp2] = verticalSeq.profile.weight
                    
                    hp-=1
                    rp1-=1
                    rp2-=1
              
                else:
                    
                    for x in xrange(abs(p)-1) :
            
                        newProfile2.A[rp2] = verticalSeq.A[vp]
                        newProfile2.C[rp2] = verticalSeq.C[vp]
                        newProfile2.G[rp2] = verticalSeq.G[vp]
                        newProfile2.T[rp2] = verticalSeq.T[vp]
                        newProfile2.Og[rp2] = verticalSeq.Og[vp]
                        newProfile2.Eg[rp2] = verticalSeq.Eg[vp]
                        
                        newProfile1.Eg[rp1] = horizontalSeq.profile.weight
                        
                        vp-=1
                        rp1-=1
                        rp2-=1
                    
                    newProfile2.A[rp2] = verticalSeq.A[vp]
                    newProfile2.C[rp2] = verticalSeq.C[vp]
                    newProfile2.G[rp2] = verticalSeq.G[vp]
                    newProfile2.T[rp2] = verticalSeq.T[vp]
                    newProfile2.Og[rp2] = verticalSeq.Og[vp]
                    newProfile2.Eg[rp2] = verticalSeq.Eg[vp]
                    
                    newProfile1.Og[rp1] = horizontalSeq.profile.weight
                    
                    vp-=1
                    rp1-=1
                    rp2-=1
            
            self.alignment1 = newProfile1
            self.alignment2 = newProfile2
                
        ali1=DNAProfile(self.alignment1,pseudo=pseudocounts)
        ali2=DNAProfile(self.alignment2,pseudo=pseudocounts)
    
        return ali1, ali2

