# cython: profile=True


from _obitools cimport *

#from cython.parallel import parallel, prange

from weakref import ref
import re
from itertools import chain
import array


from obitools.utils.iterator import uniqueChain
from obitools.sequenceencoder import DNAComplementEncoder
from obitools.location import Location

__default_raw_parser = b" %s *= *([^;]*);"
_default_raw_parser=__default_raw_parser

cdef class WrapperSetIterator(object):
    def __init__(self,s):
        self._i = set.__iter__(s)
    def next(self):
        return self._i.next()()
    def __iter__(self):
        return self
    
cdef class WrapperSet(set):
    def __iter__(self):
        return WrapperSetIterator(self)


cdef class BioSequence(object):
    '''
    BioSequence class is the base class for biological
    sequence representation.
    
    It provides storage of :
    
        - the sequence itself, 
        - an identifier,
        - a definition an manage 
        - a set of complementary information on a key / value principle.
    
    .. warning:: 
        
            :py:class:`obitools.BioSequence` is an abstract class, this constructor
            can only be called by a subclass constructor.
    '''
        
    def __init__(self,bytes id, bytes seq,
                      bytes definition=None,
                      bytes rawinfo=None,
                      bytes rawparser=__default_raw_parser,**info):
        '''        
        
        :param id: sequence identifier
        :type id:  `str`
 
        :param seq: the sequence
        :type seq:  `str`

        :param definition: sequence definition (optional)
        :type definition: `str`
        
        :param rawinfo: a text containing a set of key=value; patterns
        :type definition: `str`
        
        :param rawparser: a text describing a regular patterns template 
                          used to parse rawinfo
        :type definition: `str`
        
        :param info: extra named parameters can be added to associate complementary
                     data to the sequence
        
        '''
        
        assert type(self)!=BioSequence,"obitools.BioSequence is an abstract class"
        
        self._seq=seq
        self._info = dict(info)
        if rawinfo is not None:
            self.__rawinfo=' ' + rawinfo
        else:
            self.__rawinfo=None
        self._rawparser=rawparser
        self._definition=definition
        self._id=id
        self._hasTaxid=True
        self.__quality=None
        self.word4table=None
        self.word4over=0

    cpdef bytes get_seq(self):
        return self.__seq


    cpdef set_seq(self, object value):
        
        cdef bytes s
        
        if not isinstance(value, bytes):
            s=bytes(value)
        else:
            s=value
        
        self.__seq = s.lower()
        self.__len = len(s)

        
    cpdef object clone(self):
        seq = type(self)(self.id,
                         str(self),
                         definition=self.definition
                         )
        seq._info=dict(self.getTags())
        seq.__rawinfo=self.__rawinfo
        seq._rawparser=self._rawparser
        seq._hasTaxid=self._hasTaxid
        return seq
        
    cpdef bytes getDefinition(self):
        '''
        Sequence definition getter.
        
        :return: the sequence definition
        :rtype: str
            
        '''
        return self._definition

    cpdef setDefinition(self, bytes value):
        '''
        Sequence definition setter.
        
        :param value: the new sequence definition
        :type value: C{str}
        :return: C{None}
        '''
        self._definition = value

    cpdef bytes getId(self):
        '''
        Sequence identifier getter
        
        :return: the sequence identifier
        :rtype: C{str}
        '''
        return self._id

    cpdef setId(self, bytes value):
        '''
        Sequence identifier setter.
        
        :param value: the new sequence identifier
        :type value:  C{str}
        :return: C{None}
        '''
        self._id = value

    cpdef bytes getStr(self):
        '''
        Return the sequence as a string
        
        :return: the string representation of the sequence
        :rtype: str
        '''
        return self._seq
    
    cpdef  getSymbolAt(self, int position):
        '''
        Return the symbole at C{position} in the sequence
        
        :param position: the desired position. Position start from 0
                         if position is < 0 then they are considered
                         to reference the end of the sequence.
        :type position: `int`
        
        :return: a one letter string
        :rtype: `str`
        '''
        return str(self)[position]
    
    cpdef object getSubSeq(self, object location):
        '''
        return a subsequence as described by C{location}.
        
        The C{location} parametter can be a L{obitools.location.Location} instance,
        an interger or a python C{slice} instance. If C{location}
        is an iterger this method is equivalent to L{getSymbolAt}.
        
        :param location: the positions of the subsequence to return
        :type location: C{Location} or C{int} or C{slice}
        :return: the subsequence
        :rtype: a single character as a C{str} is C{location} is an integer,
                a L{obitools.SubSequence} instance otherwise.
        
        '''
        if isinstance(location,Location):
            return location.extractSequence(self)
        elif isinstance(location, int):
            return self.getSymbolAt(location)
        elif isinstance(location, slice):
            return SubSequence(self,location)

        raise TypeError,'key must be a Location, an integer or a slice'  
    
    cpdef object getKey(self, bytes key):
                
        if key not in self._info:
            if self.__rawinfo is None:
                if key==b'count':
                    return 1
                elif key==b'taxid' and self._hasTaxid:
                    self.extractTaxon()
                    return self._info['taxid']
                else:
                    raise KeyError,key
            p = re.compile(self._rawparser % key)
            m = p.search(self.__rawinfo)
            if m is not None:
                v=m.group(1)
                self.__rawinfo=' ' + self.__rawinfo[0:m.start(0)]+self.__rawinfo[m.end(0):]
                try:
                    v = eval(v)
                except:
                    pass
                self._info[key]=v
            else:
                if key=='count':
                    v=1
                else:
                    raise KeyError,key
        else:
            v=self._info[key]
        return v
            
    cpdef extractTaxon(self):
        '''
        Extract Taxonomy information from the sequence header.
        This method by default return None. It should be subclassed
        if necessary as in L{obitools.seqdb.AnnotatedSequence}.
        
        :return: None
        '''
        self._hasTaxid=self.hasKey(b'taxid')
        return None
        
    def __str__(self):
        return self.getStr()
    
    def __getitem__(self,key):
        if isinstance(key, bytes):
            return self.getKey(key)
        else:
            return self.getSubSeq(key)
        
    def __setitem__(self,key,value):
        self.__contains__(key)
        self._info[key]=value
        if key=='taxid':
            self._hasTaxid=value is not None
        
    def __delitem__(self,key):
        if isinstance(key, bytes):
            if key in self:
                del self._info[key]
            else:
                raise KeyError,key    
            
            if key=='taxid':
                self._hasTaxid=False
        else:
            raise TypeError,key
        
    def __iter__(self):
        '''
        Iterate through the sequence symbols
        '''
        return iter(str(self))
    
    def __len__(self):
        return self.__len
    
    cpdef bint hasKey(self,bytes key):
        cdef bint rep
        
        rep = key in self._info
        
        if not rep and self.__rawinfo is not None:
            p = re.compile(self._rawparser % key)
            m = p.search(self.__rawinfo)
            if m is not None:
                v=m.group(1)
                self.__rawinfo=' ' + self.__rawinfo[0:m.start(0)]+self.__rawinfo[m.end(0):]
                try:
                    v = eval(v)
                except:
                    pass
                self._info[key]=v
                rep=True
        
        return rep
    
    def __contains__(self,key):
        '''
        methods allowing to use the C{in} operator on a C{BioSequence}.
        
        The C{in} operator test if the C{key} value is defined for this
        sequence.
         
        :param key: the name of the checked value
        :type key: str
        :return: C{True} if the value is defined, {False} otherwise.
        :rtype: C{bool}
        '''
        if key=='taxid' and self._hasTaxid is None:
            self.extractTaxon()
        return self.hasKey(key)
    
    def rawiteritems(self):
        return self._info.iteritems()

    def iteritems(self):
        '''
        iterate other items dictionary storing the values
        associated to the sequence. It works similarly to
        the iteritems function of C{dict}.
        
        :return: an iterator over the items (key,value)
                 link to a sequence
        :rtype: iterator over tuple
        :see: L{items}
        '''
        if self.__rawinfo is not None:
            p = re.compile(self._rawparser % "([a-zA-Z]\w*)")
            for k,v in p.findall(self.__rawinfo):
                try:
                    self._info[k]=eval(v)
                except:
                    self._info[k]=v
            self.__rawinfo=None
        return self._info.iteritems()
    
    cpdef list items(self):
        return [x for x in self.iteritems()]
    
    def iterkeys(self):
        return (k for k,v in self.iteritems())
    
    cpdef list keys(self):
        return [x for x in self.iterkeys()]
    
    cpdef dict getTags(self):
        self.iteritems()
        return self._info
    
    cpdef object getRoot(self):
        return self
    
    def getWrappers(self):
        if self._wrappers is None:
            self._wrappers=WrapperSet()
        return self._wrappers
    
    def register(self,wrapper):
        self.wrappers.add(ref(wrapper,self._unregister))
        
    def _unregister(self,ref):
        self.wrappers.remove(ref)
        
    wrappers = property(getWrappers,None,None,'')

    definition = property(getDefinition, setDefinition, None, "Sequence Definition")

    id = property(getId, setId, None, 'Sequence identifier')
        
    cpdef int _getTaxid(self):
        return self['taxid']
    
    cpdef _setTaxid(self,int taxid):
        self['taxid']=taxid
        
    cpdef bytes _getRawInfo(self):
        return self.__rawinfo
    
    _rawinfo = property(_getRawInfo)

        
    taxid = property(_getTaxid,_setTaxid,None,'NCBI Taxonomy identifier')
    _seq = property(get_seq, set_seq, None, None)

    def _getQuality(self):
        if self.__quality is None:
            raise AttributeError
        else:
            return self.__quality

    def _setQuality(self,qual):
        self.__quality=qual
        
    def _delQuality(self):
        self.__quality=None

    quality = property(_getQuality,_setQuality,_delQuality,'Quality associated to the sequence')
    
