#!/usr/local/bin/python
'''
:py:mod:`obihead` : Extract the first sequences
===============================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obihead` command is in some way analog to the standard Unix `head` command.
It selects the head of  :ref:`a sequence file<the-sequence-files>`. 
But instead of working text line by text line as the standard tool, 
selection is done at sequence level. You can specify number of sequences to be printed.

.. code-block:: bash

   > obihead -n 150 seq1.fasta > seq2.fasta


'''
import sys
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager


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

    writer = sequenceWriterGenerator(options)
    
    for s in entries:
        if i < options.count:
            writer(s)
            i+=1
        else:
            sys.exit(0)
            
        

