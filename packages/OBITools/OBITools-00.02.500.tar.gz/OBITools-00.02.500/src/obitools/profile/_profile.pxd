
cdef import from "stdlib.h":
    void* malloc(int size)  except NULL
    void* realloc(void* chunk,int size)  except NULL
    void free(void* chunk)
    
cdef import from "string.h":
    void bzero(void *s, size_t n)
    void memset(void* chunk,int car,int length)
    void memcpy(void* s1, void* s2, int n)
    int memcmp(void* s1, void* s2, int n)
    
cdef import from "math.h":
    double exp(double x)
    
cdef extern from *:
    ctypedef int* int_p "int*"

    
cdef struct dnaprofile_t:
    int     length
    int     weight
    int value
    double  pseudo
    int_p   A
    int_p   C
    int_p   G
    int_p   T
    int_p   Og
    int_p   Eg
    
    
cdef dnaprofile_t* allocateDNAProfile(int size)
cdef void freeDNAProfile(dnaprofile_t* profile)
cdef void copyDNAProfile(dnaprofile_t* dest, dnaprofile_t* source)

cdef class _MemIntArray:
    
    cdef    int_p   start
    cdef    int     size
    
    cdef initialize(self, int_p start,int size)
    cdef int normalize(self, int pos)
    cpdef double frequency(self,int pos, int weight, double pseudo=?)


cdef class DNAProfile:

    cdef dnaprofile_t* profile
    cdef _MemIntArray _A
    cdef _MemIntArray _C
    cdef _MemIntArray _G
    cdef _MemIntArray _T
    cdef _MemIntArray _Og
    cdef _MemIntArray _Eg
    
    cpdef bint equal(self,DNAProfile profile)
    cpdef DNAProfile add(DNAProfile self,DNAProfile profile)
    cpdef double lproba(DNAProfile self,DNAProfile profile) except 1.
    cpdef double proba(DNAProfile self,DNAProfile profile) except -1.
    
    cdef void _initLetter(self)
    cdef void _initFromString(self, char *seq)
    
    cpdef double fA(self,int pos)
    cpdef double fC(self,int pos)
    cpdef double fG(self,int pos)
    cpdef double fT(self,int pos)
    cpdef double fOg(self,int pos)
    cpdef double fEg(self,int pos)
    
    cpdef int WP(self)