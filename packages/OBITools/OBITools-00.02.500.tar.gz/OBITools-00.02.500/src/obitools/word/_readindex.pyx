from libc.stdlib cimport free
from libc.stdlib cimport malloc,realloc
from libc.stdio cimport fopen,fclose,fread,fwrite,FILE
from libc.string cimport strlen 
from cpython.bytes cimport PyBytes_FromString
from cpython.bytes cimport PyBytes_FromStringAndSize

import sys

from threading import Lock
from cPickle import dumps,loads

from obitools._obitools import NucSequence
from turtle import Tbuffer

cdef extern from "_readindex.h":
    ctypedef char obinuc        
    ctypedef obinuc* pobinuc

    obinuc SET_SEQUSED(char x)
    obinuc SET_ENDOFREAD(char x)
    obinuc SET_ZERO(char x)
    obinuc SET_DIRECTION(char x)

    obinuc UNSET_SEQUSED(char x)
    obinuc UNSET_ENDOFREAD(char x)
    obinuc UNSET_ZERO(char x)
    obinuc UNSET_DIRECTION(char x)
    
    
    obinuc SET_REVERSE(char x, unsigned int val)
    obinuc SET_FORWARD(char x, unsigned int val)

    unsigned int GET_SEQUSED(obinuc x)
    unsigned int GET_ENDOFREAD(obinuc x)
    unsigned int GET_ZERO(obinuc x)
    unsigned int GET_DIRECTION(obinuc x)
    unsigned int GET_REVERSE(obinuc x)
    unsigned int GET_FORWARD(obinuc x)

    char DECODE_NUC(obinuc x)
    char DECODE_NUC_FR(obinuc x, unsigned int d)

    enum:
        A 
    enum:
        C 
    enum:
        G 
    enum:
        T 
    enum:
        N 

cdef extern from *:
    ctypedef void* pconstvoid "const void*"

cdef extern from "stdlib.h":
    void heapsort(void *base, size_t nel, size_t  width, int (*compar)(pconstvoid, pconstvoid))
    void qsort(void *base, size_t nel, size_t  width, int (*compar)(pconstvoid, pconstvoid))
    void* bsearch(pconstvoid key, pconstvoid base, size_t nel, size_t width, int (*compar) (pconstvoid, pconstvoid))

cdef obinuc encodeobinuc(char nuc):    
    nuc&=0b11011111
    if nuc=='A':
        return A
    elif nuc=='C':
        return C
    elif nuc=='G':
        return G
    elif nuc=='T':
        return T
    else:
        return N
    
cdef int hashword(pobinuc word, int lkey, int lword):
    cdef int key=0
    cdef int k 
    cdef int dir=1 if GET_DIRECTION(word[0])==0 else -1
    
    if lword < lkey:
        lkey=lword
        
    if dir < 0:
        word+=lword-1
        
    for k in range(lkey):
        key<<=2
        key|=GET_FORWARD(word[0]) if dir > 0 else GET_REVERSE(word[0])
        word+=dir 
        
    return key 
        
    
    
cdef void encode_direction(pobinuc word, int lword):
    cdef int direction=0
    cdef pobinuc bnuc = word
    cdef pobinuc enuc = word + lword - 1
    
    while (bnuc < enuc and GET_FORWARD(bnuc[0])==GET_REVERSE(enuc[0])):
        bnuc+=1
        enuc-=1
        
    if GET_FORWARD(bnuc[0]) > GET_REVERSE(enuc[0]):
        word[0]=SET_DIRECTION(word[0])
    else:   
        word[0]=UNSET_DIRECTION(word[0])


cdef bytes decodeword(pobinuc w, int lword):      
    cdef char[1024] cword 
    cdef bytes bword
    cdef int d
    cdef int dir=1
    cdef int j

    d = GET_DIRECTION(w[0])
    
    if d==1:
        dir=-1
        w+= lword - 1
        
    for j in range(lword):
        cword[j]=DECODE_NUC_FR(w[0],d)
        w+=dir
        
    cword[lword]=0
    bword = PyBytes_FromStringAndSize(cword,lword)
    
    return bword

