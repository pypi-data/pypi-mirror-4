'''
Created on 25 sept. 2010

@author: coissac
'''

def alreadyIdentified(seqid,options):
    cursor = options.ecobarcodedb.cursor()    
    cursor.execute('''
                     select count(*) 
                     from ecotag.identification 
                     where sequence=%s
                     and database=%s
                   ''',(int(seqid),int(options.dbid)))
    
    return int(cursor.fetchone()[0]) > 0;

def storeIdentification(seqid,
                        idstatus,taxid,
                        matches,
                        options
                        ):
    
    cursor = options.ecobarcodedb.cursor()    
    
    if not options.updatedb:
        cursor.execute('''
                       delete from ecotag.identification where sequence=%s and database=%s
                       ''',(int(seqid),int(options.dbid)))
    
    cursor.execute('''
                    insert into ecotag.identification (sequence,database,idstatus,taxid)
                    values (%s,%s,%s,%s)
                    returning id
                   ''' , (int(seqid),int(options.dbid),idstatus,int(taxid)))
    
    idid = cursor.fetchone()[0]
    
    for seq,identity in matches.iteritems():
        cursor.execute('''
                        insert into ecotag.evidence (identification,reference,identity)
                        values (%s,
                                %s,
                                %s)
                       ''',(idid,seq,identity))
        

    cursor.close()
    
    options.ecobarcodedb.commit()   
