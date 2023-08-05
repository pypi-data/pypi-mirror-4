# cython: profile=True
"""
fasta module provides functions to read and write sequences in fasta format.


"""
from _fasta cimport *

from obitools._obitools cimport  _bioSeqGenerator,BioSequence,AASequence,NucSequence
from obitools._obitools cimport  __default_raw_parser

from obitools.format.genericparser import genericEntryIteratorGenerator

#from obitools.alignment import alignmentReader
#from obitools.utils import universalOpen

import re
from obitools.ecopcr.options import loadTaxonomyDatabase
from obitools.format import SequenceFileIterator

#from _fasta import parseFastaDescription,fastaParser
#from _fasta import _fastaJoinSeq
#from _fasta import _parseFastaTag


cdef extern from "regex.h":
    struct regex_t:
        pass
    
    struct regmatch_t:
        int rm_so         # start of match
        int rm_eo         # end of match
    
    enum REG_EXTENDED:
        pass
    
    
    
    int regcomp(regex_t *preg, char *pattern, int cflags)
    int regexec(regex_t *preg, char *string, int nmatch, regmatch_t *pmatch, int eflags)
    void regfree(regex_t *preg)
    
#fastaEntryIterator=fastGenericEntryIteratorGenerator(startEntry='>')
fastaEntryIterator=genericEntryIteratorGenerator(startEntry='>')
rawFastaEntryIterator=genericEntryIteratorGenerator(startEntry='\s*>')

cdef bytes _fastaJoinSeq(list seqarray):
    return  b''.join([x.strip() for x in seqarray])


cpdef tuple parseFastaDescription(bytes ds, object tagparser):

    cdef bytes  definition
    cdef bytes  info
    cdef object m
        
    ds = b' '+ds
    m = tagparser.search(ds)
    
    if m is not None:
        info=m.group(0)
        definition = ds[m.end(0):].rstrip()
    else:
        info=None
        definition=ds
 
    return definition,info

cdef bytes  _fastTagParser=b'^[a-zA-Z][a-zA-Z0-9_]* *= *[^;]*;( +[a-zA-Z][a-zA-Z0-9_]* *= *[^;]*;)*'
cdef object _cfastTagParser=re.compile(_fastTagParser)

#cdef regex_t cfastTagParser
#cdef int     regerror=regcomp(&cfastTagParser, fastTagParser, REG_EXTENDED)

cpdef tuple fastParseFastaDescription(bytes ds):

    cdef bytes  definition
    cdef bytes  info
    cdef object m
        
    m = _cfastTagParser.search(ds)
    
    if m is not None:
        info=m.group(0)
        definition = ds[m.end(0):].rstrip()
    else:
        info=None
        definition=ds
 
    return definition,info



cpdef object fastFastaParser(bytes  seq,
                             object tagparser,
                             bytes  rawparser):
    '''
    Parse a fasta record.
    
    @attention: internal purpose function
    
    @param seq: a sequence object containing all lines corresponding
                to one fasta sequence
    @type seq: C{list} or C{tuple} of C{str}
    
    @param bioseqfactory: a callable object return a BioSequence
                          instance.
    @type bioseqfactory: a callable object
    
    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: a C{BioSequence} instance   
    '''
    cdef list  lseq  = seq.split(b'\n')    
    cdef list  title = lseq.pop(0).split(None,1)    
    cdef bytes id    = title[0][1:]
    cdef bytes defintion,info
    
    if len(title) == 2:
        definition,info=fastParseFastaDescription(title[1])
    else:
        info= None
        definition=None

    seq=b''.join([x.rstrip() for x in lseq])
        
    return _bioSeqGenerator(id, seq, definition,info,rawparser,{})


