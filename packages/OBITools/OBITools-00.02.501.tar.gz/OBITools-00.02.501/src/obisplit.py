#!/usr/local/bin/python


from obitools.options import getOptionManager
from obitools.format.options import addInOutputOption
from obitools.fasta import formatFasta
from obitools.fastq import formatFastq


def addSplitOptions(optionManager):
    
    optionManager.add_option('-p','--prefix',
                             action="store", dest="prefix",
                             metavar="<PREFIX FILENAME>",
                             type="string",
                             default=None,
                             help="prefix added at each file name")


    optionManager.add_option('-t','--tag-name',
                             action="append", dest="tagname",
                             metavar="<tagname>",
                             type="string",
                             default=[],
                             help="tag used to categorize sequences")
      
    optionManager.add_option('-u','--undefined',
                             action="store", dest="undefined",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file used to store unidentified sequences")
    
    
class OutFiles:
    def __init__(self,options):
        self._tags = options.tagname
        self._undefined = None
        if options.undefined is not None:
            self._undefined=open(options.undefined,'w')
        self._prefix=options.prefix
        self._files = {}
        self._first=None
        self._last=None
        self._extension=options.outputFormat
                
        
    def __getitem__(self,key):
        if key in self._files:
            data = self._files[key]
            prev,current,next = data
            if next is not None:
                if prev is not None:
                    self._files[prev][2]=next
                self._files[next][0]=prev
                data[0]=self._last
                data[2]=None
                self._last=key
        else:
            name = key
            if self._prefix is not None:
                name = '%s%s' % (options.prefix,name)
            current = open('%s.%s' % (name,self._extension),'a')
            prev=self._last 
            self._last=key
            next=None
            self._files[key]=[prev,current,next]
            if len(self._files)>100:
                oprev,old,onext=self._files[self._first]
                del(self._files[self._first])
                old.close()
                self._first=onext
            if self._first is None:
                self._first=key
        return current
    
    def __call__(self,seq):
        ok = reduce(lambda x,y: x and y, (z in seq for z in self._tags),True)
        if ok:
            k = "_".join([str(seq[x]) for x in self._tags])
            file=self[k]
        else:
            file=self._undefined
        if file is not None and self._extension=="fasta":
            print >>file,formatFasta(seq)
        else:
            print >>file,formatFastq(seq)
    
    def __del__(self):
        k=self._files.keys()
        for x in k:
            del(self._files[x])
            

if __name__=='__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([addSplitOptions,addInOutputOption])
    
    (options, entries) = optionParser()
            
    out=None
    
    for seq in entries:
        if out is None:
            out = OutFiles(options)
        out(seq)    
            
    
    
    
