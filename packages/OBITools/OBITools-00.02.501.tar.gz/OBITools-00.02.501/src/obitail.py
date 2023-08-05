#!/usr/local/bin/python
'''
:py:mod:`obitail` : Extract the last sequences
==============================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obitail` command is in some way analog to the standard Unix `tail` command.
It selects the tail of :ref:`a sequence file<the-sequence-files>`. 
But instead of working text line by text line as the standard tool, 
selection is done at sequence level. You can specify number of sequences to be printed.

.. code-block:: bash

   > obitail -n 150 seq1.fasta > seq2.fasta


'''

from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager
import collections

def addHeadOptions(optionManager):
    optionManager.add_option('-n','--sequence-count',
                             action="store", dest="count",
                             metavar="###",
                             type="int",
                             default=10,
                             help="Count of first sequences to print")
    

if __name__ == '__main__':
    optionParser = getOptionManager([addHeadOptions,addInOutputOption])
    
    (options, entries) = optionParser()
    i=0
    
    queue = collections.deque(entries,options.count)

    writer = sequenceWriterGenerator(options)
   
    while queue:
        writer(queue.popleft())
        
        
        

