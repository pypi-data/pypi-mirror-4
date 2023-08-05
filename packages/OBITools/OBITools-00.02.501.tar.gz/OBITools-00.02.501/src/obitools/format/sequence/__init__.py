from obitools.fasta import fastFastaIterator
from obitools.fastq import fastqSangerIterator
from obitools.seqdb.embl.parser import emblIterator
from obitools.seqdb.genbank.parser import genbankIterator
from itertools import chain
from obitools.utils import universalOpen
import sys

def skipOnErrorIterator(seqIterator):
    def internal(inputdata):
        si = seqIterator(inputdata)
        while(1):
            try:
                seq = si.next()
                yield seq
            except Exception,e:
                print >>sys.stderr,"coucou"
                if isinstance(e,StopIteration):
                    raise e
                else:
                    continue
                
    return internal
        

def autoSequenceIterator(file):
    lineiterator = universalOpen(file)
    first = lineiterator.next()
    if first[0]==">":
            reader=fastFastaIterator
    elif first[0]=='@':
        reader=fastqSangerIterator
    elif first[0:3]=='ID ':
        reader=emblIterator
    elif first[0:6]=='LOCUS ':
        reader=genbankIterator
    else:
        raise AssertionError,'file is not in fasta, fasta, embl, or genbank format'
    
    input = reader(chain([first],lineiterator))
    
    return input
