from obitools import NucSequence
from obitools.ecopcr import EcoPCRDBFile
from obitools.ecopcr.taxonomy import EcoTaxonomyDB, ecoTaxonomyWriter
from obitools.ecopcr.annotation import EcoPCRDBAnnotationWriter
from obitools.utils import universalOpen
from glob import glob
import struct
import gzip
import sys


class EcoPCRDBSequenceIterator(EcoPCRDBFile):
    '''
    Build an iterator over the sequences include in a sequence database
    formated for ecoPCR
    '''

    def __init__(self,path,taxonomy=None):
        '''
        ecoPCR data iterator constructor
        
        @param path: path to the ecoPCR database including the database prefix name
        @type path: C{str}
        @param taxonomy: a taxonomy can be given to the reader to decode the taxonomic data
                         associated to the sequences. If no Taxonomy is furnish, it will be read 
                         before the sequence database files using the same path.
        @type taxonomy: L{obitools.ecopcr.taxonomy.Taxonomy}
        '''
        self._path = path
        
        if taxonomy is not None:
            self._taxonomy=taxonomy
        else:
            self._taxonomy=EcoTaxonomyDB(path)
            
        self._seqfilesFiles =  glob('%s_???.sdx' % self._path)
        self._seqfilesFiles.sort()

    def __ecoSequenceIterator(self,file):
        for record in self._ecoRecordIterator(file):
            lrecord = len(record)
            lnames  = lrecord - (4*4+20)
            (taxid,seqid,deflength,seqlength,cptseqlength,string)=struct.unpack('> I 20s I I I %ds' % lnames, record)
            seqid=seqid.strip('\x00')
            de = string[:deflength]
            seq = gzip.zlib.decompress(string[deflength:])
            bioseq = NucSequence(seqid,seq,de,taxidx=taxid,taxid=self._taxonomy._taxonomy[taxid][0])
            yield  bioseq
        
    def __iter__(self):
        for seqfile in self._seqfilesFiles:
            for seq in self.__ecoSequenceIterator(seqfile):
                yield seq
                
class EcoPCRDBSequenceWriter(object):
    
    def __init__(self,dbname,fileidx=1,taxonomy=None,ftid=None,type=None,definition=None,append=False):
        self._taxonomy=taxonomy
        self._filename="%s_%03d.sdx" % (dbname,fileidx)
        if append:
            mode ='r+b'
            f = universalOpen(self._filename)
            (recordCount,) = struct.unpack('> I',f.read(4))
            self._sequenceCount=recordCount
            del f
            self._file = open(self._filename,mode)
            self._file.seek(0,0)
            self._file.write(struct.pack('> I',0))
            self._file.seek(0,2)
        else:
            self._sequenceCount=0
            mode = 'wb'
            self._file = open(self._filename,mode)
            self._file.write(struct.pack('> I',self._sequenceCount))
        
        if self._taxonomy is not None:
            print >> sys.stderr,"Writing the taxonomy file...",
            ecoTaxonomyWriter(dbname,self._taxonomy)
            print >> sys.stderr,"Ok"
        
        if type is not None:
            assert ftid is not None,"You must specify an id attribute for features"
            self._annotation = EcoPCRDBAnnotationWriter(dbname, ftid, fileidx, type, definition)
        else: 
            self._annotation = None
        
    def _ecoSeqPacker(self,seq):
    
        compactseq = gzip.zlib.compress(str(seq).upper(),9)
        cptseqlength  = len(compactseq)
        delength   = len(seq.definition)
        
        totalSize = 4 + 20 + 4 + 4 + 4 + cptseqlength + delength
        
        if self._taxonomy is None or 'taxid' not in seq:
            taxon=-1
        else:
            taxon=self._taxonomy.findIndex(seq['taxid'])
        
        try:
            packed = struct.pack('> I i 20s I I I %ds %ds' % (delength,cptseqlength),
                                 totalSize,
                                 taxon,
                                 seq.id,
                                 delength,
                                 len(seq),
                                 cptseqlength,
                                 seq.definition,
                                 compactseq)
        except struct.error as e:
            print >>sys.stderr,"\n\n============\n\nError on sequence : %s\n\n" % seq.id
            raise e
        
        assert len(packed) == totalSize+4, "error in sequence packing"
    
        return packed

        
    def put(self,sequence):
        if self._taxonomy is not None:
            if 'taxid' not in sequence and hasattr(sequence, 'extractTaxon'):
                sequence.extractTaxon()
        self._file.write(self._ecoSeqPacker(sequence))
        if self._annotation is not None:
            self._annotation.put(sequence, self._sequenceCount)
        self._sequenceCount+=1
        
    def __del__(self):
        self._file.seek(0,0)
        self._file.write(struct.pack('> I',self._sequenceCount))
        self._file.close()
        
    
