from _profilenws cimport *

cdef class GProfileNWS(ProfileNWS):

    cdef double matchScore(self,int h, int v)
    cdef object alignment1
    cdef object alignment2
    #cdef double doAlignment(self) except? 0