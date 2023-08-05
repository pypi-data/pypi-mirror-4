from obitools import location

class SequenceEncoder(object):
    pass
    
class DNAComplementEncoder(SequenceEncoder):
    _comp={'a': 't', 'c': 'g', 'g': 'c', 't': 'a',
           'r': 'y', 'y': 'r', 'k': 'm', 'm': 'k', 
           's': 's', 'w': 'w', 'b': 'v', 'd': 'h', 
           'h': 'd', 'v': 'b', 'n': 'n', 'u': 'a',
           '-': '-'}

    _info={'complemented':True}

    @staticmethod
    def _encode(seq,position=slice(None, None, -1)):
        cseq = [DNAComplementEncoder._comp.get(x.lower(),'n') for x in seq[position]]
        return ''.join(cseq)
    
    @staticmethod
    def _check(seq):
        assert seq.isNucleotide()

    @staticmethod
    def _convertpos(position):
        if isinstance(position, int):
            return -(position+1)
        elif isinstance(position, slice):
            return slice(-(position.stop+1),
                         -(position.start+1),
                         -position.step)
        elif isinstance(position, location.Location):
            return location.ComplementLocation(position).simplify()
        
        raise TypeError,"position must be an int, slice or Location instance"

    @staticmethod
    def complement(seq):
        return seq
    
class SeqFragmentEncoder(SequenceEncoder):
    def __init__(self,begin,end):
        assert begin < end and begin >=0
        self._limits = slice(begin,end)
        self._info = {'cut' : [begin,end,1]}
        self._len = end - begin + 1
        
    def _check(self,seq):
        lseq = len(seq)
        assert self._limits.stop <= lseq
        
    def _encode(self,seq,position=None):
        return str(seq)[self._limits]
    
    def _convertpos(self,position):
        if isinstance(position, int):
            if position < -self._len or position >= self._len:
                raise IndexError,position
            if position >=0:
                return self._limits.start + position
            else:
                return self._limits.stop + position + 1
        elif isinstance(position, slice):
            return slice(-(position.stop+1),
                         -(position.start+1),
                         -position.step)
        elif isinstance(position, location.Location):
            return location.ComplementLocation(position).simplify()
        
        raise TypeError,"position must be an int, slice or Location instance"
        
    
        