cpdef minword(bytes word):
    cdef obinuc[1024] nword 
    cdef char*        cword=word
    cdef int          lword=len(word)
    
    for i in range(lword):
        nword[i]=encodeobinuc(cword[i])
    
    encode_direction(nword,lword)
    
    return decodeword(nword,lword)
    

cdef object cmpwordlengthLock=Lock()
cdef int cmpwordlength=0

cdef int cmpwords(pconstvoid pw1, pconstvoid pw2):
    cdef pobinuc w1=(<pobinuc*>pw1)[0]   
    cdef pobinuc w2=(<pobinuc*>pw2)[0]
    cdef int dir1=1
    cdef int dir2=1
    cdef int d1=GET_DIRECTION(w1[0])
    cdef int d2=GET_DIRECTION(w2[0])
    cdef int i=0
    cdef int n1
    cdef int n2
    cdef int rep=0
    
    global cmpwordlength
    
#    print "-->",decodeword(w1,cmpwordlength),cmpwordlength,d1
#    print "-->",decodeword(w2,cmpwordlength),cmpwordlength,d2

    if d1==1:
        dir1=-1
        w1+=cmpwordlength-1
        
    if d2==1:
        dir2=-1
        w2+=cmpwordlength-1
        
    n1 = GET_FORWARD(w1[0]) if d1==0 else GET_REVERSE(w1[0])
    n2 = GET_FORWARD(w2[0]) if d2==0 else GET_REVERSE(w2[0])
    
#    print n1,n2
    
    while (n1==n2 and i < cmpwordlength):
#        print i,n1,n2
        i+=1
        w1+=dir1
        w2+=dir2
        n1 = GET_FORWARD(w1[0]) if d1==0 else GET_REVERSE(w1[0])
        n2 = GET_FORWARD(w2[0]) if d2==0 else GET_REVERSE(w2[0])
        
    if  cmpwordlength==i:
        rep=0
    elif n1 < n2:
        rep = -1
    elif n1 > n2:
        rep = 1
            
#    print rep
    
    return rep


cdef class ReadIndex:

    cdef int _size
    cdef int _readsize
    cdef int _chuncksize
    cdef int _seqsize
    cdef long long _buffer_size
    cdef pobinuc _buffer
    cdef long long _endofreads
    cdef list _ids
    cdef pobinuc* _wordlist
    cdef long long _wordlist_size
    cdef int _wordlength
    cdef int[4096] _index
    cdef int _lindex
    cdef int* _globalwordlength

    def __init__(self, int readsize=-1, int chuncksize=1000000):
        cdef int i 
        global cmpwordlength
        
        assert readsize < 1024,"You cannot use reads longer than 1023 base pair"
        self._readsize=readsize
        self._seqsize=(self._readsize+1)*2
        self._chuncksize=chuncksize
        self._buffer=NULL
        self._buffer_size=0
        self._endofreads=0
        self._size=0
        self._ids=[]
        self._wordlist=NULL
        self._wordlist_size=0
        self._wordlength=0
        self._lindex=0
        
        self._globalwordlength=&cmpwordlength
        
        for i in range(4096):
            self._index[i]=-1
        
    def __del__(self):
        if self._buffer != NULL:
            free(self._buffer)
        if self._wordlist != NULL:
            free(self._wordlist)

        
    def __len__(self):
        return self._size
    
    def save(self,bytes filename, bint verbose=False):
        cdef char* cfile=filename
        cdef FILE *f = fopen(cfile,'w')
        cdef long long i
        cdef bytes btitle
        cdef char* title
        cdef int ltitle
        cdef size_t transfered
        cdef size_t ltbuffer
        cdef bytes tbuffer
        cdef char* tcbuffer
        
        assert f!=NULL,"cannot open file Ms" % filename
        
        if verbose:
            print >>sys.stderr,"Writing header..."
            
        transfered = fwrite(&(self._size),sizeof(int),1,f)
        assert transfered==1,"Error during size writing"
        
        transfered = fwrite(&(self._readsize),sizeof(int),1,f)
        assert transfered==1,"Error during readsize writing"
        
        transfered = fwrite(&(self._seqsize),sizeof(int),1,f)
        assert transfered==1,"Error during seqsize writing"
        
        transfered = fwrite(&(self._buffer_size),sizeof(long long),1,f)
        assert transfered==1,"Error during buffer size writing"
        
        transfered = fwrite(&(self._buffer),sizeof(pobinuc),1,f)
        assert transfered==1,"Error during buffer address writing"
        
        print >> sys.stderr,self._endofreads
        transfered = fwrite(&(self._endofreads),sizeof(long long),1,f)
        assert transfered==1,"Error during endofread writing"
        
        transfered = fwrite(&(self._wordlist_size),sizeof(long long),1,f)
        assert transfered==1,"Error during wordlist size writing"
        
        transfered = fwrite(&(self._wordlength),sizeof(int),1,f)
        assert transfered==1,"Error during word length writing"
        
        transfered = fwrite(&(self._lindex),sizeof(int),1,f)
        assert transfered==1,"Error during lindex writing"
        
        if verbose:
            print >>sys.stderr,"Writing sequences..."

        fwrite(self._buffer,1,self._buffer_size,f)
        
        if verbose:
            print >>sys.stderr,"Writing %d words index..." % self._wordlist_size

