#!/usr/local/bin/python
'''
:py:mod:`ngsfilter` : Assigning reads to their experiments based on DNA tags and primers
========================================================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

A DNA metabarcoding experiment can be considered as a set a PCR products mixed together and sequenced using a next generation sequencer ({i.e.} a solexa or a 454).
To distinguish between this different PCR products, pairs of small DNA sequences (call tags, see the :py:mod:`oligoTag` command and its associated paper for more 
informations on the design of such tags) unique for each PCR products are concatenated to the PCR primers.
As they are amplified during the PCR, these tags should be recognizable, together with their respective primers, at the beginning and the end of the reads. 
The first step in data analysis is thus to demultiplex the large resulting sequence file by identifying these DNA tags and the primers.

Usually the results of sequencing are stored in one or more files formatted according to the fasta or fastq format. :py:mod:`ngsfilter` take as input such sequence file and an extra file describing the DNA tags and primers sequences used for each sample.

The results consist of sequences trimmed of the primers and tags and annotated with the corresponding sample (and possibly some extra informations). 
Sequences for which the tags and primers have not been well identified, and which are thus unassigned to any sample, are tagged as erroneous sequences 
by :py:mod:`ngsfilter`. Such erroneous sequences are not reported by the program unless specified by the appropriate option.



Input files format
------------------

Sequences data files
^^^^^^^^^^^^^^^^^^^^

Data returned by next generation sequencers follow mainly two formats. 
Solexa systems return their data as a `FASTQ <http://en.wikipedia.org/wiki/FASTQ_format>`_ formatted file including sequence data themselves and the associated quality data computed by the sequencer. 

.. code-block:: bash

   @HELIUM_000100422_612GNAAXX:1:1:1176:13188#0/1
   TACCCCACTATGCTTAGCCCTAAACCTAGATCGTTAGCTCAAACAAAACTATCCGCCAGAGAACTACTAGCAACAGCTTACAACTCAAAGGACTTGGCGGTGCTTTAC
   +HELIUM_000100422_612GNAAXX:1:1:1176:13188#0/1
   a^aa^`````^[R^`_aaaaa[aaaa`a`a]KMZ]`^\a`aX`aaPRVV]``P``XXLXLNHNNO`Y``O^^[^BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
   @HELIUM_000100422_612GNAAXX:1:1:1176:9252#0/1
   CCATGATCATTAGATACCCCACTATGCTTAGCCCTAAACACAAATAATTACAAAAACAAAATTATTCGCTAGAGTACTACCGACACCAGTCCGAAACACAAAGACCTG
   +HELIUM_000100422_612GNAAXX:1:1:1176:9252#0/1
   WXXXVX^Z[`aaaaaaaaaaaaaaaaaaaaaaaaaaaaaY^^^^[aaaaa`aaaaYZZZZZZG^aBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
   @HELIUM_000100422_612GNAAXX:1:1:1176:1609#0/1
   CCGATTCTATAGAACAGGCTCCTCTAGAGGGGTGTAAAGCACCGCCAAGTCCTTTGAGTTTTAAGCTGTTGCTAGTAGTTCTCTGGCGGATAGTTTTGTTTGAGCTCA
   +HELIUM_000100422_612GNAAXX:1:1:1176:1609#0/1
   ^^`]\`bbbbbbbbbbbbbbbbbbbbbabbbbcbbbbbbbbbbbbbbbbbbbbbbbabbbbb`babbbbaabb`bbb^[Ya]Y]]bbbXSbaa^b__\bBBBBBBBBB


The 454/Roche system provides the same data in two files. A file named with the extention '.fna' containing the sequence in 
`FASTA <http://en.wikipedia.org/wiki/FASTA_format>`_ format and a second file named with the extension '.qual' containing the quality score. 

Example of sequences from a 454/Roche output in fasta:

.. code-block:: bash

   >000140_3268_4049 length=85 uaccno=FIBZJ9Q02H89WJ
   CCGGAAGGGCAATCCTGAGCCAACTCCGTGGAGTACGGTCGCGACCGAGAACGCGATGAT
   AGGTGCAGAGACTCAATGGTTCCGG
   >000149_2785_1081 length=60 uaccno=FIBZJ9Q02G2S3F
   GAACTGGGCAATCCTGAGCCAAATTCTACCTAGGANAGGTGCAGAGACTCAATGGTAGTT
   >000191_2786_0335 length=65 uaccno=FIBZJ9Q02G2VOH
   CGAATCGAGCAATCCTGAGCCAAGTCCAAACCATCGGGATAGGTGCAGAGACTCAATGGG
   ATTCG

Example of quality indices for the 3 sequences above:

.. code-block:: bash

   >000140_3268_4049 length=85 uaccno=FIBZJ9Q02H89WJ
   35 35 35 35 37 37 32 32 32 37 37 37 37 37 37 37 37 37 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 40 38 38 38 39 40 40 40 40 40 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37 
   37 37 37 37 37 37 37 37 37 37 37 37 37 37 36 36 36 37 37 37 37 37 37 37 37 
   >000149_2785_1081 length=60 uaccno=FIBZJ9Q02G2S3F
   37 37 36 33 30 30 30 36 37 37 37 37 37 37 37 37 37 37 38 38 33 33 33 37 37 39 37 37 37 37 37 37 37 38 38 0  38 38 40 40 40 40 40 40 40 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37 
   >000191_2786_0335 length=65 uaccno=FIBZJ9Q02G2VOH
   35 35 35 35 35 35 35 35 35 35 35 35 35 35 35 35 35 35 37 35 35 35 35 32 32 33 33 25 21 21 31 31 35 35 35 35 33 33 33 32 32 35 35 35 35 35 35 35 35 35 35 35 35 34 33 33 33 34 34 34 
   35 25 25 26 34 


:py:mod:`ngsfilter` can process both the fasta or the fastq format. If fasta format is used, it can optionally use the '.qual' file to take quality into account. 
According if the input data contain quality or not, the output of :py:mod:`ngsfilter` will be formatted by default in fastq or fasta format respectively.


Sample description data files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Samples are assigned based on their DNA tag and primer sequences. :py:mod:`ngsfilter` needs a description of the primers and tags associated to each sample. 
This is done by mean of the sample description data file. The sample description file is a text file where each line describes one sample. 
Column are separated by space or tab characters



Commentaries can also be inserted in the sample description file. Lines beginning with the '#' character will be considered as commentary lines 
and will simply be ignored by :py:mod:`ngsfilter`.

.. code-block:: bash

    tab=ColumnFile(filename,strip=True,
                            types=(str,str,tagpair,lower,lower,bool),
                            head=('experiment','sample',
                                  'tags',
                                  'forward_primer','reverse_primer',
                                  'partial'),
                            skip="#",
                            extra="@")
    

.. code-block:: bash

    gh     01_11a     cacgcagtc    GGGCAATCCTGAGCCAA    CCATTGAGTCTCTGCACCTATC    F @ community=Festuca;   locality=1;  bucket=1; extraction=1; pcr=1; 
    gh     01_12a     cacgcatcg    GGGCAATCCTGAGCCAA    CCATTGAGTCTCTGCACCTATC    F @ community=Festuca;   locality=1;  bucket=1; extraction=2; pcr=1; 
    gh     01_21a     cacgcgcat    GGGCAATCCTGAGCCAA    CCATTGAGTCTCTGCACCTATC    F @ community=Festuca;   locality=1;  bucket=2; extraction=1; pcr=1; 
    gh     01_22a     cacgctact    GGGCAATCCTGAGCCAA    CCATTGAGTCTCTGCACCTATC    F @ community=Festuca;   locality=1;  bucket=2; extraction=2; pcr=1; 
    gh     02_11a     cacgctgag    GGGCAATCCTGAGCCAA    CCATTGAGTCTCTGCACCTATC    F @ community=Festuca;   locality=2;  bucket=1; extraction=1; pcr=1;
    gh     02_12a     cacgtacga    GGGCAATCCTGAGCCAA    CCATTGAGTCTCTGCACCTATC    F @ community=Festuca;   locality=2;  bucket=1; extraction=2; pcr=1;
'''
from obitools import NucSequence, DNAComplementSequence
from string import lower

