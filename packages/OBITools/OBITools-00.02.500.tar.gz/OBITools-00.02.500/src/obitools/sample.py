'''
Created on 31 oct. 2009

@author: coissac
'''
from random import randrange, sample
from obitools.utils import Counter

def lookfor(x,cumsum):
    lmax=len(cumsum)
    lmin=0
    
    assert x < cumsum[-1],"x must be smaller then cumulative sum"
    
    while((lmax - lmin) > 0):

        i=(lmax+lmin)/2
        #print i,lmin,lmax
        if (x<cumsum[i] and (i==0 or x>cumsum[i-1])):
            #print "return 1 :",i,cumsum[i-1],"<",x,"<",cumsum[i]
            return i
        elif cumsum[i]==x:
            while cumsum[i]==x:
                i+=1
            #print "return 2 :",i,cumsum[i],"<",x,"<",cumsum[i+1]
            return i
        elif x<cumsum[i]:
            lmax=i
        else:
            lmin=i
            
    raise AssertionError
    #print "end return :",i,cumsum[i-1],"<",x,"<",cumsum[i]
    return i

def weigthedSample(events,size):
    entries = events.keys()
    cumul=[0] * len(entries)
    s=0
    i=0
    for e in entries:
        s+=events[e]
        cumul[i]=s
        i+=1
    
    c = randrange(xrange(s),size)
    c.sort()
    
    i = 0
    for j in xrange(len(c)):
        v = c[j]
        while (v > cumul[i]):
            i+=1
        c[j]=entries[i]
        
    result=Counter(c)

    return result

def weigthedSampleWithoutReplacement(events,size):
    # entries = [k for k in events.iterkeys() if events[k]>0]
    entries = events.keys()
    cumul=[0] * len(entries)
    s=0
    i=0
    for e in entries:
        s+=events[e]
        cumul[i]=s
        i+=1
    
    c = sample(xrange(s),size)
    c.sort()
    
    i = 0
    for j in xrange(len(c)):
        v = c[j]
        while (v > cumul[i]):
            i+=1
        c[j]=entries[i]
        
    result=Counter(c)

    return result