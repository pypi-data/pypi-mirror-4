from cpython.dict  cimport *
from cpython.int   cimport PyInt_FromLong
from cpython.float cimport PyFloat_FromDouble
from cpython.bytes cimport PyBytes_FromStringAndSize, \
                           PyBytes_AS_STRING, \
                           PyBytes_Check
                           
from cpython.list cimport PyList_GET_SIZE,PyList_GET_ITEM
from cpython.tuple cimport PyTuple_GET_SIZE,PyTuple_GET_ITEM
                           
from cpython.string cimport PyString_Check
                           
from libc.stdlib cimport strtol
from libc.stdlib cimport strtod
from libc.stdlib cimport free
from libc.stdlib cimport malloc,realloc
from libc.string cimport strncmp,strcmp
from libc.string cimport strcpy
from libc.string cimport memset

cdef extern from "stdio.h":
    int asprintf(char **ret, char *format, ...)
    int snprintf(char *s, int n, char *format, ...)
    int printf(char *format, ...)
    

cdef extern from "regex.h":
    ctypedef struct regex_t:
        int re_nsub
    
    ctypedef long regoff_t 
    
    enum :
        REG_EXTENDED
    
    ctypedef struct regmatch_t:
        regoff_t rm_so          # start of match 
        regoff_t rm_eo          # end of match         
    
    int regcomp(regex_t* re, char *pattern, int flag)
    int regexec(regex_t* preg, char *string, int nmatch,
                regmatch_t* pmatch, int eflags)
    void regfree(regex_t *preg)

cdef class AbstractTag(dict):
    cdef char* __pchar(self,char *buffer,Py_ssize_t *size,Py_ssize_t *pos)
    cdef int __itemsnext(self,Py_ssize_t *pos,PyObject** key,PyObject** value)
    cdef PyObject* _getitemstring(self,char* ckey)
    cdef bint __hasKey(self, char* ckey)
    cdef int _delitemstring(self,char* ckey)
    cdef void _setitemstring(self,char *ckey, object value)
    cdef int _length(self)
    cdef void _clear(self)



cdef class Tag(AbstractTag):

    cdef char* _raw            # A pointer to the set of unparsed attributes
    cdef int   _lraw           # the length of the _raw string
    cdef bint  _localraw       # True if memory is allocated to store _raw
    
    cdef bint     _defParser   # True if the parser used is the default one
    cdef char*    _kparser
    cdef regex_t  _rparser
    cdef regex_t* _prparser
    
    cdef object _eval(self,char* svalue,int length)
    cdef PyObject* _extractitem(self, char* ckey)
    cdef int __compact_raw__(self,char* dest=?)
    cdef bint __hasKey(self, char* ckey)
    cdef int __itemsnext(self,Py_ssize_t *pos,PyObject** key,PyObject** value)
    cdef PyObject* _getitemstring(self,char* ckey)
    cdef int _delitemstring(self,char* ckey)
    cdef void _setitemstring(self,char *ckey, object value)
    cdef char* __pchar(self,char *buffer,Py_ssize_t *size,Py_ssize_t *pos)
    cdef int _length(self)
    cdef void _clear(self)


    
cdef class WrappedTag(AbstractTag):

    cdef dict _deleted
    cdef AbstractTag _wrapped

    cdef bint __hasKey(self, char* ckey)
    cdef char* __pchar(self,char *buffer,Py_ssize_t *size,Py_ssize_t *pos)
    cdef PyObject* _getitemstring(self,char* ckey)
    cdef int _delitemstring(self,char* ckey)
    cdef int __itemsnext(self,Py_ssize_t *pos,PyObject** key,PyObject** value)
  
    