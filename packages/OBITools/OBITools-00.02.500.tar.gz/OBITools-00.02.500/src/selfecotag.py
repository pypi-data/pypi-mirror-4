#!/usr/local/bin/python

from obitools.fasta import fastaNucIterator,formatFasta
#from obitools.align.ssearch import ssearchIterator

from obitools.align import lenlcs,ALILEN

from obitools.options.taxonomyfilter import addTaxonomyDBOptions,loadTaxonomyDatabase
from obitools.options import getOptionManager
import sys


def addSearchOptions(optionManager):
            
    optionManager.add_option('-m','--minimum-identity',
                             action="store", dest="minimum",
                             metavar="identity",
                             type="float",
                             default=0.0,
                             help="minimum identity to consider.")
    
    optionManager.add_option('-x','--explain',
                             action='store',dest='explain',
                             type="string",
                             default=None,
                             help="Add in the output CD (complementary data) record "
                                  "to explain identification decision")
    
    optionManager.add_option('--sort',
                             action='store',dest='sort',
                             type='string',
                             default=None,
                             help='Sort output on input sequence tag')

    optionManager.add_option('-E','--errors',
                             action='store',dest='error',
                             default=0.2,
                             help='Tolarated rate of wrong assignation')    


def count(data):
    rep = {}
    for x in data:
        if isinstance(x, (list,tuple)):
            k = x[0]
            if len(x) > 1:
                v = [x[1]]
                default=[]
            else:
                v = 1
                default=0
        else:
            k=x
            v=1
            default=0
        rep[k]=rep.get(k,default)+v
    return rep


def lcsIteratorSelf(entries,db,options):
    
    for seq in entries:
        results = []
        maxid   = ([],0.0)
        minid   = options.minimum
        for d in db:
            if d.id != seq.id:
                lcs,lali = lenlcs(seq,d,minid,normalized=True,reference=ALILEN)
                if lcs > maxid[1]:
                    maxid = ([d],lcs)
                    minid = maxid[1]
                elif lcs==maxid[1]:
                    maxid[0].append(d)
                
        if maxid[0]:
            results.extend([(s,maxid[1]) for s in maxid[0]])
            for d in db:
                for s in maxid[0]:
                    if d.id != s.id:
                        lcs,lali = lenlcs(s,d,maxid[1],normalized=True,reference=ALILEN)      
                        if lcs >= maxid[1]:
                            results.append((d,lcs))
                
        yield seq,maxid,results
        
if __name__=='__main__':
    
    optionParser = getOptionManager([addSearchOptions,addTaxonomyDBOptions],
                                    entryIterator=fastaNucIterator
                                    )
    
    (options, entries) = optionParser()
        
    taxonomy = loadTaxonomyDatabase(options)
    
    print >>sys.stderr,"Reading reference DB ...",
    db = [x for x in entries]
    print >>sys.stderr," : %d" % len(db)
#    print "##########@",options.large
    taxonlink = {}

    rankid = taxonomy.findRankByName(options.explain)
    
    for seq in db:
        id = seq.id[0:46]
        seq.id=id
        assert id not in taxonlink
        taxonlink[id]=int(seq['taxid'])
        
                
    matcher= lcsIteratorSelf

    search = matcher(db,db,options)
                     
                    
    for seq,best,match in search:
        
        drank='--'
        dscname='root'
        dlca=1
        
        if best[0]:
            try:
                taxlist = set(taxonlink[p[0].id] for p in match)
            except Exception,e:
                print match
                raise e
            lca = taxonomy.betterCommonTaxon(options.error,*tuple(taxlist))
            dlca= taxonomy.lastCommonTaxon(lca,seq['taxid'])

            scname = taxonomy.getScientificName(lca)
            rank = taxonomy.getRank(lca)

            dscname = taxonomy.getScientificName(dlca)
            drank=taxonomy.getRank(dlca)
      
            species = taxonomy.getSpecies(lca)
            if species is not None:
                spname = taxonomy.getScientificName(species)
            else:
                spname = '--'
                species= '-1'
      
            genus = taxonomy.getGenus(lca)
            if genus is not None:
                gnname = taxonomy.getScientificName(genus)
            else:
                gnname = '--'
                genus= '-1'
                
            order = taxonomy.getOrder(lca)
            if order is not None:
                orname = taxonomy.getScientificName(order)
            else:
                orname = '--'
                order= '-1'
                
            family = taxonomy.getFamily(lca)
            if family is not None:
                faname = taxonomy.getScientificName(family)
            else:
                faname = '--'
                family= '-1'
                
            worst = min(x[1] for x in match)
    
            data =['ID',seq.id,best[0][0].id,best[1],worst,len(match),lca,scname,rank,order,orname,family,faname,genus,gnname,species,spname]
        else:
            data =['UK',seq.id,'--','--','--',0,1,'root','no rank','-1','--','-1','--','-1','--','-1','--']
            
            
        seq['id_status']=data[0]=='ID'
        seq['match_count']=data[5]
        seq['ntaxid']=data[6]
        seq['scientific_name']=data[7]
        seq['rank']=data[8]
        seq['co_taxid']=dlca
        seq['co_scientific_name']=dscname
        seq['co_rank']=drank
        if seq['id_status']:
            seq['best_match']=data[2]
            seq['best_identity']=data[3]
            seq['worst_identity']=data[4]
            
            if int(data[9])>=0:
                seq['order']=data[9]
                seq['order_name']=data[10]
            if int(data[11])>=0:
                seq['family']=data[11]
                seq['family_name']=data[12]
            if int(data[13])>=0:
                seq['genus']=data[13]
                seq['genus_name']=data[14]
            if int(data[15])>=0:
                seq['species']=data[15]
                seq['species_name']=data[16]
            if options.explain is not None:
                seq['explain']=dict((s[0].id,s[1]) for s in match)
        print formatFasta(seq)        
                
                
                
