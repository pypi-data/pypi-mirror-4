from obitools import bioSeqGenerator
from obitools.utils import universalOpen


class SequenceFileIterator:
    
    def __init__(self,inputfile,bioseqfactory=bioSeqGenerator):
        self._inputfile = universalOpen(inputfile)
        self._bioseqfactory = bioseqfactory

    def get_inputfile(self):
        return self.__file


    def get_bioseqfactory(self):
        return self.__bioseqfactory
    
    def next(self):
        entry = self.inputfile.next()
        return self._parse(entry)
    
    def __iter__(self):
        return self

    _inputfile = property(get_inputfile, None, None, "_file's docstring")
    _bioseqfactory = property(get_bioseqfactory, None, None, "_bioseqfactory's docstring")
        
    