Wolves diet reconstruction based on DNA barcodes sequenced from a Solexa run
============================================================================

How to do a diet reconstruction from Solexa sequencing using :

- the OBITools python scripts suite
- some basic unix commands


+-------------------------------------------------------------+
| Good to remember: I'm working with tons of sequences        |
+-------------------------------------------------------------+
| It is always a good idea to have a look at the intermediate |
| results or to evaluate the best parameter of each step.     |
| Some commands are designed for that purpose, for example    |
| use :                                                       |
|                                                             |
| - :py:mod:`obicount` to count for the number of sequences   |
|   in a file                                                 |
| - :py:mod:`obihead` and :py:mod:`obitail` to view the first |
|   or last sequences of a file                               |
| - :py:mod:`obistat` to get some basic statistics (count,    |
|   mean, standard deviation) on the attributes               |
|   (attribute=value couples in the fasta header of each      |
|   sequence, see The `extended OBITools fasta format` in the |
|   :doc:`fasta format <fasta>` description) of the sequences |
| - any unix command such as ``less``, ``awk``, ``sort``,     |
|   ``wc`` to check your files                                |
+-------------------------------------------------------------+


Basic plot of the experiment of interest
----------------------------------------

+-------------------------------------------------------------+
| Good to remember: The august 2010 LECA Solexa run           |
+-------------------------------------------------------------+
| - one Solexa run with 8 `Regions`                           |
| - several experiments per `Region`                          |
| - several samples per experiment                            |
|                                                             |
| All samples put in the same `Region` should be identifiable |
| by different tag-PCR primers pairs.                         |
+-------------------------------------------------------------+