#        for i in range(self._wordlist_size):    
#            print >>sys.stderr,'--> %d %d' % (i,<long long>self._wordlist[i]),
#            self._wordlist[i]-=<long long>self._buffer
#            print " %d" % <long long>self._wordlist[i]
            
        fwrite(self._wordlist,sizeof(pobinuc),self._wordlist_size,f)

#        for i in range(self._wordlist_size):    
#            print >>sys.stderr,'--> %d %d' % (i,<long long>self._wordlist[i]),
#            self._wordlist[i]+=<long long>self._buffer
#            print " %d" % <long long>self._wordlist[i]
       
        if verbose:
            print >>sys.stderr,"Writing sequence identifiers..."

        tbuffer=dumps(self._ids)
        tcbuffer=tbuffer
        ltbuffer=strlen(tcbuffer)
        if verbose:
            print >>sys.stderr,"  identifier size = %d" % ltbuffer
        fwrite(&ltbuffer,sizeof(size_t),1,f)
        fwrite(tcbuffer,1,ltbuffer,f)
        
#        for i in range(self._size):
#            ltitple=len(self._ids[i])
#            btitle= self._ids[i]
#            title = btitle
#            fwrite(&(ltitle),sizeof(int),1,f)
#            fwrite(title,1,ltitle,f)
            
        print >>sys.stderr

        if verbose:
            print >>sys.stderr,"Save done"

        fclose(f)
            
        if verbose:
            print >>sys.stderr,"File closed"
            
    def load(self,bytes filename, bint verbose=False):
        cdef char* cfile=filename
        cdef FILE *f = fopen(cfile,'r')
        cdef char[10000] ctitle
        cdef bytes btitle
        cdef int ltitle
        cdef pobinuc oldbuf
        cdef size_t transfered
        cdef size_t ltbuffer
        cdef bytes tbuffer
        cdef char* tcbuffer

