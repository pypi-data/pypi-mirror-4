'''
Created on 17 mai 2010

@author: coissac
'''

from obitools.alignment import columnIterator


def iterOnAligment(ali):
    pos0=0
    pos1=len(ali[1].wrapped)-1
    begin0=False
    end0=False
    begin1=False
    end1=False
    for nuc0,nuc1 in columnIterator(ali):
        if nuc0=='-':
            if begin0:
                if not end0:
                    score0 = ( ali[0].wrapped.quality[pos0-1]
                              +ali[0].wrapped.quality[pos0]
                             )/2
                else:
                    score0 = 1.
            else:
                score0 = 0.
        else:
            begin0=True
            score0 = ali[0].wrapped.quality[pos0]
            pos0+=1
            end0= pos0==len(ali[0].wrapped)
            
        if nuc1=='-':
            if begin1:
                if not end1:
                    score1 = ( ali[1].wrapped.wrapped.quality[pos1]
                              +ali[1].wrapped.wrapped.quality[pos1+1]
                             )/2
                else:
                    score1 = 0.
            else:
                score1 = 1.
        else:
            begin1=True
            score1 = ali[1].wrapped.wrapped.quality[pos1]
            pos1-=1
            end1=pos1<0
        
        result = (nuc0,score0,nuc1,score1)
        yield result    
