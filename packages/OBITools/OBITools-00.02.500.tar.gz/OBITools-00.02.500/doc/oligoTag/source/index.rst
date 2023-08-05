.. oligoTag documentation master file, created by
   sphinx-quickstart on Tue Feb  9 11:30:02 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

OligoTag's documentation!
=========================

Contents:

.. toctree::
   :maxdepth: 2

Overview
--------

Sequencing a huge number of PCR amplicons using high throughput sequencing platforms 
involves using sample-specific oligonucleotide tags for allowing sample multiplexing and 
sorting out of the sequences during the data processing. OligoTags helps in designing 
sets of tags. Several parameters allow users to define the characteristics of the 
generated tags in term of family size, tag length, minimal distance between them, 
GC content and presence of homopolymers.

OligoTags is based on the clique notion from the graph theory.

To determine the tags properties you should take into account severals experiment parameter. 
Using some simple statistical models? and these experiment characteristics it is roughtly 
easy to determine tag properties. The main questions you need to asnwer are :

    * How many samples do you want to multiplex ? 

    * Will you be able to sequence the both extremities of the PCR products ? 

    * How many sequences will be read for all the multiplexed samples ? 

    * How many miss-assignation can you tolerate ? 

    * How many reads can you loose during tag assignation process ? 

Tag family building
-------------------

The simplest way to build a tag family is to enumerate all the combinations of {A,C,G,T} forming
words of size k. We know that it exists 

.. math::

    N_K = 4^k\; \;\text{words of size k}
    
If we need to tag *n* samples, we have to use tag of size

.. math::

    k=\left\lceil \frac{\log n}{\log 4} \right\rceil
    
As example for tagging 50 samples you need to use words of size :

.. math::

    k=\left\lceil \frac{\log 50}{\log 4} \right\rceil = \left\lceil 2.8219280948 \right\rceil =3
    
Using this size of words allows you enumerate 64 different words. But sequencing, primer synthesis and 
PCR reactions are not error proof processes. And the signal we read at the end of the process is
noised. We have to think to this when we design tagging system.

.. math::

    AGT  \xrightarrow[\text{Reading process}]{} AG\boldmath{C}
    
If we consider *m* the probability to erroneously read a position we can define the probability *P* to read
a tag of size *k* with *e* errors as :

.. math::

    P_{k,e,m} = \binom{e}{k} \, m^e \, (1-m)^{(k-m)}

with :

.. math::

    \binom{e}{k} = \frac{k!}{e!\;(k-e)!}
      
    
        
Errors on tag reading
---------------------

Which parameters should I set for building my tag set ? The main objective, 
that each user of oligoTag should reach is to generate a set of tags that will
not lead to the misassignation of sequences to samples. 



.. math::

   \bar{T}_{l,e}=\binom{l}{e}\;m^e\;(1-m)^{l-e}\;S

The oligoTag unix command
-------------------------

Command line prototype
......................

- Options between square braquets are not necessary, others options are    
  mandatory. 
