#!/usr/local/bin/python


from obitools.options import getOptionManager
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
import math
from obitools.fasta import formatFasta
from obitools.fastq import formatFastq


def addDistributeOptions(optionManager):
    
    optionManager.add_option('-p','--prefix',
                             action="store", dest="prefix",
                             metavar="<PREFIX FILENAME>",
                             type="string",
                             default="",
                             help="prefix added at each file name")

    optionManager.add_option('-n','--number',
                             action="store", dest="number",
                             metavar="###",
                             type="int",
                             default=None,
                             help="Number of parts")
    
    
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
        self._digit = math.ceil(math.log10(options.number))
                
        
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
                template = "%s_%%0%dd.%s" % (self._prefix,self._digit,self._extension)
            else:
                template = "%%0%dd.%s" % (self._digit,self._extension)
                
            current = open(template % name,'a')
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
    
    optionParser = getOptionManager([addDistributeOptions,addInOutputOption])
    
    (options, entries) = optionParser()
    
    assert options.number is not None, "You must specify the number of parts"
    
    digit = math.ceil(math.log10(options.number))
    out=[]

    
    i = 0
    for seq in entries:
        if not out:
            template = "%s_%%0%dd.%s" % (options.prefix,digit,options.outputFormat)
            out=[sequenceWriterGenerator(options,
                                         open(template % (i+1),"w"))
                 for i in xrange(options.number)
                ]
            
        out[i](seq)
        i+=1
        i%=options.number
        
    del out
    
            
    
