#!/usr/local/bin/python

'''
:py:mod:`obiannotate` : Add/Edit annotations of sequences
=========================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obiannotate` is the command that allows to add/modify/clear annotations tags attached to sequences.

Once such tags are added, they can be used by the other OBITools command for filtering purpose or for getting statistics.

The basic usage allows to specify `tag:value` annotations to be added in the definition of the sequences, the `value`
being a valid PYTHON EXPRESSION. The `tag:value` annotations are added to the definition of each the sequences and can
then be used and queried by the other OBITools commands.

Note that python expression can use two predefined variables :
    - `sequence` the sequence object itself
    - `counter` the rank of the sequence in the file


Example: To add a boolean tag named `short` indicating that the sequence is of length lesser than 100bp, 
the command would be as follows:

.. code-block:: bash

   > obiannotate -S short:'len(sequence)<100' seq1.fasta > seq2.fasta

    
Example: Clear all tags, set the identifier to the rank of the sequence in the file while keeping 
the old identifier in a tag named `oldID` and add the sequence length:

.. code-block:: bash

   > obiannotate  --clear -S oldID:'sequence.id' --set-identifier 'counter' --length seq1.fasta > seq2.fasta

'''

from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions
from obitools.options.bioseqfilter import filterGenerator
from obitools.options.bioseqedittag import addSequenceEditTagOptions
from obitools.options.bioseqedittag import sequenceTaggerGenerator
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
        
    
if __name__=='__main__':
    
    optionParser = getOptionManager([addSequenceFilteringOptions,
                                     addSequenceEditTagOptions,
                                     addInOutputOption], progdoc=__doc__)

    (options, entries) = optionParser()
    
    writer = sequenceWriterGenerator(options)
    
    sequenceTagger = sequenceTaggerGenerator(options)
    goodFasta = filterGenerator(options)
    
    for seq in entries:
        if goodFasta(seq):
            sequenceTagger(seq)
        writer(seq)
            
