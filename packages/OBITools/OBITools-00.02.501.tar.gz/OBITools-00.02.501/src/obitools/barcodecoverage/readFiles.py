#!/usr/local/bin/python
'''
Created on 23 nov. 2011

@author: merciece
'''

from obitools.ecopcr import sequence
from obitools.ecopcr import taxonomy


def main(entries,options):
    filteredDataFromDB = ecoPCRDatabaseReader(options)
    filteredData = ecoPCRFileReader(entries,filteredDataFromDB)
    return filteredDataFromDB,filteredData


def ecoPCRDatabaseReader(options):
    
    tax = taxonomy.EcoTaxonomyDB(options.taxonomy)
    seqs = sequence.EcoPCRDBSequenceIterator(options.taxonomy,taxonomy=tax)
       
    norankid  = tax.findRankByName('no rank')
    speciesid = tax.findRankByName('species')
    genusid   = tax.findRankByName('genus')
    familyid  = tax.findRankByName('family')
    
    minrankseq = set([speciesid,genusid,familyid])
    
    usedrankid   = {}
    
    ingroup = {}
    outgroup= {}
        
    for s in seqs :
        if 'taxid' in s :
            taxid = s['taxid']
            allrank = set()
            for p in tax.parentalTreeIterator(taxid):
                if p[1]!=norankid:
                    allrank.add(p[1])
                if len(minrankseq & allrank) == 3:
                    for r in allrank:
                        usedrankid[r]=usedrankid.get(r,0) + 1
                    
                    if tax.isAncestor(options.ingroup,taxid):
                        ingroup[s.id] = s
                    else:
                        outgroup[s.id] = s
                        
    keptranks = set(r for r in usedrankid 
                   if float(usedrankid[r])/float(len(ingroup)) > options.rankthresold)
                        
    return { 'ingroup' : ingroup,
             'outgroup': outgroup,
             'ranks'   : keptranks,
             'taxonomy': tax
           }


def ecoPCRFileReader(entries,filteredDataFromDB) :
    filteredData = []
    for s in entries :
        if 'taxid' in s :
            seqId = s.id
            if seqId in filteredDataFromDB['ingroup'] :
                filteredData.append(s)
    return filteredData

