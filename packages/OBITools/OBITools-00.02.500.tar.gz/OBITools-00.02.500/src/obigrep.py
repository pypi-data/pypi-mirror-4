#!/usr/local/bin/python
'''
:py:mod:`obigrep` : Filter sequences 
====================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obigrep` command is in some way analog to the standard Unix `grep` command.
It select a subset of sequences from  :ref:`a sequence file<the-sequence-files>`. 
But instead of working text line by text line as the standard tool, selection is done sequence by sequence. 
Moreover :py:mod:`obigrep` allows the user to specify several conditions (that take the value TRUE or FALSE) and only the sequences
that fulfill all the conditions  (all conditions are TRUE) are printed.

A sequence is more complex than a single text line and it can be split in several parts:

- the identifier (the character string just after the '>' character)
- the definition (the set of [tag=value ;]* strings just after the sequence identifier)
- the sequence itself


Depending on the options, the conditions can either concern the sequence part (e.g. some pattern to be found in the DNA sequence), the identifier or
 any of the (tag,values) pairs contained in the definition part of the sequence (see :ref:`the OBITools extension of the FASTA and FASTQ formats<obitools-fasta>`).
A large set of options allows to refine selection on each one of these elements.


Note that the '-v' option invert the selection.


Example: Keep only the sequences that contains of stretch of at least 10 'A' :

.. code-block:: bash

   > obigrep -s '.*A{10,}.*' seq1.fasta > seq2.fasta


Example: Keep only the sequences that have a sequence length equal or longer than 100bp :

.. code-block:: bash

   > obigrep -l 100 seq1.fasta > seq2.fasta


Example: Keep only the sequences that have a sequence length equal or shorter than 100bp :

.. code-block:: bash

   > obigrep -L 100 seq1.fasta > seq2.fasta

'''


from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions
from obitools.options.bioseqfilter import sequenceFilterIteratorGenerator

if __name__=='__main__':
    
    optionParser = getOptionManager([addSequenceFilteringOptions,addInOutputOption],progdoc=__doc__)
    
    (options, entries) = optionParser()
    goodSeq   = sequenceFilterIteratorGenerator(options)

    writer = sequenceWriterGenerator(options)
    
    for seq in goodSeq(entries):
        writer(seq)
            
            
