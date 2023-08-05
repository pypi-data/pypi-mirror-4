'''
Created on 14 mai 2009

@author: coissac
'''

from obitools import WrappedBioSequence

class HomoNucBioSeq(WrappedBioSequence):
    '''
    classdocs
    '''


    def __init__(self,reference,id=None,definition=None,**info):
        '''
        Constructor
        '''
        assert reference.isNucleotide(),"reference must be a nucleic sequence"
        WrappedBioSequence.__init__(self,reference,id=None,definition=None,**info)
        self.__cleanHomopolymer()
        
    def __cleanHomopolymer(self):
        s = []
        c = []
        old=None
        nc=0
        for n in self._wrapped:
            if old is not None and n!=old:
                s.append(old)
                c.append(nc)
                nc=0 
                old=n
            nc+=1
        self._cached=''.join(s)
        self['homopolymer']=c
        self._cumulative=[]
        sum=0
        for c in self._count:
            sum+=c
            self._cumulative.append(sum)

    def __len__(self):
        return len(self._cached)
    
    def getStr(self):
        return self._cached
    
    def __iter__(self):
        return iter(self._cached)
    
    def _posInWrapped(self,position):
        return self._cumulative[position]
            
        
    