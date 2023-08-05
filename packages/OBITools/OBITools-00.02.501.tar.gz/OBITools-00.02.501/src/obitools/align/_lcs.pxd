cdef extern from *:
    ctypedef char* const_char_ptr "const char*"
    ctypedef int* int32_ptr 
    
    
cdef import from "_lcs.h":
    struct column_t:
        pass    
    int fastLCSScore(const_char_ptr seq1, const_char_ptr seq2,column_t* column,int32_ptr length)
