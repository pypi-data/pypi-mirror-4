#!/usr/local/bin/python
"""
:py:mod:`obicomplement` : Reverse complement sequences 
======================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obicomplement` allows to reverse complement the sequences in a file.

Note that the identifiers 'ID' of the sequences are modified and are of the form 'ID_CMP'.

Example: 
.. code-block:: bash

   > obicomplement seq.fasta > seqRC.fasta


"""

from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions
from obitools.options.bioseqfilter import filterGenerator
from obitools.format.options import addInOutputOption, sequenceWriterGenerator


if __name__=='__main__':
    
    optionParser = getOptionManager([addSequenceFilteringOptions,addInOutputOption], progdoc=__doc__)
    
    (options, entries) = optionParser()
    
    goodFasta = filterGenerator(options)
    writer = sequenceWriterGenerator(options)
    
    for seq in entries:
        if goodFasta(seq):
            writer(seq.complement())
        else:
            writer(seq)

            