#        print >>sys.stderr,sizeof(int),sizeof(pobinuc),sizeof(long long)

        assert f!=NULL,"cannot open file Ms" % filename

        if verbose:
            print >>sys.stderr,"Reading header..."
            
        transfered = fread(&(self._size),sizeof(int),1,f)
        assert transfered==1,"Error during size reading"
        if verbose:
            print >>sys.stderr,"  index contains %d sequence pairs" % self._size
        
        transfered = fread(&(self._readsize),sizeof(int),1,f)
        assert transfered==1,"Error during read size reading"
        if verbose:
            print >>sys.stderr,"  read size is %d pb" % self._readsize
        
        transfered = fread(&(self._seqsize),sizeof(int),1,f)
        assert transfered==1,"Error during seqsize reading"
        if verbose:
            print >>sys.stderr,"  sequence size is %d bytes" % self._seqsize
        
        transfered = fread(&(self._buffer_size),sizeof(long long),1,f)
        assert transfered==1,"Error during buffer size reading"
        if verbose:
            print >>sys.stderr,"  buffer size is %d bytes" % self._buffer_size
        
        transfered = fread(&(oldbuf),sizeof(pobinuc),1,f)
        assert transfered==1,"Error during buffer address reading"
        transfered = fread(&(self._endofreads),sizeof(long long),1,f)
        assert transfered==1,"Error during endofread reading"
        if verbose:
            print >>sys.stderr,"  end of reads is %d" % self._endofreads
            
        transfered = fread(&(self._wordlist_size),sizeof(long long),1,f)
        assert transfered==1,"Error during word list size reading"
        if verbose:
            print >>sys.stderr,"  index contains %d words" % self._wordlist_size
        
        transfered = fread(&(self._wordlength),sizeof(int),1,f)
        assert transfered==1,"Error during word length reading"
        
        transfered = fread(&(self._lindex),sizeof(int),1,f)
        assert transfered==1,"Error during lindex reading"
        
        if verbose:
            print >>sys.stderr,"Reading sequences..."
            
        if (self._buffer!=NULL):
            free(self._buffer)
            
        self._buffer=<pobinuc>malloc(self._buffer_size)
        
        transfered = fread(self._buffer,1,self._buffer_size,f)

        if verbose:
            print >>sys.stderr,"Reading %d words index..." % self._wordlist_size
            
        if (self._wordlist!=NULL):
            free(self._wordlist)
            
        self._wordlist = <pobinuc *>malloc(self._wordlist_size * sizeof(pobinuc))
            
        transfered = fread(self._wordlist,sizeof(pobinuc),self._wordlist_size,f)
 

        if verbose:
            print >>sys.stderr,"Patching word index..."
            

        for i in range(self._wordlist_size):    
            self._wordlist[i]+= (self._buffer - oldbuf)

        self._ids=[]
        
        if verbose:
            print >>sys.stderr,"Reading sequence ids..."
            
        fread(&ltbuffer,sizeof(size_t),1,f)
        if verbose:
            print >>sys.stderr,"  identifier size = %d" % ltbuffer
        tcbuffer = <char*>malloc(ltbuffer)
        fread(tcbuffer,1,ltbuffer,f)
        self._ids=loads(PyBytes_FromStringAndSize(tcbuffer,ltbuffer))
        free(tcbuffer)
        
        fclose(f)
            
        self._lindex=6 if self._wordlength >=6 else self._wordlength
        
        if verbose:
            print >>sys.stderr,"Hashing word prefix..."

        for i in range(4096):
            self._index[i]=-1
            
        for i in range(self._wordlist_size):
            k = hashword(self._wordlist[i],self._lindex,self._wordlength)
            if self._index[k]==-1:
                self._index[k]=i
                #print k,i
        
        fclose(f)
            
    
    def indexWords(self,int lword,bint verbose=False):
        cdef int error=0
        cdef pobinuc sword=self._buffer
        cdef pobinuc eword=sword
        cdef pobinuc endbuff = self._buffer + self._endofreads
        cdef int i=0
        cdef int k=0
        cdef int maxwords = (self._readsize - lword + 1) * self._size * 2
                
        assert sword != NULL,"Cannot index empty ReadIndex"
        assert lword <= self._readsize,"words cannot be longer than reads"
        
        if verbose:
            print >>sys.stderr,"Indexing words from %d sequences..." % len(self)
        
        if self._wordlist!=NULL:
            free(self._wordlist)
            
        self._wordlist = <pobinuc*>malloc(maxwords * sizeof(pobinuc*))
        
        for i in range(lword):
            error+=GET_ZERO(eword[0])
            eword+=1
        
        i=0
        
        
        while (eword < endbuff):
            if error==0:
                self._wordlist[i]=sword
                encode_direction(sword,lword)
                i+=1
              
            error-=GET_ZERO(sword[0])
            error+=GET_ZERO(eword[0])
            
            sword+=1
            eword+=1
 
                        
        self._wordlist = <pobinuc*>realloc(self._wordlist, i * sizeof(pobinuc*))
        self._wordlist_size=i
        self._wordlength=lword

        if verbose:
            print >>sys.stderr,"Sorting %d words..." % i
        
        cmpwordlengthLock.acquire()
        self._globalwordlength[0]=lword
        heapsort(self._wordlist,i,sizeof(pobinuc),cmpwords)
        cmpwordlengthLock.release()
        
        self._lindex=6 if lword >=6 else lword
        
        if verbose:
            print >>sys.stderr,"Hashing word prefix..."

        for i in range(4096):
            self._index[i]=-1
            
        for i in range(self._wordlist_size):
            k = hashword(self._wordlist[i],self._lindex,lword)
            if self._index[k]==-1:
                self._index[k]=i
                #print k,i
                
                
    def itermarkedpairs(self):
        cdef size_t i
        cdef pobinuc start1
        cdef pobinuc start2
        
        for i in range(self._size):
            start1=self._buffer+ i * self._seqsize
            start2=start1 + self._seqsize / 2
            if GET_SEQUSED(start1[0])==1 and GET_SEQUSED(start2[0])==1:
                yield self.getSeqPairAt(start1,False)
        
    def itermarkedsingleton(self):
        cdef size_t i
        cdef pobinuc start1
        cdef pobinuc start2
        
        for i in range(self._size):
            start1=self._buffer+ i * self._seqsize
            start2=start1 + self._seqsize / 2
            if (GET_SEQUSED(start1[0])==1 or GET_SEQUSED(start2[0])==1) \
               and not (GET_SEQUSED(start1[0])==1 and GET_SEQUSED(start2[0])==1):
                if GET_SEQUSED(start1[0])==1:
                    yield self.getSeqAt(start1,False)
                else:
                    yield self.getSeqAt(start2,False)
                
    def iterreads(self,bytes word):
        cdef obinuc nword[1024]
        cdef pobinuc pnword=nword
        cdef pobinuc* ppnword=&pnword
        cdef pobinuc* found
        cdef char* cword=word 
        cdef int i 
        cdef int lword=self._wordlength
        cdef int k
        cdef int nk=1 << (2*self._lindex)
        cdef long long wstart
        cdef long long wend
        cdef long long wpoint
        cdef int pcomp
        cdef int scomp
        cdef int ecomp
        
        assert len(word) == lword
                 
        for i in range(lword):
            nword[i]=encodeobinuc(cword[i])
        
        encode_direction(nword,lword)
        k=hashword(nword,self._lindex,lword)
        
        wstart=self._index[k]
        
        if wstart==-1:
            raise StopIteration
        
        k+=1
        
        while (k < nk and self._index[k]==-1):
            k+=1
                    
        if k==nk:
            wend=self._wordlist_size 
        else:
            wend=self._index[k] 
            
