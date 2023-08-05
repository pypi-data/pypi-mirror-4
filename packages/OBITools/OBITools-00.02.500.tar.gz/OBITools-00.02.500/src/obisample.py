#!/usr/local/bin/python
'''
:py:mod:`obisample` : Extract a random subset of sequences from a sequence file
===============================================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>


:py:mod:`obisample` randomly sample sequences.

'-s' option allows to specify the final 'count' of sequences (by default the number of sequences provided). When option '-a' is set
the argument of the '-s' option is considered a fraction of the total number of sequences provided.

.. code-block:: bash

   > obisample -s 100 seq1.fasta > seq2.fasta



'''

from obitools.options import getOptionManager
from obitools.sample import weigthedSample, weigthedSampleWithoutReplacement
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
import random

def addSampleOptions(optionManager):
    optionManager.add_option('-s','--sample-size',
                             action="store", dest="size",
                             metavar="###",
                             type="float",
                             default=None,
                             help="Size of the generated sample. "
                                  "If -a option is set, size is expressed as fraction"
                             )
    optionManager.add_option('-a','--approx-sampling',
                             action="store_true", dest="approx",
                             default=False,
                             help="Switch to an approximative algorithm, "
                                  "useful for large files"
                             )

    optionManager.add_option('-w','--without-replacement',
                             action="store_true", dest="woreplace",
                             default=False,
                             help="Ask for sampling without replacement"
                            )
 
def rbinom(n,p):
    return sum((random.random() < p) for x in xrange(n))

if __name__ == '__main__':

    optionParser = getOptionManager([addSampleOptions,addInOutputOption]
                                    )
    
    (options, entries) = optionParser()
    
    if not options.approx:
    
        db = [s for s in entries]
        
        if options.size is None:
            options.size=len(db)
        else:
            options.size=int(options.size)
            
        distribution = {}
        idx=0
        total = 0
        for s in db:
            count = s['count']
            total+=count
            distribution[idx]=count
            idx+=1

        if options.woreplace:
            assert options.size <= total
            sp = weigthedSampleWithoutReplacement
        else:
            sp= weigthedSample
                        
        sample =sp(distribution, options.size)

        
    else:
        db = []
        distribution = {}
        idx = 0
        total = 0

        assert options.size is not None, \
            "You cannot specify option -a without option -s"
            
        assert options.size>=0 and options.size <=1, \
            "When used with -a options -s must be a probability"
          
        p = options.size * 1.5
        
        if p > 1.:
            p = 1.
            
        for seq in entries:
            count = seq['count']
            total+=count
            
            n = rbinom(count, p)
                        
            if n > 0:
                db.append(seq)
                distribution[idx]=n
                
                idx+=1
                
        size = int(total * options.size)  
        sample=weigthedSampleWithoutReplacement(distribution, size)
                    
    writer = sequenceWriterGenerator(options)
    
    for idx in sample:
        seq = db[idx]
        seq['count']=sample[idx]
        writer(seq)

        
        

