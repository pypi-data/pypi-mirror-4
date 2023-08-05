def mergeTaxonomyClassification(uniqSeq,taxonomy):
    for seq in uniqSeq:
        if seq['merged_taxid']:
            seq['taxid']=taxonomy.lastCommonTaxon(*seq['merged_taxid'].keys())
            tsp = taxonomy.getSpecies(seq['taxid'])
            tgn = taxonomy.getGenus(seq['taxid'])
            tfa = taxonomy.getFamily(seq['taxid'])
            
            if tsp is not None:
                sp_sn = taxonomy.getScientificName(tsp)
            else:
                sp_sn="###"
                tsp=-1
                
            if tgn is not None:
                gn_sn = taxonomy.getScientificName(tgn)
            else:
                gn_sn="###"
                tgn=-1
                
            if tfa is not None:
                fa_sn = taxonomy.getScientificName(tfa)
            else:
                fa_sn="###"
                tfa=-1
                
            seq['species']=tsp
            seq['genus']=tgn
            seq['family']=tfa
                
            seq['species_sn']=sp_sn
            seq['genus_sn']=gn_sn
            seq['family_sn']=fa_sn
            
            seq['rank']=taxonomy.getRank(seq['taxid'])
            seq['scientific_name']=fa_sn = taxonomy.getScientificName(seq['taxid'])

def uniqSequence(seqIterator,taxonomy=None,mergedKey=None,mergeIds=False,categories=None):
    uniques={}
    uniqSeq=[]
     
    if categories is None:
        categories=[]
    
    if mergedKey is not None:
        mergedKey=set(mergedKey)
    else:
        mergedKey=set() 
    
    if taxonomy is not None:
        mergedKey.add('taxid')
                
    for seq in seqIterator:    
        s = tuple(seq[x] for x in categories) + (str(seq),)
        if s in uniques:
            s = uniques[s]
            if 'count' in seq:
                s['count']+=seq['count']
            else:
                s['count']+=1
#            if taxonomy is not None and 'taxid' in seq:
#                s['merged_taxid'][seq['taxid']]=
            for key in mergedKey:
                if key=='taxid' and mergeIds:
                    if 'taxid_dist' in seq:
                        s["taxid_dist"].update(seq["taxid_dist"])
                    if 'taxid' in seq:
                        s["taxid_dist"][seq.id]=seq['taxid']
                        
                mkey = "merged_%s" % key 
                if key in seq:
                    s[mkey][seq[key]]=s[mkey].get(seq[key],0)+1
                if mkey in seq:
                    for skey in seq[mkey]:
                        if skey in s:
                            s[mkey][skey]=s[mkey].get(seq[skey],0)+seq[mkey][skey]
                        else:
                            s[mkey][skey]=seq[mkey][skey]
                            
            for key in seq.iterkeys():
                # Merger proprement l'attribut merged s'il exist
                if key in s and s[key]!=seq[key] and key!='count' and key[0:7]!='merged_' and key!='merged':
                    del(s[key])
                
                            
            if mergeIds:        
                s['merged'].append(seq.id)
        else:
            uniques[s]=seq
            for key in mergedKey:
                if key=='taxid' and mergeIds:
                    if 'taxid_dist' not in seq:
                        seq["taxid_dist"]={}
                    if 'taxid' in seq:
                        seq["taxid_dist"][seq.id]=seq['taxid']
                mkey = "merged_%s" % key 
                if mkey not in seq:
                    seq[mkey]={}
                if key in seq:
                    seq[mkey][seq[key]]=seq[mkey].get(seq[key],0)+1
                    del(seq[key])

            if 'count' not in seq:
                seq['count']=1
            if mergeIds:        
                seq['merged']=[seq.id]
            uniqSeq.append(seq)

    if taxonomy is not None:
        mergeTaxonomyClassification(uniqSeq, taxonomy)
                    
                     

    return uniqSeq

def uniqPrefixSequence(seqIterator,taxonomy=None,mergedKey=None,mergeIds=False,categories=None):

    if categories is None:
        categories=[]
    
    def cmpseq(s1,s2):
        return cmp(str(s1),str(s2))

    if mergedKey is not None:
        mergedKey=set(mergedKey)
    else:
        mergedKey=set() 
    
    if taxonomy is not None:
        mergedKey.add('taxid')
                
    sequences=list(seqIterator)

    if not sequences:
        return []
    
    sequences.sort(cmpseq)
    
    
    old=sequences.pop()
    uniqSeq=[old]
    if 'count' not in old:
        old['count']=1
    for key in mergedKey:
        mkey = "merged_%s" % key 
        if mkey not in old:
            old[mkey]={}
        if key in old:
            old[mkey][old[key]]=old[mkey].get(old[key],0)+1
    if mergeIds:        
        old['merged']=[old.id]

     
    while(sequences):
        seq=sequences.pop()
        lseq=len(seq)
        pold = str(old)[0:lseq]
        if pold==str(seq):
            
            if 'count' in seq:
                old['count']+=seq['count']
            else:
                old['count']+=1
                
            for key in mergedKey:
                mkey = "merged_%s" % key 
                if key in seq:
                    old[mkey][seq[key]]=old[mkey].get(seq[key],0)+1
                if mkey in seq:
                    for skey in seq[mkey]:
                        if skey in old:
                            old[mkey][skey]=old[mkey].get(seq[skey],0)+seq[mkey][skey]
                        else:
                            old[mkey][skey]=seq[mkey][skey]

            for key in seq.iterkeys():
                if key in old and old[key]!=seq[key]:
                    del(old[key])
                

            if mergeIds:        
                old['merged'].append(seq.id)
        else:
            old=seq
            
            for key in mergedKey:
                mkey = "merged_%s" % key 
                if mkey not in seq:
                    seq[mkey]={}
                if key in seq:
                    seq[mkey][seq[key]]=seq[mkey].get(seq[key],0)+1
                    del(seq[key])

            if 'count' not in seq:
                seq['count']=1
            if mergeIds:        
                seq['merged']=[seq.id]
            uniqSeq.append(seq)
            
    if taxonomy is not None:
        mergeTaxonomyClassification(uniqSeq, taxonomy)

    return uniqSeq
           
    
    

def _cmpOnKeyGenerator(key,reverse=False):
    def compare(x,y):
        try:
            c1 = x[key]
        except KeyError:
            c1=None
            
        try:
            c2 = y[key]
        except KeyError:
            c2=None
            
        if reverse:
            s=c1
            c1=c2
            c2=s
        return cmp(c1,c2)
    
    return compare

def sortSequence(seqIterator,key,reverse=False):
    seqs = list(seqIterator)
    seqs.sort(_cmpOnKeyGenerator(key, reverse))
    return seqs
    