cpdef object fastaParser(bytes  seq,
                         object bioseqfactory,
                         object tagparser,
                         bytes  rawparser,
                         object joinseq=None):
    '''
    Parse a fasta record.
    
    @attention: internal purpose function
    
    @param seq: a sequence object containing all lines corresponding
                to one fasta sequence
    @type seq: C{list} or C{tuple} of C{str}
    
    @param bioseqfactory: a callable object return a BioSequence
                          instance.
    @type bioseqfactory: a callable object
    
    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: a C{BioSequence} instance   
    '''
    cdef list  lseq  = seq.split(b'\n')    
    cdef list  title = lseq.pop(0).split(None,1)    
    cdef bytes id    = title[0][1:]
    cdef bytes defintion,info
    
    if len(title) == 2:
        definition,info=parseFastaDescription(title[1], tagparser)
    else:
        info= None
        definition=None

    if joinseq is None:
        seq=_fastaJoinSeq(lseq)
    else:
        seq=joinseq(lseq)
        
    if bioseqfactory is None:
        return _bioSeqGenerator(id, seq, definition,info,rawparser,{})
    else:
        return bioseqfactory(id, seq, definition,info,rawparser)
    
def fastaNucParser(seq,tagparser=__default_raw_parser,joinseq=None):
    return fastaParser(seq,NucSequence,tagparser=tagparser,joinseq=joinseq)

def fastaAAParser(seq,tagparser=__default_raw_parser,joinseq=None):
    return fastaParser(seq,AASequence,tagparser=tagparser,joinseq=joinseq)

def fastFastaIterator(object file,bytes tagparser=__default_raw_parser):
    '''
    iterate through a fasta file sequence by sequence.
    Returned sequences by this iterator will be BioSequence
    instances

    @param file: a line iterator containing fasta data or a filename
    @type file:  an iterable object or str
    @type bioseqfactory: a callable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{BioSequence} instance
 
    @see: L{fastaNucIterator}
    @see: L{fastaAAIterator}
    
    >>> from obitools.format.sequence.fasta import fastFastaIterator
    >>> f = fastFastaIterator('monfichier')
    >>> s = f.next()
    >>> print s
    gctagctagcatgctagcatgcta
    >>>
    '''
    cdef bytes allparser = tagparser % b'[a-zA-Z][a-zA-Z0-9_]*'
    
    rtagparser = re.compile('( *%s)+' % allparser)

    for entry in fastaEntryIterator(file):
        yield fastFastaParser(entry,rtagparser,tagparser)

def fastaIterator(object file,
                  object bioseqfactory=None,
                  bytes tagparser=__default_raw_parser,
                  object joinseq=None):
    '''
    iterate through a fasta file sequence by sequence.
    Returned sequences by this iterator will be BioSequence
    instances

    @param file: a line iterator containing fasta data or a filename
    @type file:  an iterable object or str
    @param bioseqfactory: a callable object return a BioSequence
                          instance.
    @type bioseqfactory: a callable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{BioSequence} instance
 
    @see: L{fastaNucIterator}
    @see: L{fastaAAIterator}
    
    >>> from obitools.format.sequence.fasta import fastaIterator
    >>> f = fastaIterator('monfichier')
    >>> s = f.next()
    >>> print s
    gctagctagcatgctagcatgcta
    >>>
    '''
    cdef bytes allparser = tagparser % b'[a-zA-Z][a-zA-Z0-9_]*'
    
    rtagparser = re.compile('( *%s)+' % allparser)

    for entry in fastaEntryIterator(file):
        yield fastaParser(entry,bioseqfactory,rtagparser,tagparser,joinseq)
        
def rawFastaIterator(file,bioseqfactory=None,
                     tagparser=__default_raw_parser,
                     joinseq=None):

    rawparser=tagparser
    allparser = tagparser % '[a-zA-Z][a-zA-Z0-9_]*'
    tagparser = re.compile('( *%s)+' % allparser)

    for entry in rawFastaEntryIterator(file):
        entry=entry.strip()
        yield fastaParser(entry,bioseqfactory,tagparser,rawparser,joinseq)

