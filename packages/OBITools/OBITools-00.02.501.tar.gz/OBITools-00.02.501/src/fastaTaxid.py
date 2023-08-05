#!/usr/local/bin/python

from obitools.fasta import fastaIterator,formatFasta
from obitools.options import getOptionManager
from obitools.obischemas import initConnection,getConnection
from obitools.obischemas.options import addConnectionOptions
from obitools.table.csv import csvIterator

from obitools import NucSequence


import sys
import re
from logging import root,DEBUG

def addFastaTaxidOptions(optionManager):
    
    optionManager.add_option('-r','--restrict',
                             action="store", dest="restrict",
                             metavar="<TAXID>",
                             type="string",
                             default=None,
                             help="taxid limiting to a taxonomic "
                                  "subtree")

    optionManager.add_option('-c','--csv',
                             dest="csv",
                             action="store_true", 
                             default=False,
                             help="the input file is a Ludovic CSV format")
                               

def lookForTaxon(taxon,restriction=None,connection=None):
    if connection is None:
        connection=getConnection()
    cur = connection.cursor()
    if restriction is None:
        query='''
                 select n.taxid,r.scientific_name 
                 from ncbi_taxonomy.name as n,
                      ncbi_taxonomy.taxon as r
                 where n.taxid=r.numid 
                   and n.name = '%s'
              ''' % taxon.strip()
    else:
        query='''
                 select n.taxid,r.scientific_name 
                 from ncbi_taxonomy.name as n,
                      ncbi_taxonomy.taxon as r
                 where n.taxid=r.numid 
                   and r.path ~ '*.%s.*'
                   and n.name = '%s'
              ''' % (restriction,taxon.strip())
        
    cur.execute(query)
    
    return [x for x in cur]


def lookForGenus(genus,restriction=None,connection=None):
    if connection is None:
        connection=getConnection()
    cur = connection.cursor()
    if restriction is None:
        query='''
                 select n.taxid,r.scientific_name 
                 from ncbi_taxonomy.name as n,
                      ncbi_taxonomy.genus_rank as r
                 where n.taxid=r.numid 
                   and n.name='%s'
              ''' % genus.strip()
    else:
        query='''
                 select n.taxid,r.scientific_name 
                 from ncbi_taxonomy.name as n,
                      ncbi_taxonomy.genus_rank as r
                 where n.taxid=r.numid 
                   and r.path ~ '*.%s.*'
                   and n.name='%s'
              ''' % (restriction,genus.strip())
        
    cur.execute(query)
    
    return [x for x in cur]

def lookForFamily(family,restriction=None,connection=None):
    if connection is None:
        connection=getConnection()
    cur = connection.cursor()
    if restriction is None:
        query='''
                 select n.taxid,r.scientific_name 
                 from ncbi_taxonomy.name as n,
                      ncbi_taxonomy.family_rank as r
                 where n.taxid=r.numid 
                   and n.name='%s'
              ''' % family.strip()
    else:
        query='''
                 select n.taxid,r.scientific_name 
                 from ncbi_taxonomy.name as n,
                      ncbi_taxonomy.family_rank as r
                 where n.taxid=r.numid 
                   and r.path ~ '*.%s.*'
                   and n.name='%s'
              ''' % (restriction,family.strip())
        
    cur.execute(query)
    
    return [x for x in cur]

def csvEntryIterator(entries):
    for data in csvIterator(entries):
        seq = NucSequence(data[1],data[5])
        for x in data[2:5]:
            rank,name=x.split('=',1)
            seq[rank]=name
        yield seq
        
__missing_family = set()
__missing_genus  = set()
__missing_species= set()

__multiple_family = set()
__multiple_genus  = set()
__multiple_species= set()


def clearMissing():
    global __missing_family, __missing_genus, __missing_species
    global __multiple_family, __multiple_genus, __multiple_species
    __missing_family=set()
    __missing_genus=set()
    __missing_species=set()
    __multiple_family=set()
    __multiple_genus=set()
    __multiple_species=set()
    
def sortMissing(m1,m2):
    if isinstance(m1, tuple):
        m1=m1[0]
    if isinstance(m2, tuple):
        m2=m2[0]
    return cmp(m1[0],m2[0])
    