import sys
  
import math

from obitools.options import getOptionManager
from obitools.utils import ColumnFile
from obitools.align import FreeEndGapFullMatch
from obitools.format.options import addInOutputOption, sequenceWriterGenerator



def addNGSOptions(optionManager):
    

    optionManager.add_option('-t','--tag-list',
                             action="store", dest="taglist",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file containing tag used")
    
    optionManager.add_option('-u','--unidentified',
                             action="store", dest="unidentified",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file used to store unidentified sequences")
    
    optionManager.add_option('-e','--error',
                             action="store", dest="error",
                             metavar="###",
                             type="int",
                             default=2,
                             help="matching error per primer")
    

class Primer:
    
    collection={}
    
    def __init__(self,sequence,taglength,direct=True,error=2,verbose=False):
        '''
            
        @param sequence:
        @type sequence:
        @param direct:
        @type direct:
        '''
        
        assert sequence not in Primer.collection        \
            or Primer.collection[sequence]==taglength,  \
            "Primer %s must always be used with tags of the same length" % sequence
            
        Primer.collection[sequence]=taglength
        
        self.raw=sequence
        self.sequence = NucSequence('primer',sequence)
        self.lseq = len(self.sequence)
        self.align=FreeEndGapFullMatch()
        self.align.match=4
        self.align.mismatch=-2
        self.align.opengap=-2
        self.align.extgap=-2
        self.error=error
        self.minscore = (self.lseq-error) * self.align.match + error * self.align.mismatch
        if verbose:
            print >>sys.stderr,sequence,":",self.lseq,"*",self.align.match,"+",error,"*",self.align.mismatch,"=",self.minscore
        self.taglength=taglength
        
        self.align.seqB=self.sequence
        
        self.direct = direct
        self.verbose=verbose
        
    def complement(self):
        p = Primer(self.raw,
                  self.taglength,
                  not self.direct,verbose=self.verbose,
                  error=self.error)
        p.sequence=p.sequence.complement()
        p.align.seqB=p.sequence
        return p
    
    def __hash__(self):
        return hash(str(self.raw))
    
    def __eq__(self,primer):
        return self.raw==primer.raw 
    
    def __call__(self,sequence):
        if len(sequence) <= self.lseq:
            return None
        if self.verbose:
            print >>sys.stderr,len(sequence) , self.lseq,len(sequence) < self.lseq
        self.align.seqA=sequence
        ali=self.align()
        if self.verbose:
            print >>sys.stderr,ali
            print >>sys.stderr,"Score : %d  Minscore : %d \n" %(ali.score,self.minscore)
            
        if ali.score >= self.minscore:
            score = ali.score
            start = ali[1].gaps[0][1]
            end = len(ali[1])-ali[1].gaps[-1][1]
            if self.taglength is not None:
                if isinstance(self.sequence, DNAComplementSequence):
                    if (len(sequence)-end) >= self.taglength:
                        tag=str(sequence[end:end+self.taglength].complement())
                    else:
                        tag=None
                else:
                    if start >= self.taglength:                
                        tag=str(sequence[start - self.taglength:start])
                    else:
                        tag=None
            else:
                tag=None
                
            return score,start,end,tag

        return None 
    
    def __str__(self):
        return "%s: %s" % ({True:'D',False:'R'}[self.direct],self.raw)
    
    __repr__=__str__
        
    
def tagpair(x):
    x=tuple(lower(y.strip()) for y in x.split(':'))
    if len(x)==1:
        x = (x[0],x[0])
    return x

def readTagfile(filename):
    """
    data file describing tags and primers for each sample
    is a space separated tabular file following this format
    
    experiment sample forward_tag reverse_tag forward_primer reverse_primer partial
    
    
    tags can be specified as - if no tag are used
    """

    tab=ColumnFile(filename,strip=True,
                            types=(str,str,tagpair,lower,lower,bool),
                            head=('experiment','sample',
                                  'tags',
                                  'forward_primer','reverse_primer',
                                  'partial'),
                            skip="#",
                            extra="@")
    
    primers = {}

    for p in tab:
        forward=Primer(p['forward_primer'],
                       len(p['tags'][0]) if p['tags'][0]!='-' else None,
                       True,
                       error=options.error,verbose=options.debug)
        
        fp = primers.get(forward,{})
        primers[forward]=fp
        
        reverse=Primer(p['reverse_primer'],
                       len(p['tags'][1]) if p['tags'][1]!='-' else None,
                       False,
                       error=options.error,verbose=options.debug)
        
        rp = primers.get(reverse,{})
        primers[reverse]=rp
        
        cf=forward.complement()
        cr=reverse.complement()
        
        dpp=fp.get(cr,{})
        fp[cr]=dpp
        
        rpp=rp.get(cf,{})
        rp[cf]=rpp
            
        tags = (p['tags'][0] if p['tags'][0]!='-' else None,
                p['tags'][1] if p['tags'][1]!='-' else None)
        
        assert tags not in dpp, \
               "tag pair %s is already used with primer pairs : (%s,%s)" % (str(tags),forward,reverse)
               
        extras = p.get('__extra__',{})
        data   ={'experiment':p['experiment'],
                   'sample':    p['sample']
                }
        data.update(extras)
        
        dpp[tags]=data
        rpp[tags]=data
        
                
        if p['partial']:
            dpartial = fp.get(None,{})
            fp[None]=dpartial
            rpartial = rp.get(None,{})
            rp[None]=rpartial
            
            dt = [x for x in dpartial if x[0]==tags[0]]
            rt = [x for x in rpartial if x[1]==tags[1]]
            
            assert not(dt) and not(rt), \
                "partial fragment are not usable with primer pair : (%s,%s)" % (forward,reverse)
                
            dpartial[tags]=data
            rpartial[tags]=data

    return primers
            

def annotate(sequence,options):
        
    def sortMatch(m1,m2):
        if m1[1] is None and m2[1] is None:
            return 0
        
        if m1[1] is None:
            return 1
        
        if m2[1] is None:
            return -1
        
        return cmp(m1[1][1],m2[1][2])
    
    if hasattr(sequence, "quality"):
        q = -reduce(lambda x,y:x+y,(math.log10(z) for z in sequence.quality),0)/len(sequence.quality)*10
        sequence['avg_quality']=q
        q = -reduce(lambda x,y:x+y,(math.log10(z) for z in sequence.quality[0:10]),0)
        sequence['head_quality']=q
        if len(sequence.quality[10:-10]) :
            q = -reduce(lambda x,y:x+y,(math.log10(z) for z in sequence.quality[10:-10]),0)/len(sequence.quality[10:-10])*10
            sequence['mid_quality']=q
        q = -reduce(lambda x,y:x+y,(math.log10(z) for z in sequence.quality[-10:]),0)
        sequence['tail_quality']=q
        
    primers = options.primers
    if options.debug:
        print >>sys.stderr,"directmatch"
    directmatch = [(p,p(sequence)) for p in primers]
    
    
    directmatch.sort(cmp=sortMatch)
    directmatch=directmatch[0] if directmatch[0][1] is not None else None
    
    if options.debug:
        print  >>sys.stderr,">>>>",directmatch
    if directmatch is None:
        sequence['error']='No primer match'
        return False,sequence
    
    match=str(sequence[directmatch[1][1]:directmatch[1][2]])
    
    sequence['originalLength']=len(sequence)
    
    sequence = sequence[directmatch[1][2]:]
    
    if directmatch[0].direct:
        sequence['direction']='forward'
        sequence['forward_score']=directmatch[1][0]
        sequence['forward_primer']=directmatch[0].raw
        sequence['forward_match']=match
        
    else:
        sequence['direction']='reverse'
        sequence['reverse_score']=directmatch[1][0]
        sequence['reverse_primer']=directmatch[0].raw
        sequence['reverse_match']=match
        
    del sequence['cut']
    
    primers = options.primers[directmatch[0]]
    if options.debug:
        print  >>sys.stderr,"reverse match"
    reversematch = [(p,p(sequence)) for p in primers if p is not None]
    reversematch.sort(cmp=sortMatch)
    reversematch = reversematch[0] if reversematch[0][1] is not None else None
    
    if options.debug:
        print  >>sys.stderr,"<<<<",reversematch
    if reversematch is None and None not in primers:
        if directmatch[0].direct:
            message = 'No reverse primer match'
        else:
            message = 'No direct primer match'
                  
        sequence['error']=message
        return False,sequence
    
    if reversematch is None:
        sequence['status']='partial'
        
        if directmatch[0].direct:
            tags=(directmatch[1][3],None)
        else:
            tags=(None,directmatch[1][3])
            
        samples = primers[None]
            
    else:
        sequence['status']='full'
        
        match=str(sequence[reversematch[1][1]:reversematch[1][2]].complement())
        sequence = sequence[0:reversematch[1][1]]
        
        if directmatch[0].direct:
            tags=(directmatch[1][3],reversematch[1][3])
            sequence['reverse_score']=reversematch[1][0]
            sequence['reverse_primer']=reversematch[0].raw
            sequence['reverse_match']=match
            sequence['direct_tag']=tags[0]
            sequence['reverse_tag']=tags[1]
            
        else:
            tags=(reversematch[1][3],directmatch[1][3])
            sequence['forward_score']=reversematch[1][0]
            sequence['forward_primer']=reversematch[0].raw
            sequence['forward_match']=match
        
        del sequence['cut']
        sequence['direct_tag']=tags[0]
        sequence['reverse_tag']=tags[1]

        samples = primers[reversematch[0]]
        
    
    if not directmatch[0].direct:
        sequence=sequence.complement()
        del sequence['complemented']

    sample=None

    if tags[0] is not None:                                     # Direct  tag known
        if tags[1] is not None:                                 # Reverse tag known
            sample = samples.get(tags,None)             
        else:                                                   # Reverse tag known
            s=[samples[x] for x in samples if x[0]==tags[0]]
            if len(s)==1:
                sample=s[0]
            elif len(s)>1:
                sequence['error']='multiple samples match tags'
                return False,sequence
            else:
                sample=None
    else:                                                       # Direct tag unknown
        if tags[1] is not None:                                 # Reverse tag known
            s=[samples[x] for x in samples if x[1]==tags[1]]
            if len(s)==1:
                sample=s[0]
            elif len(s)>1:
                sequence['error']='multiple samples match tags'
                return False,sequence
            else:                                               # Reverse tag known
                sample=None
                
            
    if sample is None:
        sequence['error']="Cannot assign sequence to a sample"
        return False,sequence
    
    sequence._info.update(sample)
    sequence['seqLength']=len(sequence)
    
    return True,sequence


if __name__ == '__main__':
    
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([addNGSOptions,addInOutputOption])
                                    
    
    (options, entries) = optionParser()

#    assert options.direct is not None or options.taglist is not None, \
#         "you must specify option -d ou -t"
         
    assert options.taglist is not None,"you must specify option  -t"

#    if options.taglist is not None:
    primers=readTagfile(options.taglist)
#TODO: Patch when no taglists
#    else:
#        options.direct=options.direct.lower()
#        options.reverse=options.reverse.lower()
#        primers={options.direct:(options.taglength,{})}
#        if options.reverse is not None:
#            reverse = options.reverse
#        else:
#            reverse = '-'
#        primers[options.direct][1][reverse]={'-':('-','-',True,None)}
        
    options.primers=primers
        
    if options.unidentified is not None:
        unidentified = open(options.unidentified,"w")
    
    writer = sequenceWriterGenerator(options)

    if options.unidentified is not None:
        unidentified = sequenceWriterGenerator(options,open(options.unidentified,"w"))
    else :
        unidentified = None
        
    for seq in entries:
        good,seq = annotate(seq,options)
        if good:
            writer(seq)
        elif unidentified is not None:
            unidentified(seq)
            
    
    
