#!/usr/local/bin/python


from obitools.format.sequence.fasta import formatFasta
from obitools.format.sequence.genbank import genbankIterator
from obitools import AASequence


from obitools.options import getOptionManager
import sys
import logging



def addExctractCDSOptions(optionManager):
        
    optionManager.add_option('-p','--protein',
                             action="store_true", dest="protein",
                             default=False,
                             help="Output file are protein (default=Nuc)")

if __name__=='__main__':

    optionParser = getOptionManager([addExctractCDSOptions],
                                    entryIterator=genbankIterator
                                    )
    
    (options, entries) = optionParser()

    if options.debug:
        logging.root.setLevel(logging.DEBUG)
    
    
    for entry in entries:
        entry.extractTaxon()
        taxid = entry['taxid']
        ac    = entry.id
        de    = entry.definition
        organism = entry['organism']
        logging.debug("==>Parsing entry : %s\t%s" %(ac,de))
        unkown=1
        
        for cds in (x for x in entry.getFeatureTable(True) if x.ftType=='CDS'):
            if 'protein_id' in cds:
                pid = cds['protein_id'][0]
            else:
                pid = "%s_ucds%03d" % (ac,unkown)
                unkown+=1
            fl  = cds.isFullLength()
            if 'transl_table' in cds:
                tt = cds['transl_table'][0]
            else:
                tt=1
            if options.protein:
                if 'translation' in cds:
                    seq = AASequence(pid,cds['translation'][0],de,ac=ac,
                                                                  location=cds.locStr(),
                                                                  transl_table=tt,
                                                                  taxid=taxid,
                                                                  full_length=fl,
                                                                  organism=organism)
                else:
                    logging.warning('From entry %s :  CDS %s has no translation qualifier' % (ac,pid))
            else:
                seq = entry[cds]
                seq.id=pid
                seq.definition=de
                seq['ac']=ac
                seq['location']=cds.locStr()
                seq['transl_table']=tt
                seq['taxid']=taxid
                seq['full_length']=fl
                
            print formatFasta(seq,True)
            