cdef class NucSequence(BioSequence):
    """
    :py:class:`NucSequence` specialize the :py:class:`BioSequence` class for storing DNA
    sequences. 
    
    The constructor is identical to the :py:class:`BioSequence` constructor.
    """
 
    cpdef object complement(self):
        """
        :return: The reverse complemented sequence as an instance of :py:class:`DNAComplementSequence`
        :rtype: :py:class:`DNAComplementSequence`
        """
        return DNAComplementSequence(self)
    
    cpdef bint isNucleotide(self):
        return True

    
cdef class AASequence(BioSequence):
    """
    :py:class:`AASequence` specialize the :py:class:`BioSequence` class for storing protein
    sequences. 
    
    The constructor is identical to the :py:class:`BioSequence` constructor.
    """
 

    cpdef bint isNucleotide(self):
        return False
    

    
cdef class WrappedBioSequence(BioSequence):
    """
    .. warning:: 
        
            :py:class:`obitools.WrappedBioSequence` is an abstract class, this constructor
            can only be called by a subclass constructor.
    """
 

    def __init__(self, object reference,
                       bytes id=None,
                       bytes definition=None,
                       **info):

        assert type(self)!=WrappedBioSequence,"obitools.WrappedBioSequence is an abstract class"

        self._wrapped = reference
        reference.register(self)
        self._id=id
        self.definition=definition
        self._info=info
        
    cpdef object clone(self):
        seq = type(self)(self.wrapped,
                         id=self._id,
                         definition=self._definition
                         )
        seq._info=dict(self._info)
        
        return seq
        
    cpdef object getWrapped(self):
        return self._wrapped
        
    cpdef bytes getDefinition(self):
        d = self._definition or self.wrapped.definition
        return d
    
    cpdef setDefinition(self, bytes value):
        '''
        Sequence definition setter.
        
        :param value: the new sequence definition
        :type value: C{str}
        :return: C{None}
        '''
        self._definition=value

    cpdef bytes getId(self):
        d = self._id or self.wrapped.id
        return d
    
    cpdef setId(self, bytes value):
        '''
        Sequence identifier setter.
        
        :param value: the new sequence identifier
        :type value:  C{str}
        :return: C{None}
        '''
        self._id = value

    cpdef bint isNucleotide(self):
        return self.wrapped.isNucleotide()
    

    def iterkeys(self):
        return uniqueChain(self._info.iterkeys(),
                               self.wrapped.iterkeys())
        
    def rawiteritems(self):
        return chain(self._info.iteritems(),
                        (x for x in self.wrapped.rawiteritems()
                         if x[0] not in self._info))

    def iteritems(self):
        for x in self.iterkeys():
            yield (x,self[x])
            
    cpdef object getKey(self,bytes key):
        if key in self._info:
            return self._info[key]
        else:
            return self.wrapped.getKey(key)
        
    cpdef bint hasKey(self,bytes key):
        return key in self._info or self.wrapped.hasKey(key)
            
    cpdef  getSymbolAt(self, int position):
        return self.wrapped.getSymbolAt(self.posInWrapped(position))
    
    cpdef int posInWrapped(self, int position, object reference=None):
        if reference is None or reference is self.wrapped:
            return self._posInWrapped(position)
        else:
            return self.wrapped.posInWrapped(self._posInWrapped(position),reference)
            
    
    cpdef bytes getStr(self):
        return str(self.wrapped)
    
    cpdef object getRoot(self):
        return self.wrapped.getRoot()
    
    cpdef object complement(self):
        """
        The :py:meth:`complement` method of the :py:class:`WrappedBioSequence` class 
        raises an exception :py:exc:`AttributeError` if the method is called and the cut
        sequence does not corresponds to a nucleic acid sequence.
        """
        
        if self.wrapped.isNucleotide():
            return DNAComplementSequence(self)
        raise AttributeError

    
    cpdef int _posInWrapped(self, int position):
        return position
    
    
    definition = property(getDefinition,setDefinition, None)
    id = property(getId,setId, None)

    wrapped = property(getWrapped, None, None, "A pointer to the wrapped sequence")
    
    cpdef bytes _getRawInfo(self):
        return self.wrapped.__rawinfo
    
    _rawinfo = property(_getRawInfo)
        

