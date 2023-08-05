from _nws cimport *

cdef class CodonNWS(NWS):
    #cdef double* _aamatrix
    cdef int _phasedA
    cdef int _phasedB

    cdef double matchCodon(self,int h, int v)
    cdef double doAlignment(self) except? 0
    cdef void backtrack(self)
    cdef inline int colindex(self, int idx)        
    cdef inline int rowindex(self, int idx)


             
