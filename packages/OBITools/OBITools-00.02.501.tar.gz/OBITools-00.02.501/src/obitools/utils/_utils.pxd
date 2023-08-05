cdef extern from "stdio.h":
    struct FILE
    int fprintf(FILE *stream, char *format, ...)
    FILE* stderr
    ctypedef unsigned int off_t "unsigned long long"
    
    

cdef extern from "time.h":
    struct tm :
        int tm_yday 
        int tm_hour
        int tm_min
        int tm_sec

    enum: CLOCKS_PER_SEC
    
    ctypedef int time_t
    ctypedef int clock_t
    
    
    tm *gmtime_r(time_t *clock, tm *result)
    time_t time(time_t *tloc)
    clock_t clock()

cdef class FakeFile:

    cdef object _li
    cdef list   __buffer
    cdef int    __bufsize

    cpdef str read(self,int size=?)
    cpdef str readline(self)
    
cpdef object progressBar(object pos,
                         off_t maxi,
                         bint reset=?,
                         bytes head=?,
                         list delta=?,
                         list step=?)

    