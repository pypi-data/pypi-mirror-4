'''
Created on 6 Nov. 2009

@author: coissac
'''
#@PydevCodeAnalysisIgnore

from _freeendgapfm cimport *  


cdef class FreeEndGapFullMatch(FreeEndGap):

    cdef double matchScore(self,int h, int v):
        cdef double score
        if iupacMatch(self.hSeq.sequence[h-1],self.vSeq.sequence[v-1]):
            score=self._match
        else:
            score=self._mismatch
        return score  
