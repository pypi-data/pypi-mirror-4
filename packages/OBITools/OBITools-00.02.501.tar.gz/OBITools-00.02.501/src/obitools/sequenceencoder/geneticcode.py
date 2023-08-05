'''
Created on 20 janv. 2011

@author: coissac
'''

from itertools import imap

class TranslationEncoder(object):
    '''
    classdocs
    '''


    def __init__(self,id=1,
                    codon1= 'TTTTTTTTTTTTTTTTCCCCCCCCCCCCCCCCAAAAAAAAAAAAAAAAGGGGGGGGGGGGGGGG',
                    codon2= 'TTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGG',
                    codon3= 'TCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAG',
                    aa    = 'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG',
                    start = '---M---------------M---------------M----------------------------',
                    name=None):
        '''
        Constructor
        '''
        self.aa=[0]*64
        self.start=[0]*64
        
        for n1,n2,n3,a,s in imap(None,codon1,codon2,codon3,aa,start):
            codon = self.hashCodon(n1, n2, n3)
            self.aa[codon]=a
            self.start=s
            
        self.aa=''.join(self.aa)
        self.start=''.join(self.start)
        
    def hashCodon(self,n1,n2,n3):
        if n1=='*' or n2=='*' or n3=='*':
            return -1
        return (self.hashBase(n1) << 4) | (self.hashBase(n2) << 2) | self.hashBase(n3) 
    
    def hashBase(self,n):
        return (ord(n) >> 1) & 3
    
    def __getitem__(self,codon):
        hash = self.hashCodon(codon[0], codon[1], codon[2])
        if hash < 0:
            return 'X'
        else:
            return self.aa[hash]
    
    def isStart(self,codon):
        hash = self.hashCodon(codon[0], codon[1], codon[2])
        return hash >=0 and self.aa[hash]=='M'

        