#        print "coucou : %d %d" % (wstart,wend)
    
            
#        print "locking 0"  
        cmpwordlengthLock.acquire()
#        print "locked 0"  
        self._globalwordlength[0]=lword
        
#        print decodeword(ppnword[0],lword)
#        print decodeword((self._wordlist+wstart)[0],lword)

        found = <pobinuc*>bsearch(ppnword,self._wordlist+wstart,wend-wstart,sizeof(pobinuc),cmpwords) 
        
        if found==NULL:
            cmpwordlengthLock.release()
            raise StopIteration
        
        wpoint = found - self._wordlist
            
        wstart = wpoint
        while (wpoint >0 and cmpwords(ppnword,self._wordlist+wpoint)==0):
            s=self.getSeqAt(self._wordlist[wpoint],True)
            if s is not None:
                cmpwordlengthLock.release()
                yield s
                cmpwordlengthLock.acquire()
                self._globalwordlength[0]=lword
            wpoint-=1

        wstart = wpoint+1
        while (wpoint < self._wordlist_size and cmpwords(ppnword,self._wordlist+wpoint)==0):
            s=self.getSeqAt(self._wordlist[wpoint],True)
            if s is not None:
                cmpwordlengthLock.release()
                yield s
                cmpwordlengthLock.acquire()
                self._globalwordlength[0]=lword
            wpoint+=1
          
        cmpwordlengthLock.release()
        
        
    
    def iterwords(self):
        cdef int i 
        
        assert self._wordlist != NULL,'You must index words'
        
        for i in range(self._wordlist_size):
            yield decodeword(self._wordlist[i],self._wordlength)
            
            
            
    
    def add(self,sequence):
        cdef bytes bseq
        cdef char* seq
        
        if  self._readsize<0:
            self._readsize=len(sequence[0])
            self._seqsize=(self._readsize+1)*2
            
            assert self._readsize < 1024,"You cannot use reads longer than 1023 base pair"

        else:
            assert len(sequence[0]) <= self._readsize and len(sequence[1]) <= self._readsize
       
        if self._buffer==NULL:
            self._buffer = <pobinuc>malloc(self._seqsize*self._chuncksize)
            self._buffer_size=self._seqsize*self._chuncksize
            self._endofreads=0
            
        if self._endofreads + self._seqsize >= self._buffer_size:
            self._buffer_size+=self._seqsize*self._chuncksize
            self._buffer = <pobinuc> realloc(<void*>self._buffer,self._buffer_size)
            
        self._ids.append(sequence[0].id[0:-2])
        
        bseq = bytes(sequence[0])
        seq = bseq
        l=0
        
        while seq[0]!=0:
            self._buffer[self._endofreads]=encodeobinuc(seq[0])
            self._endofreads+=1
            seq+=1
            l+=1
        
        while l<=self._readsize:
            self._buffer[self._endofreads]=SET_ENDOFREAD(N)
            self._endofreads+=1
            l+=1
        

        bseq = bytes(sequence[1])
        seq = bseq
        l=0
        
        while seq[0]!=0:
            self._buffer[self._endofreads]=encodeobinuc(seq[0])
            self._endofreads+=1
            seq+=1
            l+=1
        
        while l<=self._readsize:
            self._buffer[self._endofreads]=SET_ENDOFREAD(N)
            self._endofreads+=1
            l+=1

        self._size+=1

    cdef object getSeqAt(self,pobinuc word,bint lock=False):
        cdef long long delta
        cdef pobinuc start1
        cdef pobinuc start2
        cdef char[1024] cseqf
        cdef char[1024] cseqr
        cdef char* pseq
        cdef bytes bseqf
        cdef bytes bseqr
        cdef bytes n=b"/1"
        
        delta = <void*>word - <void*>self._buffer
        delta/= self._seqsize
        
        start1=self._buffer+ delta * self._seqsize
        start2=start1 + self._seqsize / 2
        
        if word >= start2:
            start1=start2
            n=b"/2"
        
        if lock:
            if GET_SEQUSED(start1[0])==1:
                return None
            else:
                start1[0]=SET_SEQUSED(start1[0])
                     
        pseq = cseqf
        
        while (GET_ENDOFREAD(start1[0])==0):
            pseq[0]=DECODE_NUC(start1[0])
            start1+=1
            pseq+=1
            
        pseq[0]=0
            
        bseqf = PyBytes_FromString(cseqf)
        
        return NucSequence(self._ids[delta]+n,bseqf)
    
    cdef object getSeqPairAt(self,pobinuc word,bint lock=False):
        cdef long long delta
        cdef pobinuc start1
        cdef pobinuc start2
        cdef char[1024] cseqf
        cdef char[1024] cseqr
        cdef char* pseq
        cdef bytes bseqf
        cdef bytes bseqr
        
        delta = <void*>word - <void*>self._buffer
        delta/= self._seqsize
        
        start1=self._buffer+ delta * self._seqsize
        start2=start1 + self._seqsize / 2
        
        if lock:
            if GET_SEQUSED(start1[0])==1:
                return None,None
            else:
                start1[0]=SET_SEQUSED(start1[0])
                start2[0]=SET_SEQUSED(start2[0])
                     
        pseq = cseqf
        
        while (GET_ENDOFREAD(start1[0])==0):
            pseq[0]=DECODE_NUC(start1[0])
            start1+=1
            pseq+=1
            
        pseq[0]=0
            
        bseqf = PyBytes_FromString(cseqf)
        
        pseq = cseqr
        
        while (GET_ENDOFREAD(start2[0])==0):
            pseq[0]=DECODE_NUC(start2[0])
            start2+=1
            pseq+=1
            
        pseq[0]=0
            
        bseqr = PyBytes_FromString(cseqf)
        
        return NucSequence(self._ids[delta]+'/1',bseqf),NucSequence(self._ids[delta]+'/2',bseqr)
        
    def __getitem__(self,int index):
        
        if index >= self._size:
            raise IndexError(index)
        
        if index < 0:
            index+=self._size
            
        if index < 0:
            raise IndexError(index)

        return self.getSeqAt(self._buffer + index * self._seqsize)
    
    
            
        
