#!/usr/local/bin/python
'''
Created on 24 nov. 2011

@author: merciece
'''


def main(amplifiedSeqs, seqsFromDB, keptRanks, errors, tax) :
    '''
    error threshold is set to 3 
    '''   
    
    listtaxabygroupinDB = {}
    
    for seq in seqsFromDB :
        taxid = seq['taxid']
        p = [a for a in tax.parentalTreeIterator(taxid)]
        for a in p :
            if a != p[0] :
                if a[1] in keptRanks :
                    group = a[0]
                    if group in listtaxabygroupinDB and taxid not in listtaxabygroupinDB[group] :
                        listtaxabygroupinDB[group].add(taxid)
                    elif group not in listtaxabygroupinDB :
                        listtaxabygroupinDB[group]=set([taxid])
                            
    taxabygroup = dict((x,len(listtaxabygroupinDB[x])) for x in listtaxabygroupinDB)
    
    listamplifiedtaxabygroup = {}

    for seq in amplifiedSeqs :
        if errors[seq.id][2] <= 3 :
            taxid = seq['taxid']   
            p = [a for a in tax.parentalTreeIterator(taxid)]
            for a in p :
                if a != p[0] :
                    if a[1] in keptRanks :
                        group = a[0]
                        if group in listamplifiedtaxabygroup and taxid not in listamplifiedtaxabygroup[group] :
                            listamplifiedtaxabygroup[group].add(taxid)
                        elif group not in listamplifiedtaxabygroup :
                            listamplifiedtaxabygroup[group]=set([taxid])

    amplifiedtaxabygroup = dict((x,len(listamplifiedtaxabygroup[x])) for x in listamplifiedtaxabygroup)
    
    BcValues = {}
        
    groups = [g for g in taxabygroup.keys()]
        
    for g in groups :
        if g in amplifiedtaxabygroup :
            BcValues[g] = float(amplifiedtaxabygroup[g])/taxabygroup[g]*100
            BcValues[g] = round(BcValues[g], 2)
        else :
            BcValues[g] = 0.0
    
    return BcValues