cdef int _sign(int x):
    if x == 0:
        return 0
    elif x < 0:
        return -1
    return 1

cdef class SubSequence(WrappedBioSequence):
    """
    """
    
    def __init__(self, object reference,
                       object location=None,
                       int start=0, object stop=None,
                       object id=None,
                       object definition=None,
                 **info):
        WrappedBioSequence.__init__(self,reference,id=None,definition=None,**info)
        
        if isinstance(location, slice):
            self._location = location
        else:
            step = 1
            start = 0;
            if not isinstance(stop,int):
                stop = len(reference)
            self._location=slice(start,stop,step)

        self._indices=self._location.indices(len(self.wrapped))
        self._xrange=xrange(*self._indices)
 
        self._info['cut']='[%d,%d,%s]' % self._indices
        
        if hasattr(reference,'quality'):
            self.quality = reference.quality[self._location]
        
    cpdef bytes getId(self):
        d = self._id or ("%s_SUB" % self.wrapped.id)
        return d
    
    cpdef setId(self, bytes value):
        '''
        Sequence identifier setter.
        
        :param value: the new sequence identifier
        :type value:  C{str}
        :return: C{None}
        '''
        WrappedBioSequence.setId(self,value)

        
    cpdef object clone(self):
        seq = WrappedBioSequence.clone(self)
        seq._location=self._location
        seq._indices=seq._location.indices(len(seq.wrapped))
        seq._xrange=xrange(*seq._indices)
        return seq
        
           
    def __len__(self):
        return len(self._xrange)
    
    cpdef bytes getStr(self):
        return ''.join([x for x in self])
    
    def __iter__(self):
        return (self.wrapped.getSymbolAt(x) for x in self._xrange)
    
    cpdef int _posInWrapped(self, int position):
        return self._xrange[position]
    
    
    id = property(getId,setId, None)

