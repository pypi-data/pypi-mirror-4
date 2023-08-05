#!/usr/local/bin/python

from obitools.fasta import formatFasta
from obitools.alignment.ace import contigIterator


from obitools.options import getOptionManager


def addAceOptions(optionManager):
    
    optionManager.add_option('-p','--prefix',
                             action="store", dest="prefix",
                             metavar="<FILE_PREFIX>",
                             type="string",
                             help="prefix used for fasta file name")
    
    
if __name__=='__main__':
    
    optionParser = getOptionManager([addAceOptions],
                                    entryIterator=contigIterator
                                    )
    
    (options, entries) = optionParser()
    
    
    for name,contig in entries:
        if options.prefix is None:
            filename='%s.fasta' % name
        else:
            filename='%s_%s.fasta' % (options.prefix,name)
        
        out = open(filename,'w')
        print >>out,formatFasta(contig),
        
    
