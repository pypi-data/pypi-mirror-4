'''
Created on 6 Nov. 2009

@author: coissac
'''
#@PydevCodeAnalysisIgnore

import sys

from _nwsdnabyprot cimport * 

from obitools.sequenceencoder.geneticcode import TranslationEncoder
from obitools.translate import GeneticCode
from obitools import BioSequence
from obitools.alignment import AlignedSequence
from obitools.alignment import Alignment



cdef CodonAlignMatrix* allocateCodonMatrix(int hsize, int vsize,CodonAlignMatrix *matrix=NULL):
    
    vsize+=1
    hsize+=1
    
    if matrix is NULL:
        matrix = <CodonAlignMatrix*>malloc(sizeof(CodonAlignMatrix))
        matrix.vsize=0
        matrix.hsize=0
        matrix.msize=0
        matrix.matrix=NULL
        matrix.bestVJump=NULL
        matrix.bestHJump=NULL
        
    if hsize > matrix.hsize:
        matrix.bestVJump = <int*>realloc(matrix.bestVJump,hsize * sizeof(int))
        matrix.hsize=hsize
        
    if vsize > matrix.vsize:
        matrix.bestHJump = <int*>realloc(matrix.bestHJump,vsize * sizeof(int))
        matrix.vsize=vsize
        
    if (hsize * vsize) > matrix.msize:
        matrix.msize = hsize * vsize
        matrix.matrix = <CodonAlignCell*>realloc(matrix.matrix, matrix.msize * sizeof(CodonAlignCell))
        
    return matrix

cdef void freeCodonMatrix(CodonAlignMatrix* matrix):
    if matrix is not NULL:
        if matrix.matrix is not NULL:
            free(matrix.matrix)
        if matrix.bestVJump is not NULL:
            free(matrix.bestVJump)
        if matrix.bestHJump is not NULL:
            free(matrix.bestHJump)
        free(matrix)
        
cdef void resetCodonMatrix(CodonAlignMatrix* matrix):
    if matrix is not NULL:
        if matrix.matrix is not NULL:
            bzero(<void*>matrix.matrix, matrix.msize * sizeof(CodonAlignCell))
        if matrix.bestHJump is not NULL:
            memset(<void*>matrix.bestHJump,255,matrix.vsize * sizeof(int))
        if matrix.bestVJump is not NULL:
            memset(<void*>matrix.bestVJump,255,matrix.hsize * sizeof(int))


cdef double iupacPartialCodonMatch(char[3] c1, char[3] c2):
    return (iupacPartialMatch(c1[0],c2[0]) +
            iupacPartialMatch(c1[1],c2[1]) +
            iupacPartialMatch(c1[2],c2[2])) / 3.0

