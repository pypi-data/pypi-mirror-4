'''
Created on 24 sept. 2010

@author: coissac
'''

from obitools.ecopcr.taxonomy import  TaxonomyDump 
from obitools.ecopcr.taxonomy import  Taxonomy
import sys

class EcoTaxonomyDB(TaxonomyDump) :

    def __init__(self,dbconnect):
        self._dbconnect=dbconnect
        
        print >> sys.stderr,"Reading ecobarcode taxonomy database..."
        
        self._readNodeTable()
        print >> sys.stderr," ok"
         
        print >>sys.stderr,"Adding scientific name..."
    
        self._name=[]
        for taxid,name,classname in self._nameIterator():
            self._name.append((name,classname,self._index[taxid]))
            if classname == 'scientific name':
                self._taxonomy[self._index[taxid]].append(name)
            
        print >>sys.stderr,"Adding taxid alias..."
        for taxid,current in self._mergedNodeIterator():
            self._index[taxid]=self._index[current]
        
        print >>sys.stderr,"Adding deleted taxid..."
        for taxid in self._deletedNodeIterator():
            self._index[taxid]=None

        
        Taxonomy.__init__(self)

    #####
    #
    # Iterator functions
    #
    #####
                   
    def _readNodeTable(self):
    
        cursor = self._dbconnect.cursor()
        
        cursor.execute("""
                            select     taxid,rank,parent
                            from ncbitaxonomy.nodes
                       """)
        
        print >>sys.stderr,"Reading taxonomy nodes..."
        taxonomy=[list(n) for n in cursor]
        
        print >>sys.stderr,"List all taxonomy rank..."    
        ranks =list(set(x[1] for x in taxonomy))
        ranks.sort()
        rankidx = dict(map(None,ranks,xrange(len(ranks))))
        
        print >>sys.stderr,"Sorting taxons..."
        taxonomy.sort(TaxonomyDump._taxonCmp)

        self._taxonomy=taxonomy
    
        print >>sys.stderr,"Indexing taxonomy..."
        index = {}
        for t in self._taxonomy:
            index[t[0]]=self._bsearchTaxon(t[0])
        
        print >>sys.stderr,"Indexing parent and rank..."
        for t in self._taxonomy:
            t[1]=rankidx[t[1]]
            t[2]=index[t[2]]
         
        self._ranks=ranks
        self._index=index 
        
        cursor.close()

    def _nameIterator(self):
        cursor = self._dbconnect.cursor()
        
        cursor.execute("""
                            select     taxid,name,nameclass
                            from ncbitaxonomy.names
                       """)

        for taxid,name,nameclass in cursor:
            yield taxid,name,nameclass
            
        cursor.close()
                        
    def _mergedNodeIterator(self):
        cursor = self._dbconnect.cursor()
        
        cursor.execute("""
                            select     oldtaxid,newtaxid
                            from ncbitaxonomy.merged
                       """)

        for oldtaxid,newtaxid in cursor:
                yield oldtaxid,newtaxid
                
        cursor.close()
      
    def _deletedNodeIterator(self):
        cursor = self._dbconnect.cursor()
        
        cursor.execute("""
                            select  taxid
                            from ncbitaxonomy.delnodes
                       """)

        for taxid in cursor:
                yield taxid[0]

        cursor.close()
