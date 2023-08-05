'''
Created on 6 Nov. 2009

@author: coissac
'''
#@PydevCodeAnalysisIgnore

from obitools import BioSequence
from _lcs cimport *
from _upperbond cimport *
from _dynamic cimport *  

from _upperbond import *

cdef class LCS(DynamicProgramming):
            
    def __init__(self):
        DynamicProgramming.__init__(self,opengap=0,extgap=0)

    property opengap:
        def __get__(self):
            return self._opengap
        
    property extgap:
        def __get__(self):
            return self._extgap
        
    cdef double matchScore(self,int h, int v):
        return iupacPartialMatch(self.hSeq.sequence[h-1],self.vSeq.sequence[v-1])
        
    cdef double doAlignment(self) except? 0:
        cdef int i  # vertical index
        cdef int j  # horizontal index
        cdef int idx
        cdef int jump
        cdef int delta
        cdef double score
        cdef double scoremax
        cdef int    path

        
        if self.needToCompute:
            self.allocate()
            self.reset()
            
            for j in range(1,self.hSeq.length+1):
                idx = self.index(j,0)
                self.matrix.matrix[idx].score = 0
                self.matrix.matrix[idx].path  = j
                                
            for i in range(1,self.vSeq.length+1):
                idx = self.index(0,i)
                self.matrix.matrix[idx].score = 0
                self.matrix.matrix[idx].path  = -i
                
            for i in range(1,self.vSeq.length+1):
                for j in range(1,self.hSeq.length+1):
                    
                    # 1 - came from diagonal
                    idx = self.index(j-1,i-1)
                    # print "computing cell : %d,%d --> %d/%d" % (j,i,self.index(j,i),self.matrix.msize),
                    scoremax = self.matrix.matrix[idx].score + \
                               self.matchScore(j,i)
                    path = 0

                    # print "so=%f sd=%f sm=%f" % (self.matrix.matrix[idx].score,self.matchScore(j,i),scoremax),

                    # 2 - open horizontal gap
                    idx = self.index(j-1,i)
                    score = self.matrix.matrix[idx].score
                    if score > scoremax : 
                        scoremax = score
                        path = self.matrix.matrix[idx].path
                        if path >=0:
                            path+=1
                        else: 
                            path=+1
                    
                    # 3 - open vertical gap
                    idx = self.index(j,i-1)
                    score = self.matrix.matrix[idx].score 
                    if score > scoremax : 
                        scoremax = score
                        path = self.matrix.matrix[idx].path
                        if path <=0:
                            path-=1
                        else:
                            path=-1
                        
                    idx = self.index(j,i)
                    self.matrix.matrix[idx].score = scoremax
                    self.matrix.matrix[idx].path  = path 
                                        
        self.sequenceChanged=False
        self.scoreChanged=False

        idx = self.index(self.hSeq.length,self.vSeq.length)
        return self.matrix.matrix[idx].score
                   
    cdef void backtrack(self):
        #cdef list path=[]
        cdef int i
        cdef int j 
        cdef int p
        
        self.doAlignment()
        i=self.vSeq.length
        j=self.hSeq.length
        self.path=allocatePath(i,j,self.path)
        
        while (i or j):
            p=self.matrix.matrix[self.index(j,i)].path
            self.path.path[self.path.length]=p
            self.path.length+=1
#            path.append(p)
            if p==0:
                i-=1
                j-=1
            elif p < 0:
                i+=p
            else:
                j-=p
                
        #path.reverse()
        #reversePath(self.path)
        self.path.hStart=0
        self.path.vStart=0
        #return 0,0,path
        
ALILEN=0
MAXLEN=1
MINLEN=2
                           
def lenlcs(seq1,seq2,double minimum=0.,bint normalized=False, int reference=ALILEN):
    cdef double lcs
    cdef bytes se1=bytes(str(seq1))
    cdef bytes se2=bytes(str(seq2))
    cdef int l1 = len(seq1)
    cdef int l2 = len(seq2)
    cdef array.array[unsigned char] w1
    cdef array.array[unsigned char] w2
    cdef int o1
    cdef int o2
    cdef int wordcount
    cdef int alilength
    cdef bint possible
    cdef bint large

    cdef char *s1
    cdef char *s2
    s1=se1
    s2=se2
    
    if min(l1,l2) < 8:
        lcsali = LCS()
        lcsali.seqA = seq1
        lcsali.seqB = seq2
        lcs = lcsali.doAlignment()
    else:
        if minimum > 0.:
            if isinstance(seq1, BioSequence) and hasattr(seq1, "word4table"):
                w1 = seq1.word4table
                o1 = seq1.word4over
            else:
                w1 = newtable() 
                o1 = buildTable(s1,w1._B,&wordcount)
                if isinstance(seq1, BioSequence):
                    seq1.word4table=w1
                    seq1.word4over=o1
            if isinstance(seq2, BioSequence) and hasattr(seq2, "word4table"):
                w2 = seq2.word4table
                o2 = seq2.word4over
            else:
                w2 = newtable() 
                o2 = buildTable(s2,w2._B,&wordcount)
                if isinstance(seq2, BioSequence) :
                    seq2.word4table=w2
                    seq2.word4over=o2
            large = reference==ALILEN or reference==MAXLEN
            possible = ispossible(l1, w1._B, o1,
                                  l2, w2._B, o2,
                                  minimum,normalized,large)
            if possible:
                lcs = fastLCSScore(s1,s2,NULL,&alilength)
            else:
                lcs = -1.0
        else:
            lcs = fastLCSScore(s1,s2,NULL,&alilength)
            
    if lcs >= 0 and normalized:
        if reference==ALILEN:
            if alilength > 0:
                lcs /=alilength
            else:
                lcs = 0
        elif reference==MAXLEN:
            lcs /=max(l1,l2)
        elif reference==MINLEN:
            lcs /=min(l1,l2)
        
    return lcs,alilength
           

