File formats usable with OBITools
=================================

.. _the-sequence-files:

The sequence files
------------------

Sequences can be stored following various format. OBITools knows
some of them. The central format for sequence files manipulated by OBITools scripts 
is the :doc:`fasta format <fasta>`. OBITools extends the fasta format by specifying 
a syntax to include in the definition line data qualifying the sequence.
All file formats use the :doc:`IUPAC <iupac>` code for encoding nucleotides and 
amino-acids.

.. toctree::
   :maxdepth: 2
   
   iupac
   fasta
   fastq
   descriptions
   genbank
   embl


The taxonomy files
------------------

Many OBITools are able to take into account taxonomic data. These data
are manipulated following the `NCBI taxonomy`_.

.. toctree::
   :maxdepth: 2
   
   taxdump
   obitaxonomy 

The ecoPCR files
----------------

ecoPCR_ is a software developed in LECA_. It simulates a PCR experiment by
selecting in a sequence database, sequences matching simultaneously two 
primers sequences in a way allowing a PCR amplification of a DNA region.

The ecoPrimer files
-------------------


The OBITools files
------------------


.. _ecoPCR: http://www.grenoble.prabi.fr/trac/ecoPCR
.. _LECA: http://www-leca.ujf-grenoble.fr
.. _`NCBI taxonomy`: http://www.ncbi.nlm.nih.gov/taxonomy