cdef dict _comp={'a': 't', 'c': 'g', 'g': 'c', 't': 'a',
                 'r': 'y', 'y': 'r', 'k': 'm', 'm': 'k', 
                 's': 's', 'w': 'w', 'b': 'v', 'd': 'h', 
                 'h': 'd', 'v': 'b', 'n': 'n', 'u': 'a',
                 '-': '-'}


cdef class DNAComplementSequence(WrappedBioSequence):
    """
    Class used to represent a reverse complemented DNA sequence. Usually instances
    of this class are produced by using the :py:meth:`NucSequence.complement` method.
    """
     
    def __init__(self, object reference,
                       bytes id=None,
                       bytes definition=None,
                       **info):
        WrappedBioSequence.__init__(self,reference,id=None,definition=None,**info)
        assert reference.isNucleotide()
        self._info[b'complemented']=True
        if hasattr(reference,'quality'):
            self.quality = reference.quality[::-1]

           
    cpdef bytes getId(self):
        d = self._id or (b"%s_CMP" % self.wrapped.id)
        return d
    
    cpdef setId(self, bytes value):
        '''
        Sequence identifier setter.
        
        :param value: the new sequence identifier
        :type value:  C{str}
        :return: C{None}
        '''
        WrappedBioSequence.setId(self,value)

    def __len__(self):
        return len(self._wrapped)
    
    cpdef bytes getStr(self):
        return ''.join([x for x in self])
    
    def __iter__(self):
        return (self.getSymbolAt(x) for x in xrange(len(self)))
    
    cpdef int _posInWrapped(self, int position):
        return -(position+1)

    cpdef  getSymbolAt(self, int position):
        return _comp[self.wrapped.getSymbolAt(self.posInWrapped(position))]
    
    cpdef object complement(self):
        """
        The :py:meth:`complement` method of the :py:class:`DNAComplementSequence` class actually
        returns the wrapped sequenced. Effectively the reversed complemented sequence of a reversed
        complemented sequence is the initial sequence.
        """
        return self.wrapped
    
    id = property(getId,setId, None)
                