cdef class NWSDNAByProt(DynamicProgramming):
            
    def __init__(self,match=4,
                      mismatch=-6,
                      opengap=-8,
                      extgap=-2,
                      geneticCode=None,
                      startingFrame=0):
        DynamicProgramming.__init__(self,opengap,extgap)
        self._match=match
        self._mismatch=mismatch
        
        if geneticCode is None:
            self._gc = TranslationEncoder()
        else:
            self._gc = GeneticCode
            
        self._sframe = startingFrame
        
    cdef double aaScore(self,char aa1,char aa2):
        if aa1==aa2 or aa1=='X' or aa2=='X':
            return self._match
        else:
            return self._mismatch
        
    
        
    cdef void getPossibleCodon(self,char[3] codon,int h, int v,int frame):
        cdef CodonAlignMatrix* matrix
        cdef CodonAlignCell* smatrix 
        cdef int path
        cdef int vv
        
        matrix = <CodonAlignMatrix*>self.matrix
        smatrix= matrix.matrix
        path   = smatrix[self.index(h,v)].path
        
        
        if frame == 0:
            codon[0]=self.vSeq.sequence[v-1]
            if v < (self.vSeq.length):
                codon[1]=self.vSeq.sequence[v]
            else:
                codon[1]='*'
            if v < (self.vSeq.length-1):
                codon[2]=self.vSeq.sequence[v+1]
            else:
                codon[2]='*'
            
        elif frame==1 :
            vv=v
            if v>1:
                if path==0:
                    vv-=1
                while(path!=0):
                    if path < 0:
                        vv+=path
                    else:
                        h-=path 
                    path   = smatrix[self.index(h,vv)].path
                codon[0]=self.vSeq.sequence[vv-1]
            else:
                codon[0]='*'
            codon[1]=self.vSeq.sequence[v-1]
            if v < (self.vSeq.length):
                codon[2]=self.vSeq.sequence[v]
            else:
                codon[2]='*'
        else:
            vv=v
            if v>1:
                if path==0:
                    vv-=1
                while(path!=0):
                    if path < 0:
                        vv+=path
                    else:
                        h-=path 
                    path   = smatrix[self.index(h,vv)].path
                codon[1]=self.vSeq.sequence[vv-1]
                vv-=1
                h-=1
                path   = smatrix[self.index(h,vv)].path
            else:
                codon[1]='*'
            if v>2:
                if path==0:
                    vv-=1
                while(path!=0):
                    if path < 0:
                        vv+=path
                    else:
                        h-=path 
                    path   = smatrix[self.index(h,vv)].path
                codon[0]=self.vSeq.sequence[vv-1]
                codon[0]=self.vSeq.sequence[v-3]
            else:
                codon[0]='*'
            codon[2]=self.vSeq.sequence[v-1]

        
    cdef double matchScore(self,int h, int v, int qframe):
        cdef double score
        cdef int frame
        cdef char[3] codon
        cdef char[3] qcodon
        cdef char aa
        cdef char qaa
        
        frame=((h - 1 + self._sframe) % 3)
        
                        # extract reference codon
                        
        if frame==0:
            codon[0]=self.hSeq.sequence[h-1]
            if h < (self.hSeq.length):
                codon[1]=self.hSeq.sequence[h]
            else:
                codon[1]='*'
            if h < (self.hSeq.length-1):
                codon[2]=self.hSeq.sequence[h+1]
            else:
                codon[2]='*'
        elif frame==1 :
            if h>1:
                codon[0]=self.hSeq.sequence[h-2]
            else:
                codon[0]='*'
            codon[1]=self.hSeq.sequence[h-1]
            if h < (self.hSeq.length):
                codon[2]=self.hSeq.sequence[h]
            else:
                codon[2]='*'
        else:
            if h>2:
                codon[0]=self.hSeq.sequence[h-3]
            else:
                codon[0]='*'
            if h>1:
                codon[1]=self.hSeq.sequence[h-2]
            else:
                codon[1]='*'
            codon[2]=self.hSeq.sequence[h-1]
            
        aa=ord(self._gc[str(codon)])
            
        self.getPossibleCodon(qcodon,h,v,qframe)
        qaa=ord(self._gc[str(qcodon)])
        score = iupacPartialMatch(self.hSeq.sequence[h-1],self.vSeq.sequence[v-1])
        score = self._match * score + self._mismatch * (1-score) + self.aaScore(aa,qaa)

