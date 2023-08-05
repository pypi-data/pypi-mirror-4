import sys

from _dict cimport *

cpdef object str2number(char* cinput):
    """
    Fast string to float or int conversion function.
    
    Internal function do not use directly
    
    @see: 
    """
    cdef char *stop 
    cdef long iresult
    cdef double dresult
    cdef object result=None
    
    iresult = strtol(cinput,&stop,10)
    
    if stop[0]!=';':
        dresult = strtod(cinput,&stop)
        if stop[0]==';':
            result  = PyFloat_FromDouble(dresult)
    else:
        result = PyInt_FromLong(iresult)
        
    return result

cdef object str2bool(char* cinput):
    cdef long iresult
    cdef object result=None
    
    iresult = strncmp(cinput, b"True;", 5)
    
    if iresult==0: result=True
        
    iresult = strncmp(cinput, b"False;", 6)
    
    if iresult==0: result=False
        
    return result

cdef class AbstractTag(dict):
    """
    This class is used as base class for Tag and AbstractTag classes
    and cannot be initialized directly.
    
    This is a sub class of the standard dict python class. 
    """

    def __init__(self,d=None, 
                 **values):
        '''
        Initialize the base class AbstractTag.
        
        The arguments of the __init__ function are used to initialized
        the dictionary in the same way than the one used for the dict
        class.
        
        :param d: an iterable element used for initializing the dictionary
                  or None if the AbstractTag instance is created empty.
        :type d: iterable or None
        '''

        if d is not None:
            if PyDict_Check(d):
                dict.__init__(self,d.items())
            else:
                dict.__init__(self,d)
        PyDict_Update(self,values)
                    
        
    cdef char* __pchar(self,char *buffer,Py_ssize_t *size,Py_ssize_t *pos):
        return <char*>NULL

    cdef int __itemsnext(self,Py_ssize_t *pos,PyObject** key,PyObject** value):
        return 0
    
    cdef PyObject* _getitemstring(self,char* ckey):
        return <PyObject*>NULL
    
    cdef bint __hasKey(self, char* ckey):
        return False
    
    cdef int _delitemstring(self, char* ckey):
        return -1 
    
    cdef void _setitemstring(self,char *ckey, object value):
        PyDict_SetItemString(self,ckey,value)
        
    cdef void _clear(self):
        PyDict_Clear(self)

    
    cdef int _length(self):
        return -1
        
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
        cdef Py_ssize_t pos=0
        cdef PyObject* pkey
        cdef PyObject* pvalue
        cdef object key
        cdef object value
        cdef int ok
        
        ok = self.__itemsnext(&pos,&pkey,&pvalue)

        while(ok):

            key  = <object> pkey
            value= <object> pvalue
            
            yield key,value

            ok = self.__itemsnext(&pos,&pkey,&pvalue)
            
    
    def items(self):
        '''
        Return a list of pairs (tuple) associating keys and values.
        
        :return: a list of (key,value) pairs
        :rtype: list 
        '''
        return [x for x in self.iteritems()]
    
    
    def __iter__(self):
        return self.iterkeys()
    
    def iterkeys(self):
        cdef bytes k
        return (k for k,v in self.iteritems())
    
    def keys(self):
        return [x for x in self.iterkeys()]
    
    def itervalues(self):
        cdef bytes k        
        return (v for k,v in self.iteritems())
    
    def values(self):
        return [x for x in self.itervalues()]
    
    def __str__(self):
        return self.__bytes__()
    
    def __repr__(self):
        return '<obitools.%s @ %d: %s>' % (self.__class__.__name__,id(self),self.__bytes__())
    
    def __contains__(self, bytes key):
        cdef char*     ckey=key
        
        return self.__hasKey(ckey)
    
    def has_key(self, bytes key):
        cdef char*     ckey=key
        
        return self.__hasKey(ckey)

    def get(self, bytes key, object default=None):
        cdef PyObject* pvalue
        cdef object    value
        cdef char*     ckey=key
        cdef bint      error
        
        pvalue = self._getitemstring(ckey)
        
        if pvalue == NULL:
            value=default
        else:
            value=<object>pvalue                    

        return value

    
    def __getitem__(self,bytes key):
        cdef PyObject* pvalue
        cdef object    value
        cdef char*     ckey=key
        cdef bint      error
        
        pvalue = self._getitemstring(ckey)
        
        if pvalue == NULL:
            raise KeyError,key

        value=<object>pvalue                    

        return value
    
    def __setitem__(self,bytes key, object value):
        cdef char* ckey=key
        self._setitemstring(ckey,value)
                
    def __delitem__(self,bytes key):
        cdef char*     ckey=key
        cdef int       error
        error = self._delitemstring(ckey)
        if error != 0:
            raise KeyError,key 

    def __bytes__(self):
        cdef Py_ssize_t  sizebuf=10000
        cdef char *rep
        cdef Py_ssize_t pos=0
        cdef bytes dval
        
        rep = self.__pchar(NULL,&sizebuf,&pos)
 
        if pos > 0:
            dval = PyBytes_FromStringAndSize(rep,pos)
        else:
            deval=""
            
        free(rep)
        
        return dval
    
    def __len__(self):
        return self._length()
    
    def clear(self):
        self._clear()
        
    @classmethod
    def fromkeys(keys,value=None):
        raise NotImplementedError
    
    def pop(self,bytes key,*defaults):
        cdef PyObject* rep
        cdef char* ckey=key
        cdef object o 
        
        rep = self._getitemstring(ckey)
        
        if rep==NULL:
            if PyTuple_GET_SIZE(defaults)==0:
                raise KeyError,key
            rep = PyTuple_GET_ITEM(defaults,0)
            o=<object>rep
        else:
            o=<object>rep
            self._delitemstring(ckey)
        
        return o
    
    def popitem(self):
        try:
            i=self.iteritems().next()
        except StopIteration:
            raise KeyError
        del self[i[0]]
        
        return i
    
    def setdefault(self,bytes key,object default=None):
        cdef PyObject* rep
        cdef char* ckey=key
        cdef object o 

        rep = self._getitemstring(ckey)
        
        if rep==NULL:
            o=default 
            self._setitemstring(ckey,default)
        else:
            o=<object>rep
            
        return o

    def copy(self):
        return Tag(self)
    

                
