The fasta format
================


The fasta format is certainly the most widely used sequence file format. 
This is certainly due to its great simplicity. It was originally created 
for the ''Lipman'' and ''Pearson'' `FASTA program`_. OBITools use in more
of :ref:`the classical fasta format <classical-fasta>` several extended 
version of this format where structured data are included in the title line.


.. _classical-fasta:

The fasta format
----------------

In fasta format a sequence is represented by a title line beginning with a **>** character and
the sequences by itself following :doc:`iupac`. The sequence is usually split other severals
lines of the same length (expected for the last one) ::


    >my_sequence this is my pretty sequence
    ACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGT
    GTGCTGACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTGTTT
    AACGACGTTGCAGTACGTTGCAGT
 

This is no special format for the title line excepting that this line should be unique.
Usually the first word following the **>** character is considered as the sequence identifier.
The end of the title line corresponding to a description of the sequence.

Several sequences can be concatenated in a same file. The description of the next sequence
is just pasted at the end of the description of the previous one ::


    >sequence_A this is my first pretty sequence
    ACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGT
    GTGCTGACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTGTTT
    AACGACGTTGCAGTACGTTGCAGT
    >sequence_B this is my second pretty sequence
    ACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGT
    GTGCTGACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTGTTT
    AACGACGTTGCAGTACGTTGCAGT
    >sequence_C this is my third pretty sequence
    ACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGT
    GTGCTGACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTGTTT
    AACGACGTTGCAGTACGTTGCAGT

.. _obitools-fasta:

The extended OBITools fasta format
----------------------------------

The *extended OBITools Fasta format* is a strict :doc:`fasta format file <fasta>`.
The file in *extended OBITools Fasta format* can be readed by all programs
reading fasta files.

Difference between standard and extended fasta is just the structure of the title
line. For OBITools title line is divided in three parts :

        - Seqid : the sequence identifier
        - key=value; : a set of key/value keys
        - the sequence definition


::

    >my_sequence taxid=3456; direct=True; sample=A354; this is my pretty sequence
    ACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGT
    GTGCTGACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTGTTT
    AACGACGTTGCAGTACGTTGCAGT

Following these rules, the title line can be parsed :

        - The sequence identifier of this sequence is : *my_sequence* 
        - Three keys are assigned to this sequence :
              - Key *taxid* with value *3456*
              - Key *direct* with value *True*
              - Key *sample* with value *A354*
        - The definition of this sequence is this is *my pretty sequence* 

Values can be any valid python expression. If a key value cannot be evaluated as
a python expression, it is them assumed as a simple string. Following this rule,
taxid value is considered as an integer value, direct value as a boolean and sample
value is not a valid python expression so it is considered as a string value.




.. _`FASTA program`: http://www.ncbi.nlm.nih.gov/pubmed/3162770?dopt=Citation