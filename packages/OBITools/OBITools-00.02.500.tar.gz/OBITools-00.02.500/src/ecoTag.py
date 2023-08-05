#!/usr/local/bin/python

from obitools.fasta import fastaNucIterator,formatFasta
#from obitools.align.ssearch import ssearchIterator
from obitools.utils.bioseq import uniqSequence,sortSequence

from obitools.align import lenlcs,ALILEN

from obitools.options.taxonomyfilter import addTaxonomyDBOptions,loadTaxonomyDatabase
from obitools.ecobarcode.databases import referenceDBIterator
from obitools.options import getOptionManager
from obitools.ecobarcode.rawdata import sequenceIterator
import sys
from obitools.ecobarcode.ecotag import storeIdentification


def addSearchOptions(optionManager):
    
    optionManager.add_option('-R','--ref-database',
                             action="store", dest="database",
                             metavar="<FILENAME>",
                             type="string",
                             help="fasta file containing reference"
                                  "sequences")
        
    optionManager.add_option('-s','--shape',
                             action="store", dest="shape",
                             metavar="shapeness",
                             type="float",
                             default=2.0,
                             help="selectivity on the ssearch results "
                                  "1.0 is the higher selectivity."
                                  "value > 1.0 decrease selectivity.")
    
    optionManager.add_option('-m','--minimum-identity',
                             action="store", dest="minimum",
                             metavar="identity",
                             type="float",
                             default=0.0,
                             help="minimum identity to consider.")
    
    optionManager.add_option('-S','--normalized-smallest',
                             action="store_false", dest="large",
                             default=True,
                             help="normalize identity over the shortest sequence")
    
    optionManager.add_option('-L','--normalized-largest',
                             action="store_true", dest="large",
                             default=True,
                             help="normalize identity over the longest sequence")
    
    optionManager.add_option('-x','--explain',
                             action='store',dest='explain',
                             type="string",
                             default=None,
                             help="Add in the output CD (complementary data) record "
                                  "to explain identification decision")
    
    optionManager.add_option('-u','--uniq',
                             action='store_true',dest='uniq',
                             default=False,
                             help='Apply uniq filter on sequences before identification')
    
    optionManager.add_option('-T','--table',
                             action='store_true',dest='table',
                             default=False,
                             help='Write results in a tabular format')
    
    optionManager.add_option('--store-in-db',
                             action='store_true',dest='storeindb',
                             default=False,
                             help='Write results in an ecobarcode DB')
    
    optionManager.add_option('--update-db',
                             action='store_true',dest='updatedb',
                             default=False,
                             help='Run identification only on new sequences')
    
    optionManager.add_option('--sort',
                             action='store',dest='sort',
                             type='string',
                             default=None,
                             help='Sort output on input sequence tag')
    
    optionManager.add_option('-r','--reverse',
                             action='store_true',dest='reverse',
                             default=False,
                             help='Sort in reverse order (should be used with -S)')
    
    optionManager.add_option('-o','--output-sequence',
                             action='store_true',dest='sequence',
                             default=False,
                             help='Add an extra column in the output with the query sequence')
    
    optionManager.add_option('--self-matches',
                             action='store_true',dest='selfmatches',
                             default=False,
                             help='Switch to the new match algorithm')    

    optionManager.add_option('-E','--errors',
                             action='store',dest='error',
                             default=0.0,
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

def lcsIterator(entries,db,options):
    
    for seq in entries:
        results = []
        maxid   = (None,0.0)
        minid   = options.minimum
        for d in db:
            lcs,lali = lenlcs(seq,d,minid,normalized=True,reference=ALILEN)
            if lcs > maxid[1]:
                maxid = (d,lcs)
                minid = maxid[1] ** options.shape
            results.append((d,lcs))
        minid = maxid[1] ** options.shape
        results = [x for x in results if x[1]>=minid]
        yield seq,([maxid[0]],maxid[1]),results


def lcsIteratorSelf(entries,db,options):
    
    for seq in entries:
        results = []
        maxid   = ([],0.0)
        minid   = options.minimum
        for d in db:
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
        
    if options.explain is not None:
        options.table=True
        

    taxonomy = loadTaxonomyDatabase(options)
    
    print >>sys.stderr,"Reading reference DB ...",
    if (hasattr(options, 'ecobarcodedb') and options.ecobarcodedb is not None):
        try:
            db = list(fastaNucIterator(options.database))
        except IOError:
            db = list(referenceDBIterator(options))  
        if options.primer is not None:
            entries = sequenceIterator(options)  
    else:
        db = list(fastaNucIterator(options.database))
    print >>sys.stderr," : %d" % len(db)
#    print "##########@",options.large
    taxonlink = {}

    rankid = taxonomy.findRankByName(options.explain)
    
    for seq in db:
        id = seq.id[0:46]
        seq.id=id
        assert id not in taxonlink
        taxonlink[id]=int(seq['taxid'])
        
                
    if options.uniq:
        entries = uniqSequence(entries)
        
    if options.sort is not None:
        entries = sortSequence(entries, options.sort, options.reverse)

    matcher = lcsIterator
    
    if options.selfmatches:
        matcher= lcsIteratorSelf

    search = matcher(entries,db,options)
                     
                    
    for seq,best,match in search:
        try:
            seqcount = seq['count']
        except KeyError:
            seqcount=1

        if best[0] is not None:
            taxlist = set(taxonlink[p[0].id] for p in match)
            lca = taxonomy.betterCommonTaxon(options.error,*tuple(taxlist))
            scname = taxonomy.getScientificName(lca)
            rank = taxonomy.getRank(lca)
            if len(taxlist) < 15:
                species_list = set(taxonomy.getSpecies(t) for t in taxlist)
                species_list = [taxonomy.getScientificName(t) for t in species_list if t is not None]
            else:
                species_list = []
                
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
    
            data =['ID',seq.id,best[0][0].id,best[1],worst,'%4.3f' %(best[1]**options.shape),seqcount,len(match),lca,scname,rank,order,orname,family,faname,genus,gnname,species,spname]
        else:
            data =['UK',seq.id,'--','--','--','--',seqcount,0,1,'root','no rank','-1','--','-1','--','-1','--','-1','--']
            
        if options.sequence:
            data.append(seq)
            
        if options.table:
            print '\t'.join([str(x) for x in data])
            if match and rankid is not None:
                splist=count((taxonomy.getTaxonAtRank(x, rankid),y) 
                             for x,y in ((taxonlink[p[0].id],p[1]) for p in match))
                if None in splist:
                    del splist[None]
                data=[]
                for taxon in splist:
                    scname = taxonomy.getScientificName(taxon)
                    species=taxonomy.getSpecies(taxon)
                    countt = len(splist[taxon])
                    mini = min(splist[taxon])
                    maxi = max(splist[taxon])
                    if species is not None:
                        spname = taxonomy.getScientificName(species)
                    else:
                        spname = '--'
                        species= '-1'
              
                    genus = taxonomy.getGenus(taxon)
                    if genus is not None:
                        gnname = taxonomy.getScientificName(genus)
                    else:
                        gnname = '--'
                        genus= '-1'
                        
                    order = taxonomy.getOrder(taxon)
                    if order is not None:
                        orname = taxonomy.getScientificName(order)
                    else:
                        orname = '--'
                        order= '-1'
                        
                    family = taxonomy.getFamily(taxon)
                    if family is not None:
                        faname = taxonomy.getScientificName(family)
                    else:
                        faname = '--'
                        family= '-1'
    
    
                    data.append(['CD',seq.id,'--',maxi,mini,'--','--',countt,taxon,scname,options.explain,order,orname,family,faname,genus,gnname,species,spname])
                data.sort(lambda x,y:cmp(y[2], x[2]))    
                for d in data:
                    if options.sequence:
                        d.append('--')
                    print '\t'.join([str(x) for x in d])

        elif options.storeindb:
            storeIdentification(seq.id,data[0]=='ID',data[8],
                                dict((s[0]['refdbid'],s[1]) for s in match),
                                options)
        else:
            seq['id_status']=data[0]=='ID'
            seq['count']=data[6]
            seq['match_count']=data[7]
            seq['taxid']=data[8]
            seq['scientific_name']=data[9]
            seq['rank']=data[10]
            if seq['id_status']:
                seq['best_match']=data[2]
                seq['best_identity']=data[3]
                seq['worst_identity']=data[4]
                seq['lower_id_limit']=float(data[5])
                if int(data[11])>=0:
                    seq['order']=data[11]
                    seq['order_name']=data[12]
                if int(data[13])>=0:
                    seq['family']=data[13]
                    seq['family_name']=data[14]
                if int(data[15])>=0:
                    seq['genus']=data[15]
                    seq['genus_name']=data[16]
                if int(data[17])>=0:
                    seq['species']=data[17]
                    seq['species_name']=data[18]
                if options.explain is not None:
                    seq['explain']=dict((s[0].id,s[1]) for s in match)
                seq['species_list']=species_list
            print formatFasta(seq)        
                
        
                
    if (hasattr(options, 'ecobarcodedb') and options.ecobarcodedb is not None):
        options.ecobarcodedb.commit()
        options.ecobarcodedb.close()
        
                