def fastaNucIterator(file,tagparser=__default_raw_parser):
    '''
    iterate through a fasta file sequence by sequence.
    Returned sequences by this iterator will be NucSequence
    instances
    
    @param file: a line iterator containint fasta data
    @type file: an iterable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{NucBioSequence} instance
    @rtype: a generator object
    
    @see: L{fastaIterator}
    @see: L{fastaAAIterator}
    '''
    return fastaIterator(file, NucSequence,tagparser)

def fastaAAIterator(file,tagparser=__default_raw_parser):
    '''
    iterate through a fasta file sequence by sequence.
    Returned sequences by this iterator will be AASequence
    instances
    
    @param file: a line iterator containing fasta data
    @type file: an iterable object
    
    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{AABioSequence} instance

    @see: L{fastaIterator}
    @see: L{fastaNucIterator}
    '''
    return fastaIterator(file, AASequence,tagparser)

def formatFasta(data,gbmode=False,upper=False,restrict=None):
    '''
    Convert a seqence or a set of sequences in a
    string following the fasta format
    
    @param data: sequence or a set of sequences
    @type data: BioSequence instance or an iterable object 
                on BioSequence instances
                
    @param gbmode: if set to C{True} identifier part of the title
                   line follows recommendation from nbci to allow
                   sequence indexing with the blast formatdb command.
    @type gbmode: bool
                
    @param restrict: a set of key name that will be print in the formated
                     output. If restrict is set to C{None} (default) then
                     all keys are formated.
    @type restrict: any iterable value or None
    
    @return: a fasta formated string
    @rtype: str
    '''
    if isinstance(data, BioSequence):
        data = [data]

    if restrict is not None and not isinstance(restrict, set):
        restrict = set(restrict)    

    rep = []
    for sequence in data:
        seq = str(sequence)
        if sequence.definition is None:
            definition=''
        else:
            definition=sequence.definition
        if upper:
            frgseq = '\n'.join([seq[x:x+60].upper() for x in xrange(0,len(seq),60)])
        else:
            frgseq = '\n'.join([seq[x:x+60] for x in xrange(0,len(seq),60)])
        info='; '.join(['%s=%s' % x 
                        for x in sequence.rawiteritems()
                        if restrict is None or x[0] in restrict])
        if info:
            info=info+';'
        if sequence._rawinfo is not None and sequence._rawinfo:
            info+=" " + sequence._rawinfo.strip()
            
        id = sequence.id
        if gbmode:
            if 'gi' in sequence:
                id = "gi|%s|%s" % (sequence['gi'],id)
            else:
                id = "lcl|%s|" % (id)
        title='>%s %s %s' %(id,info,definition)
        rep.append("%s\n%s" % (title,frgseq))
    return '\n'.join(rep)

