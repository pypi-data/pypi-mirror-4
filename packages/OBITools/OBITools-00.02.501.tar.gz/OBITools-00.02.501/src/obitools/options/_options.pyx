# cython: profile=True

from obitools.utils._utils cimport progressBar

from obitools.utils import universalOpen
from obitools.utils import universalTell
from obitools.utils import fileSize

from logging import debug
import sys

cdef extern from "stdio.h":
    ctypedef unsigned int off_t "unsigned long long"
    
    
cdef class CurrentFileStatus:
    cdef public bytes currentInputFileName
    cdef public object currentFile
    cdef public off_t currentFileSize

    def __init__(self):
        self.currentInputFileName=None
        self.currentFile = None
        self.currentFileSize = -1

cfs=CurrentFileStatus()

cpdef bytes currentInputFileName():
    return cfs.currentInputFileName

cpdef object  currentInputFile():
    return cfs.currentFile

cpdef off_t currentFileSize():
    return cfs.currentFileSize

cpdef off_t currentFileTell():
    return universalTell(cfs.currentFile)

def fileWithProgressBar(file, int step=100):
   
    cdef off_t size
    cdef off_t pos
    
    size = cfs.currentFileSize
                
    def fileBar():
        
        cdef str l
        
        pos=1
        progressBar(pos, size, True,cfs.currentInputFileName)
        for l in file:
            progressBar(currentFileTell,size, False,
                        cfs.currentInputFileName)
            yield l 
        print >>sys.stderr,''   
         
    if size < 0:
        return file
    else:
        f = fileBar()
        return f


def allEntryIterator(files,entryIterator,with_progress=False,histo_step=102):

    if files :
        for f in files:
            cfs.currentInputFileName=f
            f = universalOpen(f)
            cfs.currentFile=f
            cfs.currentFileSize=fileSize(cfs.currentFile)
            debug(f)
            
            if with_progress:
                f=fileWithProgressBar(f,step=histo_step)
                
            if entryIterator is None:
                for line in f:
                    yield line
            else:
                for entry in entryIterator(f):
                    yield entry
    else:
        if entryIterator is None:
            for line in sys.stdin:
                yield line
        else:
            for entry in entryIterator(sys.stdin):
                yield entry
            
