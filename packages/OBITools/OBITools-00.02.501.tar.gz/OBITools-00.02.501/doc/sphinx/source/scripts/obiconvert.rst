================================================================
**obiconvert** : Convert sequence files to fasta or fastq format 
================================================================

:command:`obiconvert` [options] [filename 1] [filename 2] ...

Convert sequence files to the *extended OBITools fasta* format or to
the *sanger fastq* format. If no file name are specified data are 
read from standard input. 



.. include:: ../optionsSet/defaultoptions.txt

.. include:: ../optionsSet/inputformat.txt
            
example
-------

for converting a genbank file to fasta ::

    % obiconvert --genbank --nuc sequences.gb > sequences.fasta
    
