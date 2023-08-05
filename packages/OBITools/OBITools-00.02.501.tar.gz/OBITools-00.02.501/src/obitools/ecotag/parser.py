from itertools import imap
from obitools import utils

from obitools.ecotag import EcoTagResult

class EcoTagFileIterator(utils.ColumnFile):
    
    @staticmethod
    def taxid(x):
        x = int(x)
        if x < 0:
            return None
        else:
            return x
        
    @staticmethod
    def scientificName(x):
        if x=='--':
            return None
        else:
            return x
        
    @staticmethod
    def value(x):
        if x=='--':
            return None
        else:
            return float(x)
        
    @staticmethod
    def count(x):
        if x=='--':
            return None
        else:
            return int(x)
        
    
    def __init__(self,stream):
        utils.ColumnFile.__init__(self,
                                  stream, '\t', True, 
                                  (str,str,str,
                                   EcoTagFileIterator.value,
                                   EcoTagFileIterator.value,
                                   EcoTagFileIterator.value,
                                   EcoTagFileIterator.count,
                                   EcoTagFileIterator.count,
                                   EcoTagFileIterator.taxid,
                                   EcoTagFileIterator.scientificName,
                                   str,
                                   EcoTagFileIterator.taxid,
                                   EcoTagFileIterator.scientificName,
                                   EcoTagFileIterator.taxid,
                                   EcoTagFileIterator.scientificName,
                                   EcoTagFileIterator.taxid,
                                   EcoTagFileIterator.scientificName,
                                   str
                                   ))
        self._memory=None

    _colname = ['identification',
                'seqid',
                'best_match_ac',
                'max_identity',
                'min_identity',
                'theorical_min_identity',
                'count',
                'match_count',
                'taxid',
                'scientific_name',
                'rank',
                'order_taxid',
                'order_sn',
                'family_taxid',
                'family_sn',
                'genus_taxid',
                'genus_sn',
                'species_taxid',
                'species_sn',
                'sequence']

    def next(self):
        if self._memory is not None:
            data=self._memory
            self._memory=None
        else:
            data = utils.ColumnFile.next(self)
            data = EcoTagResult(imap(None,EcoTagFileIterator._colname[:len(data)],data))
               
        if data['identification']=='ID':
            data.cd=[]
            try:
                nextone = utils.ColumnFile.next(self)
                nextone = EcoTagResult(imap(None,EcoTagFileIterator._colname[:len(nextone)],nextone))
            except StopIteration:
                nextone = None
            while nextone is not None and nextone['identification']=='CD':
                data.cd.append(nextone)
                try:
                    nextone = utils.ColumnFile.next(self)
                    nextone = EcoTagResult(imap(None,EcoTagFileIterator._colname[:len(nextone)],nextone))
                except StopIteration:
                    nextone = None
            self._memory=nextone
                
        return data
    
def ecoTagIdentifiedFilter(ecoTagIterator):
    for x in ecoTagIterator:
        if x['identification']=='ID':
            yield x
            
            
class EcoTagAbstractIterator(utils.ColumnFile):

    _colname = ['scientific_name',
                'taxid',
                'rank',
                'count',
                'max_identity',
                'min_identity']


    @staticmethod
    def taxid(x):
        x = int(x)
        if x < 0:
            return None
        else:
            return x

    def __init__(self,stream):
        utils.ColumnFile.__init__(self,
                                  stream, '\t', True, 
                                  (str,
                                   EcoTagFileIterator.taxid,
                                   str,
                                   int,
                                   float,float,float))
       
    def next(self):
        data = utils.ColumnFile.next(self)
        data = dict(imap(None,EcoTagAbstractIterator._colname,data))

        return data
   
def ecoTagAbstractFilter(ecoTagAbsIterator):
    for x in ecoTagAbsIterator:
        if x['taxid'] is not None:
            yield x
 