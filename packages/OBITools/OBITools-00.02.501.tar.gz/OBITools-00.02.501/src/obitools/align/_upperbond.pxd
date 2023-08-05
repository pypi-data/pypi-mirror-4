from array import array
cimport array

cdef extern from *:
    ctypedef char* const_char_ptr "const char*"
    
    
cdef import from "_upperbond.h":
    int buildTable(const_char_ptr sequence, unsigned char *table, int *count)
    int compareTable(unsigned char *t1, int over1, unsigned char* t2,  int over2)
    int threshold4(int wordcount,double identity)
    int thresholdLCS4(int reflen,int lcs)
    bint ispossible(int len1, unsigned char *t1, int over1,
                   int len2, unsigned char* t2, int over2,
                   double minimum, bint normalized, bint large)
                   
cdef array.array[unsigned char] newtable()
