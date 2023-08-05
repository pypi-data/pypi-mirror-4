# cython: profile=True

from _utils cimport *

import sys

cdef class FakeFile:

    def __init__(self,li):
        self._li = li
        self.__buffer = []
        self.__bufsize=0
        
    cpdef str read(self,int size=-1):
        
        cdef int csize=self.__bufsize
        cdef str line
        cdef str buffer
         
        try:
            while(csize < size or size < 0):
                    line = self._li.next()
                    csize+=len(line)
                    self.__buffer.append(line)
        except StopIteration:
            if csize==0:
                raise EOFError
        
        buffer = ''.join(self.__buffer)
        
        if size >= 0:
            self.__buffer=[buffer[size:]]
            self.__bufsize=len(self.__buffer[0])
            buffer=buffer[0:size]
        else:
            self.__buffer=[]
            self.__bufsize=0
            
        return buffer
        
    cpdef str readline(self):
     
            cdef str line
            
            try:
                if self.__buffer:
                    line = self.__buffer[0]
                    self.__buffer=[]
                    self.__bufsize=0
                else:
                    line=self._li.next()
            except StopIteration:
                raise EOFError
            
            return line
        
cpdef object progressBar(object pos,
                  off_t maxi,
                  bint reset=False,
                  bytes head=b'',
                  list delta=[],
                  list step=[1,0,0]):
                  
    cdef off_t    ipos
    cdef double percent 
    cdef int days,hour,minu,sec
    cdef bytes bar
    cdef off_t fraction
    cdef int freq,cycle,arrow
    cdef tm remain

    cdef clock_t d
    cdef clock_t elapsed
    cdef clock_t newtime 
    cdef clock_t more
    
    #                   0123456789
    cdef char* wheel=  '|/-\\'
    cdef char*  spaces='          ' \
                       '          ' \
                       '          ' \
                       '          ' \
                       '          '
                
    cdef char*  diese ='##########' \
                       '##########' \
                       '##########' \
                       '##########' \
                       '##########' 
                  
    if reset:
        del delta[:]
    if not delta:
        delta.append(clock())
        delta.append(clock())
        
    assert maxi>0
    
    freq,cycle,arrow = step

    cycle+=1
    
    if cycle % freq == 0:
        cycle=1
        newtime = clock()
        d = newtime-delta[1]
        
        if d < 0.2 * CLOCKS_PER_SEC :
            freq*=2
        elif d > 0.4 * CLOCKS_PER_SEC and freq>1:
            freq/=2
            
        delta[1]=newtime
        elapsed = newtime-delta[0]
        
        if callable(pos):
            ipos=pos()
        else:
            ipos=pos
            
        percent = <double>ipos/<double>maxi
        more = <time_t>((<double>elapsed / percent * (1. - percent))/CLOCKS_PER_SEC)
        <void>gmtime_r(&more, &remain)
        days = remain.tm_yday 
        hour = remain.tm_hour
        minu  = remain.tm_min
        sec  = remain.tm_sec

        fraction=<int>(percent * 50.)
        arrow=(arrow+1) % 4
        diese[fraction]=0
        spaces[50 - fraction]=0
        
        if days:
            <void>fprintf(stderr,b'\r%s %5.1f %% |%s%c%s] remain : %d days %02d:%02d:%02d',
                            <char*>head,
                            percent*100,
                            diese,wheel[arrow],spaces,
                            days,hour,minu,sec)
        else:
            <void>fprintf(stderr,b'\r%s %5.1f %% |%s%c%s] remain : %02d:%02d:%02d',
                            <char*>head,
                            percent*100.,
                            diese,wheel[arrow],spaces,
                            hour,minu,sec)
            
        diese[fraction]='#'
        spaces[50 - fraction]=' '

    else:
        cycle+=1

    step[0:3] = freq,cycle,arrow
    