cdef set _iupac=set(['r', 'y', 'k', 'm', 
                     's', 'w', 'b', 'd', 
                     'h', 'v', 'n',
                     'R', 'Y', 'K', 'M', 
                     'S', 'W', 'B', 'D', 
                     'H', 'V', 'N'])

#cdef char *_iupac=b"acgtrykmswbdhvnu-"

cdef set _nuc = set(['a', 'c', 'g', 't','u','A', 'C', 'G', 'T','U','-'])

#cdef char *_nuc=b"acgt-"

cpdef bint _isNucSeq(bytes text):
    cdef int acgt
    cdef int notnuc
    cdef int ltot,lltot
    cdef int  i
    
    acgt   = 0
    notnuc = 0
    lltot  = len(text)
    ltot   = lltot * 4 / 5
    
    for c in text:
        if c in _nuc:
            acgt+=1
        elif c not in _iupac:
            notnuc+=1
    return notnuc==0 and acgt > ltot

  
cdef object _bioSeqGenerator(bytes id,
                             bytes seq,
                             bytes definition,
                             bytes rawinfo,
                             bytes rawparser,
                             dict info):
                             
    if _isNucSeq(seq):
        return NucSequence(id,seq,definition,rawinfo,rawparser,**info)
    else:
        return AASequence(id,seq,definition,rawinfo,rawparser,**info)


def  bioSeqGenerator(bytes id,
                     bytes seq,
                     bytes definition=None,
                     bytes rawinfo=None,
                     bytes rawparser=__default_raw_parser,
                     **info):
    """
    Generate automagically the good class instance between :
    
        - :py:class:`NucSequence`
        - :py:class:`AASequence`
    
    Build a new sequence instance. Sequences are instancied as :py:class:`NucSequence` if the
    `seq` attribute contains more than 80% of *A*, *C*, *G*, *T* or *-* symbols 
    in upper or lower cases. Conversely, the new sequence instance is instancied as 
    :py:class:`AASequence`.
    

    
    :param id: sequence identifier
    :type id:  `str`
    
    :param seq: the sequence
    :type seq:  `str`
    
    :param definition: sequence definition (optional)
    :type definition: `str`
    
    :param rawinfo: a text containing a set of key=value; patterns
    :type definition: `str`
    
    :param rawparser: a text describing a regular patterns template 
                      used to parse rawinfo
    :type definition: `str`
    
    :param info: extra named parameters can be added to associate complementary
                 data to the sequence
    """
    return _bioSeqGenerator(id,seq,definition,rawinfo,rawparser,info)
