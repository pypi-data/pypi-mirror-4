from itertools import imap
from obitools import utils

class GoAFileIterator(utils.ColumnFile):
    def __init__(self,stream):
        utils.ColumnFile.__init__(self,
                                  stream, '\t', True, 
                                  (str,))

    _colname = ['database',
                'ac',
                'symbol',
                'qualifier',
                'goid',
                'origin',
                'evidence',
                'evidnce_origine',
                'namespace',
                'db_object_name',
                'gene',
                'object_type',
                'taxid',
                'date',
                'assigned_by']

    def next(self):
        data = utils.ColumnFile.next(self)
        data = dict(imap(None,GoAFileIterator._colname,data))
                 
        return data
    
        
        