- **###** represente a numerical argument.
- names between **<** and **>** represente string argument

  oligoTag.py -h | -s ### -f ### [-d ###] [-g ###] [-a <pattern>] [-r <pattern>] 
  [-p ###] [-P ###] [-T ###] [-L <FILENAME>] 

options
.......

General options
,,,,,,,,,,,,,,,

    * -h, --help show this help message and exit 

    * -T <seconde>, --timeout=<seconde> 

        timeout to identify a clique of good size

Tag description options
,,,,,,,,,,,,,,,,,,,,,,,

    * -L <filename>, --oligo-list=<filename> 

        filename containing a list of oligonucleotide

    * -s <###>, --oligo-size=<###> 

        Size of oligonucleotide to generate

    * -f <###>, --family-size=<###> 

        Size of oligonucleotide family to generate

    * -d <###>, --distance=<###> 

        minimal distance between two oligonucleotides

    * -g <###>, --gc-max=<###> 

        maximum count of G or C nucleotide acceptable in a word

    * -a <IUPAC pattern>, --accepted=<IUPAC pattern> 

        pattern of accepted oligonucleotide

    * -r <IUPAC pattern>, --rejected=<IUPAC pattern> 

        pattern of rejected oligonucleotide

    * -p <###>, --homopolymere=<###> 

        reject oligo with homopolymere longer than.

    * -P <###>, --homopolymere-min=<###> 

        accept only oligo with homopolymere longer or equal to.

Debugging options
,,,,,,,,,,,,,,,,,

    * --DEBUG Set logging in debug mode
    * --no-psyco Don't use psyco even if it installed
    * -E <filename>, --bad-pairs=<filename> 

        filename containing a list of oligonucleotide



outputs
.......

command line examples
.....................

::

    oligoTag.py -s 4 -f 1 -d 3 -p 2 -r cnnn | awk '((NR-1) % 8 ==0) {print ""} {printf("\t%s",$1)} END {print ""}'

Sets of precomputed tags
------------------------

With at least three differences between tags
............................................

All tag sets were builded with the following common parameters

:Minimum distance:  3
:Maximum homopolymer: 2


Tag size: 4
,,,,,,,,,,,

:Pattern: NNNN
:Tag count: 11

::

        aaca    acac    ctcc    gctt    tatc    aggt    tccg    tgaa
        gtga    attg    caag
    
Tag size: 5
,,,,,,,,,,,

:Pattern: NNNNN
:Tag count: 33

::

        aacaa   aagcc   gactt   gtaat   cgagg   aatgg   cgcat   acaac
        tctaa   gtcca   ggtta   attct   accgt   gtggc   caatc   gccag
        acgta   tgatt   taacg   gcgct   agaca   catca   tacgc   ctgtt
        tgtcc   agctc   aggag   ttaga   cttag   tagat   gatac   cctgc
        atatg

Tag size: 6
,,,,,,,,,,,

:Pattern: NNNNNN
:Tag count: 108

::

        aacaac aaccga ccggaa agtgtt ccgctg aacgcg ggctac ttctcg ttctcg
        tcactc gaacta ccgtcc aagaca cgtgcg ggtaag ataatt cgtcac cgtcac
        ttgagt aagcag ttgcaa cacgta taacat tgcgtg ggtcga cactct cactct
        cttggt tccagc acttca gcgaga tggaac gtacac aagtgt tcttgg tcttgg
        aaggtc ggcgca tcgacg cctgtc agaaga aatagg ggttct taatga taatga
        gtaaca aatcct agaccg tggcgg ctataa aatgaa cgaatc agagac agagac
        ttcgga cgacgt ctcatg tgtata acaacc tcagag gtagtg agcact agcact
        gcggtt acacaa gctccg tacttc gttgcc gtatgt gtcaat agcctc agcctc
        tcgtta tgtggc ctctgc atggat acaggt tccgct gtccgg cattag cattag
        gaagct gatatt agctgg cgcgat acattg ccaagg accata aggatg aggatg
        gtctta tatacc acctat aggtaa attcta gtgatc gacggc gtgcct gtgcct
        tatctg cggcca cctaat acgcgc gtgtag ttcctt cagagc tgatcc tgatcc  
        
              
Tag size: 7
,,,,,,,,,,,

:Pattern: NNNNNNN
:Tag count: 316

::

        aacaaca aacacac tccgact tgcctgc cgtcgca ggtcagt ccgctag acgcggc acgcggc
        gaagctg aacaggt gccggcc ggtcgag taagcct aacattg aaccaag agtgaag agtgaag
        ccggatc ggtctcc aaccgcc ccggcct ttcggcg agtgcca taagtgg acggcga acggcga
        tcctaag aacctga ggtgatc acggtac aacgagc tggcacc taatagt ccgtaat ccgtaat
        gaatgat aacgccg caagtat acgtacc ggtccta aacggaa tcctgca ggtgtga ggtgtga
        taattaa ggttaca tccttgt aagagta ccgttca aactatt tccgcgc agttggc agttggc
        cctaacg ggttcgg gacataa ataacgc actaagt gcgatcc tcgagcg tacagtc tacagtc
        ggttgtt gtaacag ctcacct ataagtg cctagga aagaagg gcctctg tgtatag tgtatag
        aagacct gtaagct tggccgt tcgcagg gcgcctt taccgat tcgccac gtaatga gtaatga
        gaccttc cctcata gtacaat cctccgc cacgctt gacgcga tcgctct aagcatc aagcatc
        gtacctc aagccaa cgtgact actctaa taaggta gacgtct gtactcg gcttgaa gcttgaa
        cctgcaa aagctcg gtagacc tgtgctg aaggaat tactacc tcggttg cacttac cacttac
        gtagcgt cctggtg gtaggaa tatactt actggct tactcta ctagtta cctgtgt cctgtgt
        atatact gcgtgtc gagaatt gtatagg gaatata acttcag taagaac gtatcca gtatcca
        aagtcgc caatgtc gctactc aagtgag cgctcgt cgaacat ctattgt agaaccg agaaccg
        gtattac ctcaata tagatac gtcaacg agaagga aatacga agaatac cgaattg cgaattg
        tctacca aatagcg gtcagac cagctgt ggtgcat aatatat ttaccga agacagg agacagg
        aatcact ctccgaa agacgat atcctat tagctta aatcctg taggaga agactca agactca
        tctcgcc gtccgtg acaagcc cagtatg taggctc agagatt ctcgcgg cgaggcc cgaggcc
        gtcgatt gcttagc tagtccg gcttcct gtcgtag tcttatt aatgtcc gagttga gagttga
        agtaacc atctctc tagtgtt aattaac ttatctg cagaggc gtccaga cgatgaa cgatgaa
        ttatgcc agatcta tataagc gtctcat ctctggc ggaagtc catattc ctcttcg ctcttcg
        tatagaa cgcaagg ttcacaa catcagg acaacaa tacgatg tgtggac ctgacac ctgacac
        tgaatct agcactt catcgac gtgaagc agcagag ttcatcc gtgacta acaatgg acaatgg
        ttccaac acacaac atgcagt tgacgcg agccata gtgatat acaccgt cgagaga cgagaga
        acacgta gtgccgg ctgcgtt gatggca gactgcg acagaca atggcag ctggacg ctggacg
        cggttgc cattcat cgcggat agcggtc acagctc atggtct acaggag cgcgtca cgcgtca
        ttcgtga agcgtgg tcgaata agctacg tgatcac cgctatc ctgtaga gtggttc gtggttc
        acatatg agcttaa atgttgg cgtctat cggaaca ggcagca acattat tacacgg tacacgg
        tcaagtt gtgtggt accaatc ttgagga cttagat ctacatg aatgata aggatgt aggatgt
        accatct cttatca gcactgc accgcat cggcctc gttattg ttgcgag cttccag cttccag
        aggcgtg attcttc accgtta gttcggc acctaga gtgcgca ccatcga tcagtcc tcagtcc
        aggtcat ttggcca cttgagc attgctt ccatgcg aggtgca acctgac gttgccg gttgccg
        ttgtatc ctgctcc tgtaggt caaccta tgctgtg acgactg caacgct gccacgt gccacgt
        taacaca acgagat ttgaact taaccag agtatta taacggc agtccac gccgagg gccgagg
        caagcgc     
            
Tag size: 8
,,,,,,,,,,,

:Pattern: NNNNNNNN
:Tag count: 347

::

        acacacac acacagca agcgctcg gtctagtc tgcatacg gtctatat acacatgt acacgacg
        gcagctcg tgcatcac gtctcaca acacgcga tgctgata atgtctgc ctgatgta gcagtcac
        agcgtgat tgcatgta ctgcacta tgcgacag acactagc gcagtgca agctactc acactctg
        tgcgagca acactgat gcatacgt acatgata cacacacg gtctgcag acagacta acagagag
        tgcgatgc cacacgac agctatgt tgcgcact gtctgtgc tgcgcgac cgtcgagc gtgacact
        acagcaca cacactga acgtacga gtgacgag gcgatagt cacagagc cacagcag acagcgtc
        tgcgtaga acagctat gcatctga gtgagaga cacagtct agacgctc tcagatac cacatata
        acagtcgt gtgagtac tgctacga cacatcgt ctgtagcg cgcgcgta agacgtag tgctagat
        tcagcgct gtgatatc cacgacac cagtgtga ctgatacg tgctatcg acatatcg tgctcagc
        ctgtcgtc acatcagt tgctcgtg cacgcatc gtgcagtg tcagtgtg tagctgat gtgcatca
        gcgagtcg tcatactc ctgtgctg gtgcgacg acatgcag ctgtgtct tgctgtac cacgtact
        agtatgca cacgtctg acatgtgc tgtacaga acgacacg agtcacgt gacacgta tgtacgat
        acgacgac tcatctag gtgctcat tgtactcg cactacta acgactga tgtagact tctgtcgc
        acgagagc tgtagcag ctactcgt acgagcat cactcagt tgtagtgc cactcgca gagcgcta
        tgtatatc gacatctc acgatata tgcagtca tgtatcgt gtgtcatg tcacgatc tcgactct
        agtctgtc acgatgct ctgcatat agtgactg tgtcagcg acgcagtc acgcatag agtgatac
        gacgcaga tgtcatga gcgtagta cagacgct gacgcgct tgtcgatg gcatagac acgcgtca
        cagagaca tgtcgtat ctagacat cacgagcg tacactat cagagctc tgtctcta tctgcata
        gcgtgcgc gactacgc tacagcta gactagag tcacgtct acgtagat cagatgag gtgtacac
        cgtcgtca tcgcgcgt tgtgagtc gctacatg cagcacag tgtgatct acgtcatc cgtctcag
        cagcagca atacgcat acgtcgca tcgctcac gactctac cagcatgc gactgact cagcgagt
        gtagtatg tcgtacag tgatcaca cagcgtcg atactgcg tgtgtgag tcgtatca cagctatc
        cagctcga gtcatgcg gctatgtc actacgta cgtgctat actactag gagactca cacgctag
        actagaca cagtacgt cagtagac gagagcgt tacgtgtc actagctc cgtgtgct actagtgt
        catgtcat gctcgctg ctgatcgc actatcga atagtctc cagtctat gctctata ctacgact
        gctctcgt atatactg gctctgag atatatac tcgctacg gcatcgtg gctgacga ctacgtga
        atatcacg tactgcat agctgacg gctgagct ctactata gctgatag gacatgat actcgtac
        atatcgta catacgtg tagacagc actctact tctatctg gagctaca catagcga agcacaca
        tcgacgtg catagtac atatgtca actgacat tctcagta ctagatgc tatgtgca tagagatg
        atcacatg tcgtcaga ctagcgac gagtactg tctcgaga atcacgct actgatca gagtagct
        gtacacag ctagctca actgcagc ctctgcgt actgcgcg catcactc atcagcac cactgatg
        catcagat tgtcacac atcagtcg actgtatg gtacgcgc catcgata gagtgatc actgtgac
        tagcatct atcatgtc catctacg atcgacga agacagtg atgcgtgt atcgagac ctatcgct
        gtactgtc agacgagt atctctag atcgatct gatactgt gatagacg atcgcagt gtagagta
        tctgctgt agactaca catgagta gacgatca ctatgtag gtagcagc catgcaca atcgtata
        gatatagc ctatgagc gcgtgtat gatatcag agagacgc agagagct catgctgc gtagtcga
        tagtcgcg gtagtgat atctagca agagcatg cgacacga gctcatgc agagctga cgacagac
        gatcgcac tgactcat agagtcag cgacatcg gatcgtct atctgaga agagtgta agatacat
        tcgtgcta gtatgcta agatcgac atgactat atagtact ctcgtagc agatctct tatatgac
        gatgcgac atgagcta ctcgtgca cagtcata atgatcag tagatact tatcatag cgagcgcg
        gatgtcta agcacgag ctctatga atgcacgc cgagtagt agcactgc atgcagct agcagatc
        agcagcga tatctagt gtcgactg agcagtat atgcgatc cacgatgt cgatagca agcatagt
        tatctgtg tgatgcgc acgtgact tatgacgt agcatctg atgctaga ctgcgcac tagtgtag
        atgctgac cgatctgc cgtgtctc
        
 
Tag sets not starting by a C
............................

All tag sets were builded with the following common parameters

:Minimum distance:  3
:Maximum homopolymer: 2

Tag size: 4
,,,,,,,,,,,

:Pattern:   DNNN
:Tag count: 10

::

        aaca    acac    gtga    tgaa    gcct    tagc    aggt    ggtc
        attg    gaag

Tag size: 5
,,,,,,,,,,,

:Pattern:   DNNNN
:Tag count: 25

::

        aacaa   aagcc   tagat   agaca   gccag   atatt   ggaat   accgt
        gctcc   aatgg   acaac   tactg   tgtac   tcact   aggag   ttaag
        agctc   ttcca   gacgc   gttaa   gaacg   gtgtg   tctga   acgta
        ttggc
        
Tag size: 6
,,,,,,,,,,,

:Pattern:   DNNNNN
:Tag count: 75

::

        aacaac  aaccga  ggtatt  tcatga  agtgtg  gcctcc  aacgcg  ttgcgt
        tgctaa  ggtcgg  taacgg  ttggaa  agttgc  gacagt  gcgaag  aagaca
        tggaac  taagct  ataatt  ttgtcc  aagcag  gccgtg  tggcca  taattc
        gttgta  tacatg  gaatca  acttca  gtacga  aagtgt  tggttg  tgcgcc
        agaaga  tgtacg  gtagcc  gctaga  aatcct  agaccg  ttcaat  tgtcat
        gtatag  gctcac  aaggtc  aatgaa  agagac  gagtac  tccagc  gtcacg
        atcggc  tgtgga  gatacc  acaacc  ttaaca  agcact  acacaa  ttacac
        tctgag  acgcgc  acaggt  atggct  ttagtg  acattg  atgtta  accata
        ggatgt  gtgctc  aatagg  acctat  ttccta  agcctc  ttctgg  ggcgat
        gaacat  gcgcct  tcactt
        
Tag size: 7
,,,,,,,,,,,

:Pattern:   DNNNNN
:Tag count: 236

::

        aacaaca aacacac gaaggcc tggtggc tggccac aatgtcc atctctc gaggctt
        ttatgtg aattaac gaagtag aacaggt atctgca tggcgca agatcta gataggc
        aacattg ggtctgg aaccaag taagtct gaatatc ggtgaga aaccgcc gcctcct
        agtgcaa tggcttg tggtaag ttcactt acggcga acaacaa aacctga taatcat
        agtcgtc gcctgta acggtac gaatggt aacgagc acgcggc tggtcct tatcagc
        tgacatc gccgtgc gtgacgt agcagag aacgccg agaaccg gcgaacg acgtacc
        atgatca gtgagcc aacggaa gatctac gcgacac acaatgg acacaac atgcaga
        ttccgct tgtaaca gatgacg accaatc agccata ggttcac tgtacag aactatt
        ttcctgg acaccgt tctgagg gcgatga ggaggaa tatctca gtgcctc gccggcg
        ttcgagt acacgta actaagt tgtaggt ttcgcca gcgcatt ttcaacg gcgccgg
        ggttatt tgtattc acagaca gcgcgaa ttcggtc atggcag aagacct ttaggat
        gtggact taccgtg tatgttg gtaatta tgtccga ttctaac acagctc gattcta
        ttaccta gagctgt acaggag ggatgcg gtcttcg agcgtgg aagaagg agctacg
        tgtctat atacgcg ggattga tattgtc tgtgaac ggcaagg aagccaa gtgtatg
        agctcgt tcaacct acatatg ggcacca atacttc actctaa atgtggt ttgaagc
        agcttaa aagagta tgtgctt atagcct aagctcg gcacaga ggagctg gtgttat
        tgcagcc acattat aaggaat tactcga ttgagag atagtaa taatacg attagaa
        tagcgat gcctaag actggct gttaccg tcgagtc tcgtgcg gacgtca tacttag
        tggcagt gcactcc gatggat gctaata tgttgaa aggatgt gtatcca tagaatt
        ggccttc ggcgacc ttaacac gctagag attccac aagtcgc tctacgc accatct
        accgcat aagtgag ttaagca ttgctcc tagatac gagcaca taaggta gcaggtt
        tgcgcgc tctatcg atcacgg ttaatgt ttggata ttacaag accgtta aatacga
        ggaccgc agaatac acctaga gtcagga aatagcg acttcag gcggttg gttgatc
        tctcgac aatatat ttacggc agacagg ggctgat ggtcgct ttcataa aagcatc
        ggaagtc gtccagc gttggca attgtgt gtccgag agacgat gaacaat atcctat
        tcattca ggaacat ttgtcaa gctgcgt aatcctg agtaatg agactca ataagtt
        ttagcgg aatcact atcgatg acaagcc taggtga acgactg agaagga acgagat
        tcctggt agagatt gtcgcac tggacta tccgctg ggtataa gcttagc aatgata
        ttataga tcttact tagtctg taattgc gagttcc attaacc aggcctt tgtggcg
        gaagcga acctgac ttagacc gtatgac

Tag size: 8
,,,,,,,,,,,

:Pattern:   DNNNNN
:Tag count: 10

::

       
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