#        print >>sys.stderr, h,frame,chr(aa),chr(codon[0])+chr(codon[1])+chr(codon[2]),  
#        print >>sys.stderr, chr(qaa),chr(qcodon[0])+chr(qcodon[1])+chr(qcodon[2]), score

        return score
        
    cdef double doAlignment(self) except? 0:
        cdef int i  # vertical index
        cdef int j  # horizontal index
        cdef int idx
        cdef int jump
        cdef int delta
        cdef double score 
        cdef double scoremax
        cdef int    path
        cdef int    frame
        cdef bint   sframe
        cdef int fframe
        cdef CodonAlignMatrix* matrix
        cdef CodonAlignCell* smatrix 
        
        cdef fscost=-10

        
        if self.needToCompute:
            self.allocate()
            self.reset()
            
            matrix = <CodonAlignMatrix*>self.matrix
            smatrix= matrix.matrix
            smatrix[0].frame=(self._sframe-1) % 3
            
            for j in range(1,self.hSeq.length+1):
                idx = self.index(j,0)
                smatrix[idx].score = self._opengap + (self._extgap * (j-1))
                smatrix[idx].path  = j
                smatrix[idx].frame = smatrix[0].frame
                                
            for i in range(1,self.vSeq.length+1):
                idx = self.index(0,i)
                smatrix[idx].score = self._opengap + (self._extgap * (i-1))
                smatrix[idx].path  = -i
                smatrix[idx].frame = smatrix[0].frame
                
            for i in range(1,self.vSeq.length+1):
                for j in range(1,self.hSeq.length+1):
                    
                    # 1 - came from diagonal
                    idx = self.index(j-1,i-1)
                    fframe=smatrix[idx].frame
                    fframe=(fframe + 1) % 3
                    # print "computing cell : %d,%d --> %d/%d" % (j,i,self.index(j,i),self.matrix.msize),
                    scoremax = smatrix[idx].score + \
                               self.matchScore(j,i,0) + \
                               (fframe > -1 and fframe != 0) * fscost
                    path = 0
                    frame= 0

                    score    = smatrix[idx].score + \
                               self.matchScore(j,i,1) + \
                               (fframe > -1 and fframe != 1) * fscost
                    if score > scoremax or (fframe==1 and score==scoremax): 
                        scoremax = score
                        frame = 1

                    score    = smatrix[idx].score + \
                               self.matchScore(j,i,2) + \
                               (fframe > -1 and fframe != 2) * fscost
                    if score > scoremax or (fframe==2 and score==scoremax) : 
                        scoremax = score
                        frame = 2
                        
                    # print >>sys.stderr,j,i,frame,scoremax
                    # print "so=%f sd=%f sm=%f" % (self.matrix.matrix[idx].score,self.matchScore(j,i),scoremax),

                    # 2 - open horizontal gap
                    idx = self.index(j-1,i)
                    score = smatrix[idx].score + \
                            self._opengap
                    if score > scoremax : 
                        scoremax = score
                        path = +1
                        frame= smatrix[idx].frame
                    
                    # 3 - open vertical gap
                    idx = self.index(j,i-1)
                    score = smatrix[idx].score + \
                            self._opengap
                    if score > scoremax : 
                        scoremax = score
                        path = -1
                        frame= smatrix[idx].frame

                    # 4 - extend horizontal gap
                    jump = matrix.bestHJump[i]
                    if jump >= 0:
                        idx = self.index(jump,i)
                        delta = j-jump
                        score = smatrix[idx].score + \
                                self._extgap * delta
                        if score > scoremax :
                            scoremax = score
                            path = delta+1 
                            frame= smatrix[idx].frame
                            
                    # 5 - extend vertical gap
                    jump = matrix.bestVJump[j]
                    if jump >= 0:
                        idx = self.index(j,jump)
                        delta = i-jump
                        score = smatrix[idx].score + \
                                self._extgap * delta
                        if score > scoremax :
                            scoremax = score
                            path = -delta-1 
                            frame= smatrix[idx].frame
    
                    idx = self.index(j,i)
                    smatrix[idx].score = scoremax
                    smatrix[idx].path  = path 
                    smatrix[idx].frame = frame 
                    
                    if path == -1:
                        matrix.bestVJump[j]=i
                    elif path == +1 :
                        matrix.bestHJump[i]=j
                    
        self.sequenceChanged=False
        self.scoreChanged=False

        idx = self.index(self.hSeq.length,self.vSeq.length)
        return smatrix[idx].score
                   
    cdef void backtrack(self):
        #cdef list path=[]
        cdef int i
        cdef int j 
        cdef int p
        cdef CodonAlignMatrix* matrix
        cdef CodonAlignCell* smatrix 

       
        self.doAlignment()
        
        matrix = <CodonAlignMatrix*>self.matrix
        smatrix= matrix.matrix
            
        i=self.vSeq.length
        j=self.hSeq.length
        self.path=allocatePath(i,j,self.path)
        
        while (i or j):
            p=smatrix[self.index(j,i)].path
            self.path.path[self.path.length]=p
            self.path.length+=1
            #path.append(p)
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
                           
    property match:
        def __get__(self):
            return self._match
        
        def __set__(self,match):
            self._match=match 
            self.scoreChanged=True
            
    property mismatch:
        def __get__(self):
            return self._mismatch
        
        def __set__(self,mismatch):
            self._mismatch=mismatch 
            self.scoreChanged=True
 
    cdef int allocate(self) except -1:
        
        assert self.horizontalSeq is not None,'Sequence A must be set'
        assert self.verticalSeq is not None,'Sequence B must be set'
        
        cdef long lenH=self.hSeq.length
        cdef long lenV=self.vSeq.length

        self.matrix=<AlignMatrix*>allocateCodonMatrix(lenH,lenV,<CodonAlignMatrix*>self.matrix)
        return 0

    cdef void reset(self):
        self.scoreChanged=True
        resetCodonMatrix(<CodonAlignMatrix*>self.matrix)
        
    cdef void clean(self):
        freeCodonMatrix(<CodonAlignMatrix*>self.matrix)
        freeSequence(self.hSeq)
        freeSequence(self.vSeq)
        freePath(self.path)

    def __call__(self):
        cdef list hgaps=[]
        cdef list vgaps=[]
        cdef list vframe=[]
        cdef list b
        cdef int  hp=0
        cdef int  vp=0
        cdef int  lenh=0
        cdef int  lenv=0
        cdef int  h,v,p
        cdef int  i
        cdef object ali
        cdef double score
        cdef CodonAlignMatrix* matrix
        cdef CodonAlignCell* smatrix 

        
        if self._needToCompute():
            score = self.doAlignment()
            self.backtrack()
            
            h=self.path.hStart
            v=self.path.vStart
            matrix = <CodonAlignMatrix*>self.matrix
            smatrix= matrix.matrix
            
            
            for i in range(self.path.length-1,-1,-1):
                p=self.path.path[i]
                if p==0:
                    hp+=1
                    vp+=1
                    lenh+=1
                    lenv+=1
                    v+=1
                    h+=1
                    vframe.append(smatrix[self.index(h,v)].frame)
                elif p>0:
                    hp+=p
                    lenh+=p
                    vgaps.append([vp,p])
                    vp=0
                    h+=p
                    #vframe.extend(['*']*p)
                else:
                    vp-=p
                    lenv-=p
                    hgaps.append([hp,-p])
                    hp=0
                    v-=p
                    vframe.extend([smatrix[self.index(h,v)].frame]*-p)
                
            if hp:
                hgaps.append([hp,0])
            if vp:
                vgaps.append([vp,0])
                
            if lenh < self.hSeq.length:
                hseq=self.horizontalSeq[self.path.hStart:self.path.hStart+lenh]
            else:
                hseq=self.horizontalSeq
            
            hseq=AlignedSequence(hseq) 
            hseq.gaps=hgaps       
            
            if lenv < self.vSeq.length:
                vseq=self.verticalSeq[self.path.vStart:self.path.vStart+lenv]
            else:
                vseq=self.verticalSeq
    
            vseq=AlignedSequence(vseq) 
            vseq.gaps=vgaps       
                        
            ali=Alignment()
            ali.append(hseq)
            ali.append(vseq)
            
            ali.score=score
            self.alignment=ali
        ali=self.alignment.clone()
        ali[1]['frame']=vframe
        ali.score=self.alignment.score
        return ali
        
           

