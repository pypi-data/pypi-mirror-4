#!/usr/local/bin/python

from obitools.ecopcr import EcoPCRFile
from obitools.fasta import formatFasta

from obitools import NucSequence

from obitools.options import getOptionManager



def addOligoOptions(optionManager):
        
    optionManager.add_option('-p','--with-primer',
                             action="store_true", dest="primer",
                             metavar="<FILENAME>",
                             default=False,
                             help="concate primer sequence to amplifia")

if __name__=='__main__':

    optionParser = getOptionManager([addOligoOptions],
                                    entryIterator=EcoPCRFile
                                    )
    
    (options, entries) = optionParser()

old_id = ''
seq_in_id=0
for seq in entries:
    if seq.id != old_id:
        seq_in_id=0
        old_id = seq.id
    seq_in_id+=1
    seq.id="%s_%d" % (seq.id,seq_in_id)
    
    if options.primer:
        rp = str(NucSequence('rp',str(seq['reverse_primer'])).complement())
        s=''.join([seq['forward_primer'],str(seq),rp])
        seq = NucSequence(seq.id,s,seq.definition,**seq.getTags())
    print formatFasta(seq)
    
    