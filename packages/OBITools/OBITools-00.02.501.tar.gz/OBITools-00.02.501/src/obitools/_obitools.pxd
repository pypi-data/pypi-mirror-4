cdef extern from "strings.h":
     void *memchr(char *s, int c, int n)

cdef public bytes __default_raw_parser = b" %s *= *([^;]*);"


cdef class BioSequence(object):
    
    cdef object __quality
    cdef public bytes __seq
    cdef public int   __len
    cdef public bytes __rawinfo
    cdef public dict  _info
    cdef public bytes _rawparser
    cdef public bytes _definition
    cdef public bytes _id
    cdef public bint _hasTaxid
    cdef public object _wrappers
    cdef public object word4table
    cdef public int word4over

    cpdef bytes get_seq(self)
    cpdef set_seq(self, object value)
    cpdef object clone(self)
    cpdef bytes getDefinition(self)
    cpdef setDefinition(self, bytes value)
    cpdef bytes getId(self)
    cpdef setId(self, bytes value)
    cpdef bytes getStr(self)
    cpdef getSymbolAt(self, int position)
    cpdef object getSubSeq(self, object location)
    cpdef object getKey(self, bytes key)
    cpdef extractTaxon(self)
    cpdef bint hasKey(self,bytes key)
    cpdef list items(self)
    cpdef list keys(self)
    cpdef dict getTags(self)
    cpdef object getRoot(self)
    cpdef int _getTaxid(self)
    cpdef _setTaxid(self,int taxid)
    cpdef bytes _getRawInfo(self)
    
cdef class NucSequence(BioSequence):
    cpdef object complement(self)
    cpdef bint isNucleotide(self)
    
cdef class AASequence(BioSequence):
    cpdef bint isNucleotide(self)
    
cdef class WrappedBioSequence(BioSequence):

    cdef object _wrapped
    cdef object __weakref__
        
    cpdef object clone(self)
    cpdef object getWrapped(self)
    cpdef bytes getDefinition(self)
    cpdef setDefinition(self, bytes value)
    cpdef bytes getId(self)
    cpdef setId(self, bytes value)
    cpdef bint isNucleotide(self)
    cpdef object getKey(self,bytes key)
    cpdef bint hasKey(self,bytes key)
    cpdef getSymbolAt(self, int position)
    cpdef int posInWrapped(self, int position, object reference=?   ) except *
    cpdef  int _posInWrapped(self, int position) except *
    cpdef bytes getStr(self)
    cpdef object getRoot(self)
    cpdef object complement(self)    
    cpdef bytes _getRawInfo(self)

cdef int _sign(int x)

cdef class SubSequence(WrappedBioSequence):

    cdef public object _location
    cdef public object _indices
    cdef public object _xrange

    cpdef bytes getId(self)
    cpdef setId(self, bytes value)
    cpdef object clone(self)
    cpdef bytes getStr(self)
    cpdef int _posInWrapped(self, int position) except *

cdef class DNAComplementSequence(WrappedBioSequence):

    cdef dict _comp
    
    cpdef bytes getId(self)
    cpdef setId(self, bytes value)
    cpdef bytes getStr(self)
    cpdef int _posInWrapped(self, int position)
    cpdef  getSymbolAt(self, int position)
    cpdef object complement(self)
    
cpdef bint _isNucSeq(bytes text)
 
cdef object _bioSeqGenerator(bytes id,
                             bytes seq,
                             bytes definition,
                             bytes rawinfo,
                             bytes rawparser,
                             dict info)
 
    
 
    
    