#
# Initialisation of global variable corresponding to
# the default parser used by the class tag
#

cdef char* defaultParser=" %s *= *([^;]*);"
cdef char* defaultFormat="%s=%s;"
cdef char* defaultKey="([a-zA-Z][^ ]*)"

cdef bint    compDefaultPattern=False
cdef regex_t defaultPattern

cdef int        retcomp
cdef char*      cpattern

retcomp = asprintf(&cpattern,defaultParser,defaultKey)
if retcomp<0: 
    raise SystemError

retcomp = regcomp(&defaultPattern,cpattern,REG_EXTENDED)
free(cpattern)
       
if retcomp!=0: 
    regfree(&defaultPattern)
    raise SystemError



cdef class Tag(AbstractTag):
    """
    Dictionary like class used for storing attributes associated to a
    sequence.
    
    Some restrictions exist compare to a classic python dictionary:
    
        - Keys have to be bytes
        
    Tag can be initialized using a string (bytes) that will be parsed
    on purpose.
    """
    
    cdef object _eval(self,char* svalue,int length):
        cdef object result=None
    
        if svalue[0]=='T' or svalue[0]=='F':
            result=str2bool(svalue)
            
        if result is None:
            result=str2number(svalue)
            
        if result is None:
            if strncmp(svalue, b"None;", 5)!=0:                
                result=PyBytes_FromStringAndSize(svalue,length)
                if    svalue[0]=='(' \
                   or svalue[0]=='[' \
                   or svalue[0]=='{' \
                   or strncmp(svalue, b"set(", 4)==0:
                    try:
                        result = eval(result)
                    except:
                        pass 
                    
        return result
            
    
    cdef PyObject* _extractitem(self, char* ckey):
        cdef char*      cpattern
        cdef char*      kparser=self._kparser
        cdef char*      craw      = self._raw
        cdef regex_t    rpattern
        cdef regmatch_t rmatch[2]
        cdef int        retcomp
        cdef int        lmatch
        cdef char*      bmatch
        cdef object     value=None
        cdef PyObject*  pvalue=NULL
        
        if self._raw==NULL:
            return NULL
        
        retcomp = asprintf(&cpattern,kparser,ckey)
    
        if retcomp<0: 
            return NULL 
            
        retcomp = regcomp(&rpattern,cpattern,REG_EXTENDED)
                              
        if retcomp!=0 or rpattern.re_nsub!=1: 
            free(cpattern)
            regfree(&rpattern)
            return NULL 

        retcomp = regexec(&rpattern,craw,2,rmatch,0)        
        
        if retcomp==0:
            bmatch = craw + rmatch[1].rm_so
            lmatch = rmatch[1].rm_eo - rmatch[1].rm_so
            value=self._eval(bmatch,lmatch)
            memset(craw + rmatch[0].rm_so,
                   255,
                   rmatch[0].rm_eo - rmatch[0].rm_so)
            PyDict_SetItemString(self,ckey,value)
            pvalue=<PyObject*>value
                            
        # print "1 : %d -> %d" % (rmatch[0].rm_so,rmatch[0].rm_eo)
        # print "1 : %d -> %d" % (rmatch[1].rm_so,rmatch[1].rm_eo)

        regfree(&rpattern)
        free(cpattern)
        
        return pvalue
    
    cdef PyObject* _getitemstring(self,char* ckey):
        cdef PyObject* pvalue
        cdef object    value
        
        pvalue = PyDict_GetItemString(self,ckey)
        
        if pvalue == NULL:
            pvalue = self._extractitem(ckey)
            
            if pvalue==NULL and  strcmp(ckey,"count")==0:
                value=1
                PyDict_SetItemString(self,ckey,value)
                pvalue=<PyObject*>value
                    
        return pvalue
    
    cdef int _length(self):
        cdef list k
        if self._raw!=NULL:
            k = self.items()
        return PyDict_Size(self)

    cdef void _clear(self):
        if self._localraw:
            free(self._raw)  
        self._localraw=False
        self._raw=NULL
        PyDict_Clear(self)

        

    cdef int _delitemstring(self,char* ckey):

        if self.__hasKey(ckey):
            PyDict_DelItemString(self,ckey)
            return 0
        return -1
        
    
    
    def __init__(self,
                 object d=None, 
                 bytes raw=None,
                 bytes parser=None,
                 **values):
        '''
        
        :param d:
        :type d:
        '''
        
        cdef int lstr
        cdef char* cstr
        cdef char* ckey="([a-zA-Z][^ ]*)"
        cdef char* cparser
        cdef char* cpattern
        cdef int      retcomp
        cdef regex_t* rpattern

        if PyString_Check(d):
            d = bytes(d)
            
        if PyBytes_Check(d):
            if raw is not None:
                raw = b"%s %s" % (d,raw)
            else:
                raw = d
            d=None
            

        AbstractTag.__init__(self,d,**values)
        self._localraw=False
        
        if raw is None:
            self._raw=NULL
            self._lraw=0
        else:
            lstr = len(raw) + 2
            self._lraw=lstr-2
            if lstr > 2:
                self._localraw=True
                self._raw=<char*>malloc(lstr)
                if self._raw != NULL:
                    cstr = raw
                    strcpy(self._raw+1,cstr)
                    self._raw[0]=' '
                else:
                    raise MemoryError
            else:
                self._raw=NULL
                self._lraw=0
                
        if parser is None:
            self._defParser=True
            self._kparser=defaultParser
            self._prparser=&defaultPattern
        else:
            lstr = len(parser) + 1
            if lstr > 1:
                self._defParser=False
                self._kparser = <char*>malloc(lstr)
                if self._kparser == NULL:
                    raise SystemError
                cparser = parser
                strcpy(self._kparser,cparser)

                self._prparser=&(self._rparser)
                rparser=self._prparser
                retcomp = asprintf(&cpattern,self._kparser,defaultKey)
                
                if retcomp<0: 
                    raise SystemError
            
                retcomp = regcomp(rpattern,cpattern,REG_EXTENDED)
                free(cpattern)
                   
                if retcomp!=0: 
                    regfree(rpattern)
                    raise SystemError
                
                
                
                # If the object is not using the default parser
                # we force the full parsing of the raw string
                # during the object initialisation
                
                k = self.items()

            else:
                self._defParser=True
                self._kparser=defaultParser
                self._prparser=&defaultPattern
            
                        
    @classmethod
    def fromkeys(self,keys,value=None):
        r = Tag()
        for k in keys:
            r[k]=value 
        return r
        
    cdef int __compact_raw__(self,char* dest=NULL):
        cdef char* p1
        cdef char* p2
        
        if dest==NULL:
            dest=self._raw
            
        if self._raw != NULL:
            p1 = self._raw
            p2 = dest
            
            while (p1[0]!=0):
                if p1[0]!=-1:
                    p2[0]=p1[0]
                    p2+=1
                p1+=1
                    
            p2[0]=0
            
        return (p2 - dest)
            
            

    def __dealloc__(self):
        if self._localraw:
            free(self._raw)  
        
        if not self._defParser:
            free(self._kparser)
            regfree(self._prparser)
            
    def clear(self):
        if self._localraw:
            free(self._raw)
            self._localraw=False
        AbstractTag.clear(self)
        
    def update(self,data):
        if self._raw != NULL:
            self.items()
        AbstractTag.update(self,data)
            
    cdef char* __pchar(self,char *buffer,Py_ssize_t *size,Py_ssize_t *pos):
        cdef int  sizebuf=size[0]
        cdef char *rep
        cdef Py_ssize_t i=pos[0]
        cdef int  lp=0 
        cdef Py_ssize_t  kpos=0
        cdef char* ckey
        cdef PyObject* pvalue
        cdef PyObject* pkey
        cdef object key
        cdef bytes bvalue
        cdef char* cvalue   
                
        if buffer==NULL:
            rep=<char*>malloc(sizebuf)
        else:
            rep=buffer
        
        while (PyDict_Next(self, &kpos, &pkey, &pvalue)):
            
            key=<object>pkey
            ckey = PyBytes_AS_STRING(key)
            bvalue=bytes(<object>pvalue)
            cvalue=bvalue
            lp = snprintf(rep+i,sizebuf - i,defaultFormat,ckey,cvalue)
            if lp < 0:
                raise SystemError

            while lp >= (sizebuf - i):
                sizebuf*=2
                rep = <char*>realloc(rep,sizebuf)
                lp = snprintf(rep+i,sizebuf - i,defaultFormat,ckey,cvalue)
                if lp < 0:
                    raise SystemError
            
            i+=lp   
            
            if  (sizebuf - i) <2:
                sizebuf*=2
                rep = <char*>realloc(rep,sizebuf)

            rep[i]=' '
            i+=1
            
        if i>0:
            i-=1
            
        rep[i]=0
                        
        if self._raw!=NULL:
            if (sizebuf - i) <= self._lraw:
                sizebuf+=self._lraw+1
                rep = <char*>realloc(rep,sizebuf)
            i+=self.__compact_raw__(rep+i)
             
        if i>0:
            pos[0]=i
            size[0]=sizebuf
            
        return rep
            
    cdef bint __hasKey(self, char* ckey):
        cdef PyObject* pvalue
        cdef object    value
        cdef bint      error
        cdef bint      rep=False

        pvalue = PyDict_GetItemString(self,ckey)

        if pvalue == NULL:
            pvalue = self._extractitem(ckey)
        
        return pvalue!=NULL
    
 
    cdef void _setitemstring(self,char *ckey, object value):
        if self._raw!=NULL:
            self.__hasKey(ckey)
        PyDict_SetItemString(self,ckey,value)
        
    cdef int __itemsnext(self,Py_ssize_t *pos,PyObject** key,PyObject** value):
        '''
        iterate other items dictionary storing the values
        associated to the sequence. It works similarly to
        the iteritems function of C{dict}.
        
        :return: an iterator over the items (key,value)
                 link to a sequence
        :rtype: iterator over tuple
        :see: L{items}
        '''

        cdef char*      craw      = self._raw
        cdef regmatch_t rmatch[3]
        cdef int        retcomp
        cdef int        lmatch
        cdef char*      bmatch
        cdef object     _value=None

        #
        # During the first call to this function 
        # we parse the raw argument
        #
        
        if craw!=NULL:
            rpattern = self._prparser
            retcomp = regexec(rpattern,craw,3,rmatch,0)
                        
            while(retcomp==0):
                bmatch = craw + rmatch[2].rm_so
                lmatch = rmatch[2].rm_eo - rmatch[2].rm_so
                _value=self._eval(bmatch,lmatch)
                bmatch = craw + rmatch[1].rm_so
                lmatch = rmatch[1].rm_eo - rmatch[1].rm_so
                bmatch[lmatch]=0
                    
                PyDict_SetItemString(self,bmatch,_value)
                
                memset(craw + rmatch[0].rm_so,
                       255,
                       rmatch[0].rm_eo - rmatch[0].rm_so)
                                
                craw+=rmatch[0].rm_eo - rmatch[0].rm_so
                retcomp = regexec(rpattern,craw,3,rmatch,0)

            free(self._raw)
            self._raw=NULL

        return PyDict_Next(self, pos, key, value)  
         
    