def printMissing(out=sys.stderr):
    sf = '%s'
    tf = '   "%s" in %s (%s)'
    if __missing_family:
        print >>out,'Missing Family'
        print >>out,'--------------'
        print >>out
        l = list(__missing_family)
        l.sort()
        for f in l:
            print >> out,'   ',f
        print >>out
    if __multiple_family:
        print >>out,'Multiply defined Family'
        print >>out,'-----------------------'
        print >>out
        l = list(__multiple_family)
        l.sort()
        for f in l:
            print >> out,'   ',f
        print >>out

    if __missing_genus:
        print >>out,'Missing genus'
        print >>out,'-------------'
        print >>out
        l = list(__missing_genus)
        l.sort(sortMissing)
        for f in l:
            if isinstance(f,tuple):
                print >>out,tf % f
            else:
                print >>out,f
        print >>out
    if __multiple_genus:
        print >>out,'Multiply defined genus'
        print >>out,'----------------------'
        print >>out
        l = list(__multiple_genus)
        l.sort(sortMissing)
        for f in l:
            if isinstance(f,tuple):
                print >>out,tf % f
            else:
                print >>out,f
        print >>out

    if __missing_species:
        print >>out,'Missing species'
        print >>out,'---------------'
        print >>out
        l = list(__missing_species)
        l.sort(sortMissing)
        for f in l:
            if isinstance(f,tuple):
                print >>out,tf % f
            else:
                print >>out,f
        print >>out
    if __multiple_species:
        print >>out,'Multiply defined specie'
        print >>out,'----------------------'
        print >>out
        l = list(__multiple_species)
        l.sort(sortMissing)
        for f in l:
            if isinstance(f,tuple):
                print >>out,tf % f
            else:
                print >>out,f
        print >>out

        
        
        
        

    
def tagSequence(seq,restriction=None):
    family    = seq['Family']
    genus = seq['Genus']
    species = '%s %s' % (genus,seq['Species'])
    genus_id=None
    family_id=None

    species_id = lookForTaxon(species, 
                              restriction)
    
    if len(species_id)==1:
        seq['ncbi_scientific_name']=species_id[0][1]
        seq['taxid']=species_id[0][0]
    elif not species_id:
        genus_id = lookForGenus(genus, 
                                restriction)
        if len(genus_id)==1:
            seq['ncbi_genus']=genus_id[0][1]
            genus_id = genus_id[0][0]
            __missing_species.add((species,genus,genus_id))
        else:
            __missing_species.add(species)
            genus_id=None
        species_id=None
    else:
        genus_id = lookForGenus(genus, 
                                restriction)
        if len(genus_id)==1:
            seq['ncbi_genus']=genus_id[0][1]
            genus_id = genus_id[0][0]
            __multiple_species.add((species,genus_id,genus))
        else:
            __multiple_species.add(species)
            genus_id=None
        species_id=None
        
    if species_id is None and genus_id is None:
        genus_id = lookForGenus(genus, 
                                restriction)
        if len(genus_id)==1:
                    seq['ncbi_genus']=genus_id[0][1]
                    genus_id = genus_id[0][0]   
        elif not genus_id:
            family_id = lookForFamily(family, restriction)
            
            if len(family_id)==1:           
                seq['ncbi_family']=family_id[0][1]
                family_id=family_id[0][0]
                __missing_genus.add((genus,family,family_id))
            else:
                __missing_genus.add(genus)
                family_id=None
            genus_id=None
        else:
            family_id = lookForFamily(family, restriction)
            
            if len(family_id)==1:           
                seq['ncbi_family']=family_id[0][1]
                family_id=family_id[0][0]
                __multiple_genus.add((genus,family,family_id))
            else:
                __multiple_genus.add(genus)
            genus_id=None
            
    if family_id is not None and isinstance(family_id, list):
        if not family_id:
            __missing_family.add(family)
        else:
            __multiple_family.add(family)
            
    return seq
        
   
if __name__=='__main__':
    
    optionParser = getOptionManager([addFastaTaxidOptions,
                                     addConnectionOptions],
                                    )
    
    (options, entries) = optionParser()
    
    if options.csv:
        entries = csvEntryIterator(entries)
    else:
        entries = fastaIterator(entries) 
    
    initConnection(options)
    
    clearMissing()
    
    for e in entries:
        print formatFasta(tagSequence(e,restriction=options.restrict))

    printMissing()

        
