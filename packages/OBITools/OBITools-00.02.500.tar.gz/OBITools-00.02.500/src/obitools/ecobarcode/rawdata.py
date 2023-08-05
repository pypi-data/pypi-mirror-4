'''
Created on 25 sept. 2010

@author: coissac
'''

from obitools import NucSequence
from obitools.utils import progressBar
from obitools.ecobarcode.ecotag import alreadyIdentified

import sys

def sequenceIterator(options):
    cursor = options.ecobarcodedb.cursor()
    
    cursor.execute('''
                      select s.id,sum(o.count),s.sequence
                      from rawdata.sequence      s,
                           rawdata.occurrences   o
                      where o.sequence= s.id
                        and s.primers = '%s'
                      group by s.id,s.sequence
                   ''' % options.primer
                  )
    
    nbseq = cursor.rowcount
    progressBar(1, nbseq, True, head=options.dbname)
    for id,count,sequence in cursor:
        progressBar(cursor.rownumber+1, nbseq, head=options.dbname)
        if not options.updatedb or not alreadyIdentified(id,options):
            s = NucSequence(id,sequence)
            s['count']=count
            print >>sys.stderr,' +', cursor.rownumber+1,
            yield s
        else:
            print >>sys.stderr,' @', cursor.rownumber+1,
        
    print >>sys.stderr
