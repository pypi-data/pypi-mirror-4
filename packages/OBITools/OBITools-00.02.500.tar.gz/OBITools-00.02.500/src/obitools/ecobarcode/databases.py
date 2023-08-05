'''
Created on 25 sept. 2010

@author: coissac
'''
from obitools import NucSequence

def referenceDBIterator(options):
    
    cursor = options.ecobarcodedb.cursor()

    cursor.execute("select id from databases.database where name='%s'" % options.database)
    options.dbid = cursor.fetchone()[0]
   
    cursor.execute('''
                      select s.accession,r.id,r.taxid,r.sequence
                      from databases.database    d,
                           databases.reference   r,
                           databases.relatedsequences s
                      where r.database = d.id
                        and s.reference= r.id
                        and s.mainac
                        and d.name = '%s'
                   ''' % options.database
                  )
    
    for ac,id,taxid,sequence in cursor:
        s = NucSequence(ac,sequence)
        s['taxid']=taxid
        s['refdbid']=id
        yield s
        