The goal of one of the experiments that was part the solexa run was to analyze the diet of wolves from feces samples with DNA barcodes 
targetting the 12S-V5 barcodes (see [#]_ and [#]_).

The experiment that interest us is :

* CL-b = Canis lupus with blocking oligos, 32 feces samples, 2 replicates with the exact same protocol + 1 experimental protocol per sample, 
  32 feces samples x (2+1))

The PCR products have been sequences in the seventh region of a Solexa run.



Data
----

The data needed to reproduce the tutorial are the following:


- the :doc:`fastq <fastq>` files resulting of the Solexa pair-end sequencing assay of DNA extracted and amplified from 
  the wolves feces and other samples (not described here)
    * ``YG_BIOSP_7_1_612GNAAXX.fastq``
    * ``YG_BIOSP_7_2_612GNAAXX.fastq``
- the file describing the primers and tags used for all samples sequenced in the seventh region of the Solexa run
    * ``NGS-R7.txt``
- the EMBL nucleotide distribution and the NCBI taxonomy formatted in the ecoPCR_ format (see the ecoPCRFormat.py utility for details)
    * ``embl_r107*`` 


Step by step analysis
---------------------

Preprocessing of reads
^^^^^^^^^^^^^^^^^^^^^^

The goal of the first step of the analysis is, from the result of a Solexa run of mixed samples, to get a sequence file that contains, for each sequence, the information 
on total counts and the list of samples it comes from.


Recover full sequence read from 5' and 3' partial reads
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using the result of a paired-end sequencing assay with supposedly overlapping 5' and 3' reads, the first step is to recover the full sequence form these two fragments.

The two separate files contain respectively the 5' and 3' reads of the same fragments *at the same line position* in the two files. 
Based on this two files, the assembly of the two fragments is done with the :py:mod:`solexaPairEnd` utility that aligns the two fragments and returns the reconstructed 
sequence.

In our case, the command would be: 

.. code-block:: bash

   > solexaPairEnd -r YG_BIOSP_7_2_612GNAAXX.fastq YG_BIOSP_7_1_612GNAAXX.fastq > region_7.fastq

Note: Of course, this step is only needed in case of *pair-end sequencing* with an insert size compatible with the alignment of the 5' and 3' reads.


Assign each read to its sample
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to assign each read to its original sample, one use the information of the primer sequences used for the PCR step. In most of the cases, oligo tags are added 
so that samples amplified with the same PCR primers pairs can be discriminated. The design of such oligo tags is explain in detail in the description of 
the oligoTag_ program. Such tags and primers are described in a file used by the :py:mod:`ngsfilter` program to recover, for each read, the sample it comes from.


The PCR primers pair used for our samples are described in [#]_ and they were especially designed to allow the identification of vertebrates:

+----------+-----------------------------------------+-------------+------------+---------------+-----------------------+----------+
|  Primer  |             Name Sequences              |     Tm      |  Amplified |    Quality    |  Fragment size (bp)   |  Region  |
|          +--------------------+--------------------+------+------+------+-----+-------+-------+------+------+---------+          |
|          |      Direct        |        Reverse     |  P1  |  P2  |  Es  |  Cs |  Bc   |  Bs   | Min  |  Max | Average |          |
+==========+====================+====================+======+======+======+=====+=======+=======+======+======+=========+==========+
| 12S-V5   | TAGAACAGGCTCCTCTAG | TTAGATACCCCACTATGC | 52.3 | 50.7 | 1236 |  7  | 0.980 | 0.720 |  73  |  110 |  98.32  |  12S RNA |
+----------+--------------------+--------------------+------+------+------+-----+-------+-------+------+------+---------+----------+

As there are 32 samples in our experiment, 8-mer were added to the PCR primers, one sample being identified by one and only one such tag.


The ``NGS-R7.txt`` file contains the descriptions for all samples/experiments that were put in the seventh region. Our experiment is named `CL-b`, thus 
to check the 10 first sample descriptions concerning the wolf experiment, just type :

.. code-block:: bash

   > egrep '^CL\-b' NGS-R7.txt | head -10

Here is the output with the sample descriptions:

.. code-block:: bash

    CL-b    1a_2701037      aacaaca TAGAACAGGCTCCTCTAG      TTAGATACCCCACTATGC      F       @       "user=Wasim_Christian_Carole;"  "position=A1;"  "expected=0.04167;"     region=7
    CL-b    2a_2702034      aacacac TAGAACAGGCTCCTCTAG      TTAGATACCCCACTATGC      F       @       "user=Wasim_Christian_Carole;"  "position=B1;"  "expected=0.04167;"     region=7
    CL-b    3a_2702086      gaaggcc TAGAACAGGCTCCTCTAG      TTAGATACCCCACTATGC      F       @       "user=Wasim_Christian_Carole;"  "position=C1;"  "expected=0.04167;"     region=7
    CL-b    4a_2702069      tggtggc TAGAACAGGCTCCTCTAG      TTAGATACCCCACTATGC      F       @       "user=Wasim_Christian_Carole;"  "position=D1;"  "expected=0.04167;"     region=7
    CL-b    5a_2702070      tggccac TAGAACAGGCTCCTCTAG      TTAGATACCCCACTATGC      F       @       "user=Wasim_Christian_Carole;"  "position=E1;"  "expected=0.04167;"     region=7
    CL-b    6a_2703131      aatgtcc TAGAACAGGCTCCTCTAG      TTAGATACCCCACTATGC      F       @       "user=Wasim_Christian_Carole;"  "position=F1;"  "expected=0.04167;"     region=7
    CL-b    7a_2702055      atctctc TAGAACAGGCTCCTCTAG      TTAGATACCCCACTATGC      F       @       "user=Wasim_Christian_Carole;"  "position=G1;"  "expected=0.04167;"     region=7
    CL-b    8a_2703107      gaggctt TAGAACAGGCTCCTCTAG      TTAGATACCCCACTATGC      F       @       "user=Wasim_Christian_Carole;"  "position=H1;"  "expected=0.04167;"     region=7
    CL-b    9a_2702033      ttatgtg TAGAACAGGCTCCTCTAG      TTAGATACCCCACTATGC      F       @       "user=Wasim_Christian_Carole;"  "position=A2;"  "expected=0.04167;"     region=7
    CL-b    13a_F730603     aattaac TAGAACAGGCTCCTCTAG      TTAGATACCCCACTATGC      F       @       "user=Wasim_Christian_Carole;"  "position=B2;"  "expected=0.04167;"     region=7


This file is a tab separated column file, the columns correspond to :

:Column 1:
   Experiment name, will be reported in the header of each matched read as ``experiment=experiment name``  

:Column 2:
   Sample name, will be reported in the header of each matched read as ``sample=sample name``

:Column 3:
   Oligo tag used to identified the sample

:Column 4 and 5:
   Forward and reverse primers used for the PCR step

:Column 6:
   If it is *Partial* ?

:Extra information:
   All text that is after the ``@`` symbol is considered as extra information that will be added to each read that is associated
   to this sample.

.. code-block:: bash

   > ngsfilter -t NGS-R7.txt region_7.fastq > regions_7.assigned.fastq


Keep only the reads of the wolf experiment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To keep working on the wolf sequences only, we select the reads by taking advantage of the ``experiment=CL-b`` information that has been added to the reads header
at the previous step.

.. code-block:: bash

   > obigrep -a 'experiment:CL\-b'  regions_7.assigned.fastq > CL-b.fastq


The file `` CL-b.fastq`` thus contains all reads concerning the wolf experiment.

Dereplicate reads into uniq sequences
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The same DNA molecule can have been read several times by the sequencing machine. In order to reduce the file size (and computations) and get easier interpretable results, 
it is convenient to work with uniq *sequences* instead of *reads*. To *dereplicate* such *reads* into uniq *sequences*, we use the :py:mod:`obiuniq` command.

+-------------------------------------------------------------+
| Definition: Dereplicate reads into uniq sequences           |
+-------------------------------------------------------------+
| 1. compare all the reads in a data set to each other        |
| 2. group strictly identical reads together                  |
| 3. output the sequence for each group and its count in the  |
|    original dataset (in this way, duplicate reads are       |
|    removed from a library)                                  |
|                                                             |
| Definition adapted from [#]_                                 |
+-------------------------------------------------------------+


We use the :py:mod:`obiuniq` command with the ``-m sample``. The ``-m sample``option is used to keep the information of the samples of origin for each sequence.

.. code-block:: bash

   > obiuniq -m sample CL-b.fastq > CL-b.uniq.fasta


To see exactly what has been added to the sequence header we can check the first sequence of the file:

.. code-block:: bash

   > obihead --without-progress-bar -n 1 CL-b.uniq.fasta


This print the output:

.. code-block:: bash

  >HELIUM_000100422_612GNAAXX:7:1:1138:1664#0/1_CONS_SUB  seqAInsertion=0; tag_length=7; reverse_match=ttagataccccactatgc; seqADeletion=0; reverse_primer=ttagataccccactatgc; alignment=left; merged_sample={'19c_F730627': 1, '13a_F730603': 1}; cut=[27, 127, 1]; direct_match=tagaacaggctcctctag; direct_primer=tagaacaggctcctctag; experiment=loup-P09-R7; expected=0.04167; reverse_score=72.0; seqBInsertion=0; seqBDeletion=0; user=Wasim_Christian_Carole; direct_score=72.0; count=2; region=7; seqASingle=46; seqBSingle=46; 
  aagggtataaagcaccgccaagtcctttgagttttaagctattgccnnnnnnnnnnnnnn
  gaatagttttgtttgcataactatttgtgtttaaggctag


The run of :py:mod:`obiuniq` has added two key=values entries in the header of the fasta sequence :
   - :py:mod:`merged_sample={'19c_F730627': 1, '13a_F730603': 1}` : this sequence have been found once in two samples
   - :py:mod:`count=2` : the total number of counts for this sequence is 2 

To keep only these two ``key=value`` informations, we can use the :py:mod:`obiannotate` command:

.. code-block:: bash

   > obiannotate -k count -k merged_sample CL-b.uniq.fasta > $$ ; mv $$ CL-b.uniq.fasta


Denoising the sequence dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To have a set of sequences assigned to their original samples does not mean that all sequences are *biologically* meaningful i.e. some of these sequences can contains 
PCR and/or sequencing errors or the result of the sequencing of PCR chimeras. To remove such sequences as much as possible, we first remove rare sequences and then remove
sequences variants from the original dataset.


Get the counts statistics
~~~~~~~~~~~~~~~~~~~~~~~~~

In that case, we use :py:mod:`obistat` to get the counting statistics on the 'count' attribute (the count attribute has been set by the :py:mod:`obiuniq` command). By piping 
the result in the unix commands ``sort`` and ``head`` we keep only the counting statistics for the 20 lowest values of the 'count' attributes.

.. code-block:: bash

   > obistat -c count CL-b.uniq.fasta | sort -nk1 | head -20

This print the output:

.. code-block:: bash

    count     count     total
    1         95697     95697
    2          4974      9948
    3          1733      5199
    4           927      3708
    5           610      3050
    6           385      2310
    7           314      2198
    8           266      2128
    9           202      1818
    10          161      1610
    11          149      1639
    12          127      1524
    13          118      1534
    14           91      1274
    15           76      1140
    16           67      1072
    17           62      1054
    18           57      1026
    19           51       969
    
Keep only the sequences having a count greater or equal to 10
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on the previous observation, we set the cut-off for keeping sequences for further analysis to a count of 10. To do this, we use the :py:mod:`obigrep` command.
The ``-p 'count>=10'`` option means that the ``python`` expression :py:mod:`count>=10` must be evaluated to :py:mod:`True` for each sequence to be kept.

.. code-block:: bash

   > obigrep -p 'count>=10' CL-b.uniq.fasta > CL-b.uniq.10.fasta



Clean the sequences for PCR/sequencing errors (sequence variants)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a final step of denoising, using the :py:mod:`obiclean` we keep the `Head` sequences (``-h`` option) that are sequences with no variants with greater count or 
sequences with no variants with 20-fold greater (``-r 0.05`` option).

.. code-block:: bash

   > obiclean -s merged_sample -r 0.05 -H CL-b.uniq.10.fasta > CL-b.uniq.10.heads.fasta


Taxonomic assignment of sequences
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The taxonomic assignement of sequences requires a reference database compiling all possible species to be identified in the sample. The assignment is then done 
based on sequence comparisons between the sample sequences and the reference sequences.


Build a reference database
~~~~~~~~~~~~~~~~~~~~~~~~~~

To build the reference database, we use the :py:mod:`ecoPCR` program to simulate a PCR and to extract all sequences from the embl that may be amplified by the two
primers (`TAGAACAGGCTCCTCTAG` and `TTAGATACCCCACTATGC`) extracted from the samples description used to assign each read to its sample (file ``NGS-R7.txt``).
 

Retrieve the sequences
......................

.. code-block:: bash

   > ecoPCR -d /Volumes/R0/Barcode-Leca/embl_r107 -e 3 -l 60 -L 150 TAGAACAGGCTCCTCTAG TTAGATACCCCACTATGC > v5.ecopcr
   
Clean the database
..................


    1. filter the sequences so that they have a good taxonomic description

    2. remove redundant sequences

    3. ensure sequences have a taxid
       
    4. ensure that sequences have uniq names

.. code-block:: bash

   > obigrep -d /Volumes/R0/Barcode-Leca/embl_r107 --require-rank=species --require-rank=genus --require-rank=family v5.ecopcr > v5.clean.fasta

   > obiuniq v5.clean.fasta > v5.clean.uniq.fasta

   > obigrep -A taxid v5.clean.uniq.fasta >  db_v5.fasta

   > gawk '/^>/{gsub(/^>/,"",$1);if ($1 in tab) {notuniq[$1]}tab[$1];}END{for (id in notuniq) {print id;}}'  db_v5.fasta

   DQ993168
   EU547102
    
In that particular case, we had to remove by hand one of the two 'DQ993168' and 'EU547102' sequences in db_v5.fasta that were duplicated *and should not be* 
in db_v5.fasta


Assign each sequence to a taxon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the reference database is built, one can compare the sequences to the database to do the taxonomic assignment. This is done with the :py:mod:`ecoTag` command.

.. code-block:: bash

   > ecoTag -d /Volumes/R0/Barcode-Leca/embl_r107 -R db_v5.fasta CL-b.uniq.10.heads.fasta > CL-b.uniq.10.count-merged_sample.heads.ecotag.fasta


The :py:mod:`ecoTag` adds several `key=value` pairs, omong them are :

- best_match=ACCESSION where ACCESSION is the id of the sequence in the reference db that best align to the sequence
- best_identity=FLOAT where FLOAT*100 is the percentage identity between the best match sequence and the sequence
- taxid=TAXID where TAXID is the final assignation of the sequence by ecoTag (may be different of the taxid of the best matching sequence)
- scientific_name=NAME where NAME is the scientific name of the assigned taxid


Clean tags of sequences and generate an excel result file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a final step, for example, to facilitate the analysis, one can remove some unuseful informations, sort the sequences by their count and export the result as
a TAB separated text file. 

.. code-block:: bash

   > obiannotate --delete-tag=father --delete-tag=fathers --delete-tag=clean CL-b.uniq.10.count-merged_sample.heads.ecotag.fasta | obisort -k 'count' -r | obitab -o > CL-b.uniq.10.count-merged_sample.heads.ecotag.csv 


References
----------

.. _oligoTag: http://www.grenoble.prabi.fr/trac/OBITools/wiki/oligoTag.py
.. [#] Shehzad et al., Mol. Ecol., 2012 
.. [#] Riaz et al., NAR, 2011 
.. [#] Riaz et al., NAR, 2011 
.. [#] Seguritan and Rohwer, BMC Bioinformatics, 2001
.. _ecoPCR:   http://www.grenoble.prabi.fr/trac/ecoPCR


Contact
-------

For any suggestion and improvement of this tutorial, please contact :

- eric.coissac@metabarcoding.org
- frederic.boyer@ujf-grenoble.fr


