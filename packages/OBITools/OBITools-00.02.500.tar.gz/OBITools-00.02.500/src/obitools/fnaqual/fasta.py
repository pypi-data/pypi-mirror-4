from obitools.fasta import fastaNucIterator
from obitools.fnaqual import fnaTag

def fnaFastaIterator(file):
    
    x = fastaNucIterator(file, fnaTag)
    
    return x