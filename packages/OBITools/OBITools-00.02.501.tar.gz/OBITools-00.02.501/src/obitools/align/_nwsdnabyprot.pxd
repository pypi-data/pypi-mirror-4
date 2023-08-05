from _dynamic cimport *

cdef struct CodonAlignCell :
    double score
    int   path 
    int   frame

cdef struct CodonAlignMatrix :
    CodonAlignCell*  matrix
    int*        bestVJump
    int*        bestHJump
    int         msize
    int         vsize
    int         hsize

cdef CodonAlignMatrix* allocateCodonMatrix(int hsize, int vsize,CodonAlignMatrix *matrix=?)
cdef void freeCodonMatrix(CodonAlignMatrix* matrix)
cdef void resetCodonMatrix(CodonAlignMatrix* matrix)

cdef double iupacPartialCodonMatch(char[3] c1, char[3] c2)

cdef class NWSDNAByProt(DynamicProgramming):
    cdef double _match
    cdef double _mismatch
    cdef int _sframe
    cdef object _gc
    
    cdef void getPossibleCodon(self,char[3] codon,int h,int v,int frame)    
    cdef double aaScore(self,char aa1,char aa2)
    cdef double matchScore(self,int h, int v, int qframe)
    cdef double doAlignment(self) except? 0
    cdef void reset(self)
    cdef int allocate(self) except -1
    cdef void clean(self)

             
