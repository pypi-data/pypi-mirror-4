from obitools import bioSeqGenerator as __bioSeqGenerator
from obitools import BioSequence
from obitools.fasta import formatFasta

__anonymous_seq__=0

class InteractiveBioseqProxy:
    def __init__(self,bio):
        assert(isinstance(bio, BioSequence))
        self._reference=bio
        
    def __repr__(self):
        return formatFasta(self._reference)
    
        
    
    def __getattr__(self,key):
        return getattr(self._reference,key)

def bioseq(seq,id=None,definition=None):
    global __anonymous_seq__
    
    if id is None:
        __anonymous_seq__+=1
        id='seq%05d' % __anonymous_seq__
        
    if definition is None:
        definition=""
        
    return InteractiveBioseqProxy(__bioSeqGenerator(id,seq,definition))