def formatSAPFastaGenerator(options):
    loadTaxonomyDatabase(options)
    
    taxonomy=None
    if options.taxonomy is not None:
        taxonomy=options.taxonomy
    
    assert taxonomy is not None,"SAP formating require indication of a taxonomy database"

    ranks = ('superkingdom', 'kingdom', 'subkingdom', 'superphylum', 
             'phylum', 'subphylum', 'superclass', 'class', 'subclass', 
             'infraclass', 'superorder', 'order', 'suborder', 'infraorder', 
             'parvorder', 'superfamily', 'family', 'subfamily', 'supertribe', 'tribe', 
             'subtribe', 'supergenus', 'genus', 'subgenus', 'species group', 
             'species subgroup', 'species', 'subspecies')
    
    trank=set(taxonomy._ranks)
    ranks = [taxonomy._ranks.index(x) for x in ranks if x in trank]
    
    strict= options.strictsap
    
    def formatSAPFasta(data,gbmode=False,upper=False,restrict=None):
        '''
        Convert a seqence or a set of sequences in a
        string following the fasta format as recommended for the SAP
        software 
        
        http://ib.berkeley.edu/labs/slatkin/munch/StatisticalAssignmentPackage.html
        
        @param data: sequence or a set of sequences
        @type data: BioSequence instance or an iterable object 
                    on BioSequence instances
                    
        @param gbmode: if set to C{True} identifier part of the title
                       line follows recommendation from nbci to allow
                       sequence indexing with the blast formatdb command.
        @type gbmode: bool
                    
        @param restrict: a set of key name that will be print in the formated
                         output. If restrict is set to C{None} (default) then
                         all keys are formated.
        @type restrict: any iterable value or None
        
        @return: a fasta formated string
        @rtype: str
        '''
        if isinstance(data, BioSequence):
            data = [data]
    
        if restrict is not None and not isinstance(restrict, set):
            restrict = set(restrict)    
    
        rep = []
        for sequence in data:
            seq = str(sequence)

            if upper:
                frgseq = '\n'.join([seq[x:x+60].upper() for x in xrange(0,len(seq),60)])
            else:
                frgseq = '\n'.join([seq[x:x+60] for x in xrange(0,len(seq),60)])
                        
            try:    
                taxid = sequence["taxid"]
            except KeyError:
                if strict:
                    raise AssertionError('All sequence must have a taxid')
                else:
                    continue
                
            definition=' ;'
            
            for r in ranks:
                taxon = taxonomy.getTaxonAtRank(taxid,r)
                if taxon is not None:
                    definition+=' %s: %s,' % (taxonomy._ranks[r],taxonomy.getPreferedName(taxon))
                    
            definition='%s ; %s' % (definition[0:-1],taxonomy.getPreferedName(taxid))
            
            id = sequence.id
            if gbmode:
                if 'gi' in sequence:
                    id = "gi|%s|%s" % (sequence['gi'],id)
                else:
                    id = "lcl|%s|" % (id)
            title='>%s%s' %(id,definition)
            rep.append("%s\n%s" % (title,frgseq))
        return '\n'.join(rep)

    return formatSAPFasta

#class FastaIterator(SequenceFileIterator):
#    
#    
#    entryIterator = genericEntryIteratorGenerator(startEntry='>')
#    classmethod(entryIterator)
#    
#    def __init__(self,inputfile,bioseqfactory=bioSeqGenerator,
#                      tagparser=_default_raw_parser,
#                      joinseq=_fastaJoinSeq):
#        
#        SequenceFileIterator.__init__(self, inputfile, bioseqfactory)
#
#        self.__file = FastaIterator.entryIterator(self._inputfile)
#        
#        self._tagparser = tagparser
#        self._joinseq   = joinseq
#
#    def get_tagparser(self):
#        return self.__tagparser
#
#
#    def set_tagparser(self, value):
#        self._rawparser = value
#        allparser = value % '[a-zA-Z][a-zA-Z0-9_]*'
#        self.__tagparser = re.compile('( *%s)+' % allparser)
#
#    def _parseFastaDescription(self,ds):
#        
#        m = self._tagparser.search(' '+ds)
#        if m is not None:
#            info=m.group(0)
#            definition = ds[m.end(0):].strip()
#        else:
#            info=None
#            definition=ds
#     
#        return definition,info
#
#
#    def _parser(self):
#        '''
#        Parse a fasta record.
#        
#        @attention: internal purpose function
#                
#        @return: a C{BioSequence} instance   
#        '''
#        seq = self._seq.split('\n')
#        title = seq[0].strip()[1:].split(None,1)
#        id=title[0]
#        if len(title) == 2:
#            definition,info=self._parseFastaDescription(title[1])
#        else:
#            info= None
#            definition=None
#    
#        seq=self._joinseq(seq[1:])
#        
#        return self._bioseqfactory(id, seq, definition,info,self._rawparser)
#    
#    _tagparser = property(get_tagparser, set_tagparser, None, "_tagparser's docstring")
