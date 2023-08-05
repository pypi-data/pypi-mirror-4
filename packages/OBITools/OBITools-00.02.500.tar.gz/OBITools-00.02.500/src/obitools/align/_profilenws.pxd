from _nws cimport *
from obitools.profile._profile cimport *

cdef struct alignProfile:
    long    length
    long    buffsize
    double* frequency

cdef alignProfile* allocateProfile(object profile, alignProfile* prof=?)

cdef void freeProfile(alignProfile* prof)

cdef class ProfileNWS(NWS):

    cdef alignProfile* hProf
    cdef alignProfile* vProf

    cdef double matchScore(self,int h, int v)
    cdef void clean(self)
    
    cdef int _vlen(self)
    cdef int _hlen(self)
    cdef double doAlignment(self) except? 0