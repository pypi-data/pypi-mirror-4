'''
Created on 6 Nov. 2009

@author: coissac
'''
#@PydevCodeAnalysisIgnore

from _dynamic cimport *  
from array import array
cimport array

from obitools import BioSequence
from _upperbond cimport *
#from libupperbond import buildTable

cdef array.array[unsigned char] newtable():
    table = array.array('B',[0])
    array.resize(table,256)
    return table


def indexSequences(seq,double threshold=0.95):
    cdef bytes sequence
    cdef array.array[unsigned char] table
    cdef int overflow
    cdef int wordcount
    cdef int wordmin
    
    table = newtable() 
    sequence=bytes(str(seq))
    overflow = buildTable(sequence,table._B,&wordcount)
    wordmin = threshold4(wordcount,threshold)
    return (table,overflow,wordmin)

cpdef int countCommonWords(array.array table1,
                       int overflow1,
                       array.array table2,
                       int overflow2):
    return compareTable(table1._B,overflow1,
                        table2._B,overflow2)
 
cpdef bint isLCSReachable(object seq1,
                          object seq2,
                          double minimum,
                          bint normalized=False, 
                          bint large=True):
                          
    cdef bytes se1
    cdef bytes se2
    cdef int l1 = len(seq1)
    cdef int l2 = len(seq2)
    cdef array.array[unsigned char] w1
    cdef array.array[unsigned char] w2
    cdef int o1
    cdef int o2
    cdef int wordcount
    cdef bint possible

    cdef char *s1
    cdef char *s2

    if isinstance(seq1, BioSequence) and seq1.word4table is not None:
        w1 = seq1.word4table
        o1 = seq1.word4over
    else:
        se1=bytes(str(seq1))
        s1=se1
        
        w1 = newtable() 
        o1 = buildTable(s1,w1._B,&wordcount)
        if isinstance(seq1, BioSequence):
            seq1.word4table=w1
            seq1.word4over=o1
            
    if isinstance(seq2, BioSequence) and seq2.word4table is not None:
        w2 = seq2.word4table
        o2 = seq2.word4over
    else:
        se2=bytes(str(seq2))
        s2=se2
        
        w2 = newtable() 
        o2 = buildTable(s2,w2._B,&wordcount)
        if isinstance(seq2, BioSequence) :
            seq2.word4table=w2
            seq2.word4over=o2
            
    possible = ispossible(l1, w1._B, o1,
                          l2, w2._B, o2,
                          minimum,normalized,large)

    return possible 

