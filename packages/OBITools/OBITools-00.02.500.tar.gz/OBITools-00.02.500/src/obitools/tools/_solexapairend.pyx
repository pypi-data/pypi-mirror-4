# cython: profile=False


from obitools.tools.solexapairend import iterOnAligment
from array import array
from obitools import NucSequence

cimport array


cdef class IterOnConsensus:

    cdef object _ali
    cdef int __seqASingle
    cdef int __seqBSingle
    cdef int __seqABMatch
    cdef int __seqAMismatch
    cdef int __seqBMismatch
    cdef int __seqAInsertion
    cdef int __seqBInsertion
    cdef int __seqADeletion
    cdef int __seqBDeletion
    cdef object __ioa 
    cdef bint __firstSeqB

    def __cinit__(self,ali):
        self._ali=ali
        self.__seqASingle=0
        self.__seqBSingle=0
        self.__seqABMatch=0
        self.__seqAMismatch=0
        self.__seqBMismatch=0
        self.__seqAInsertion=0
        self.__seqBInsertion=0
        self.__seqADeletion=0
        self.__seqBDeletion=0
        
        self.__ioa = iterOnAligment(self._ali)
        self.__firstSeqB=False

    def get_seqASingle(self):
        return self.__seqASingle


    def get_seqBSingle(self):
        return self.__seqBSingle


    def get_seqABMatch(self):
        return self.__seqABMatch


    def get_seqAMismatch(self):
        return self.__seqAMismatch


    def get_seqBMismatch(self):
        return self.__seqBMismatch


    def get_seqAInsertion(self):
        return self.__seqAInsertion


    def get_seqBInsertion(self):
        return self.__seqBInsertion


    def get_seqADeletion(self):
        return self.__seqADeletion


    def get_seqBDeletion(self):
        return self.__seqBDeletion
    
    def __next__(self):
        cdef bytes snuc0
        cdef bytes snuc1
        cdef char* nuc0
        cdef char* nuc1
        cdef char* dash='-'
        cdef double score0
        cdef double score1
        cdef double h0
        cdef double h1
        
        while(1):
            snuc0,score0,snuc1,score1 = self.__ioa.next()
            nuc0=snuc0
            nuc1=snuc1
            if nuc0[0]==nuc1[0]: 
                if nuc1[0]!=dash[0]:
                    self.__firstSeqB=True
                    self.__seqABMatch+=1
                    self.__seqBSingle=0
                    return (nuc0,score0*score1)
            else:
                h0 = score0 * (1-score1/3)
                h1 = score1 * (1-score0/3)
                if h0 < h1:
                    
                    if nuc0[0]!=dash[0]:
                        self.__seqBSingle=0
                        if nuc1[0]==dash[0]:
                            if self.__firstSeqB:
                                self.__seqAInsertion+=1
                            else:
                                self.__seqASingle+=1
                        else:
                            self.__firstSeqB=True
                            self.__seqAMismatch+=1
                        return (nuc0,h0)
                    else:
                        self.__seqADeletion+=1
                else:
                    if nuc1[0]!=dash[0]:
                        self.__firstSeqB=True
                        if nuc0[0]==dash[0]:
                            self.__seqBInsertion+=1
                            self.__seqBSingle+=1
                        else:
                            self.__seqBMismatch+=1
                            self.__seqBSingle=0
                        return (nuc1,h1)
                    else:
                        self.__seqBSingle=0
                        self.__seqBDeletion+=1

    
    def __iter__(self):
        return self
    
    seqASingle = property(get_seqASingle, None, None, "direct's docstring")
    seqBSingle = property(get_seqBSingle, None, None, "reverse's docstring")
    seqABMatch = property(get_seqABMatch, None, None, "idem's docstring")
    seqAMismatch = property(get_seqAMismatch, None, None, "mismatchdirect's docstring")
    seqBMismatch = property(get_seqBMismatch, None, None, "mismatchreverse's docstring")
    seqAInsertion = property(get_seqAInsertion, None, None, "insertdirect's docstring")
    seqBInsertion = property(get_seqBInsertion, None, None, "insertreverse's docstring")
    seqADeletion = property(get_seqADeletion, None, None, "deletedirect's docstring")
    seqBDeletion = property(get_seqBDeletion, None, None, "deletereverse's docstring")


def buildConsensus(ali):
    cdef array.array[double] quality = array.array('d',[0])
    cdef array.array[char]   aseq    = array.array('c',' ')
    cdef double* dquality
    cdef char*   cseq
    cdef int i=0
    cdef char* cnuc
    cdef bytes nuc
    cdef double score
    cdef str sseq
    
    array.resize(quality,len(ali[0]))
    array.resize(aseq,len(ali[0]))
    dquality = quality._d
    cseq     = aseq._c
    
    ic=IterOnConsensus(ali)

    for nuc,score in ic:
        cnuc=nuc
        dquality[i]=score
        cseq[i]=cnuc[0]
        i+=1
        
    array.resize(quality,i)
    array.resize(aseq,i)
    
    sseq=''.join(aseq)
    seq=NucSequence(ali[0].wrapped.id+'_CONS',sseq,**ali[0].wrapped.getTags())
    seq.quality=quality
    
    if hasattr(ali, "direction"):
        seq['direction']=ali.direction
    if hasattr(ali, "counter"):
        seq['alignement_id']=ali.counter
    seq['seqASingle']=ic.seqASingle
    seq['seqBSingle']=ic.seqBSingle
    seq['seqABMatch']=ic.seqABMatch
    seq['seqAMismatch']=ic.seqAMismatch
    seq['seqBMismatch']=ic.seqBMismatch
    seq['seqAInsertion']=ic.seqAInsertion
    seq['seqBInsertion']=ic.seqBInsertion-ic.seqBSingle
    seq['seqADeletion']=ic.seqADeletion
    seq['seqBDeletion']=ic.seqBDeletion
    seq['score']=ali.score
    seq['ali_length']=len(seq)-ic.seqASingle-ic.seqBSingle
    if seq['ali_length']>0:
        seq['score_norm']=float(ali.score)/seq['ali_length']
    seq['mode']='alignement'
    return seq