cdef class WrappedTag(AbstractTag):

    def __init__(self,AbstractTag wrapped,
                 **values):

        super(AbstractTag,self).__init__(values)        
        self._wrapped = wrapped
        self._deleted = {}
        
    cdef void _clear(self):
        self._deleted.update([(k,None) for k in self._wrapped])
        PyDict_Clear(self)
        
    cdef PyObject* _getitemstring(self,char* ckey):
        cdef PyObject* pvalue

        pvalue = PyDict_GetItemString(self,ckey)

        if pvalue == NULL and PyDict_GetItemString(self._deleted,ckey)==NULL:
            pvalue = self._wrapped._getitemstring(ckey)
            
        return pvalue
  
  
    cdef int _delitemstring(self,char* ckey):
        cdef int delok
    
        if PyDict_GetItemString(self,ckey)!=NULL:
            delok = PyDict_DelItemString(self,ckey)
            return 0
        
        if self._wrapped.__hasKey(ckey) and PyDict_GetItemString(self._deleted,ckey)==NULL:
            PyDict_SetItemString(self._deleted,ckey,None)
            return 0
                    
        return -1

    cdef bint __hasKey(self, char* ckey):
        cdef PyObject* pvalue
        cdef bint      rep=False

        pvalue = PyDict_GetItemString(self,ckey)

        if pvalue == NULL:
            if PyDict_GetItemString(self._deleted,ckey)!=NULL:
                return False
            rep = self._wrapped.__hasKey(ckey)
        else:
            rep=True
            
        return rep
                
    cdef int __itemsnext(self,Py_ssize_t *pos,PyObject** key,PyObject** value):
        '''
        iterate other items dictionary storing the values
        associated to the sequence. It works similarly to
        the iteritems function of C{dict}.
        
        :return: an iterator over the items (key,value)
                 link to a sequence
        :rtype: iterator over tuple
        :see: L{items}
        '''

        cdef Py_ssize_t mask=1 << (sizeof(Py_ssize_t)*8-1)
        cdef Py_ssize_t nmask= ~mask 
        cdef Py_ssize_t lpos=pos[0]
        cdef int        retcomp
        cdef object     pkey
        cdef char*      ckey

        #
        # During the first call to this function 
        # we parse the raw argument
        #
        
        if lpos & mask == mask:
            lpos &= nmask
            retcomp = self._wrapped.__itemsnext(&lpos,key,value) 
            pkey = <object>key[0]
            ckey = pkey
            while(retcomp and (PyDict_GetItemString(self._deleted,ckey)!=NULL 
                          or PyDict_GetItemString(self,ckey)!=NULL)): 
                retcomp = self._wrapped.__itemsnext(&lpos,key,value) 
                pkey = <object>key[0]
                ckey = pkey
            pos[0] = lpos | mask        
        else:
            retcomp = PyDict_Next(self, pos, key, value) 
            if retcomp==0:
                pos[0] = lpos | mask
                retcomp = self.__itemsnext(&pos[0],key,value) 
                            
        return retcomp 

    cdef int _length(self):
        return PyDict_Size(self) + self._wrapped._length() - PyDict_Size(self._deleted)


    cdef char* __pchar(self,char *buffer,Py_ssize_t *size,Py_ssize_t *pos):
        return b"coucou"