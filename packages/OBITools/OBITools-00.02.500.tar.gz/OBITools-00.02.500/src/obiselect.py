#!/usr/local/bin/python
"""
:py:mod:`obiselect` : Select and print sequences identified by a list of IDs 
============================================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obiselect` command allows to select a set of sequences
Example:

.. code-block:: bash

   > obiselect ...


"""
from obitools.format.options import addInOutputOption, sequenceWriterGenerator,\
    addInputFormatOption
from obitools.options import getOptionManager
from obitools.ecopcr.options import addTaxonomyDBOptions, loadTaxonomyDatabase
from random import random
import math

def minimum(seqs):
    return min(s['select'] for s in seqs)

def maximum(seqs):
    return max(s['select'] for s in seqs)

def mean(seqs):
    ss= reduce(lambda x,y: x + y,(s['select'] for s in seqs),0)
    return float(ss) / len(seqs)

def median(seqs):
    ss = [s['select'] for s in seqs]
    ss.sort()
    return ss[len(ss)/2]

    

def addSelectOptions(optionManager):
    
    optionManager.add_option('-c','--category-attribute',
                             action="append", dest="categories",
                             metavar="<Attribute Name>",
                             default=[],
                             help="Add one attribute to the list of"
                                  " attribute used for categorizing sequences")

    optionManager.add_option('-n','--number',
                             action="store", dest="number",
                             metavar="",
                             type="int",
                             default=1,
                             help="select sequence in each group minimizing the function")

    optionManager.add_option('-f','--function',
                             action="store", dest="function",
                             metavar="",
                             default="random",
                             help="select sequence in each group minimizing the function")

   
    optionManager.add_option('-m','--min',
                             action="store_const", dest="method",
                             metavar="",
                             default=maximum,
                             const=minimum,
                             help="select sequence in each group minimizing the function")
    
    optionManager.add_option('-M','--max',
                             action="store_const", dest="method",
                             metavar="<Attribute Name>",
                             default=maximum,
                             const=maximum,
                             help="select sequence in each group maximizing the function")

    optionManager.add_option('-a','--mean',
                             action="store_const", dest="method",
                             metavar="<Attribute Name>",
                             default=maximum,
                             const=mean,
                             help="select sequence in each group closest to the mean of the function")


    optionManager.add_option('--median',
                             action="store_const", dest="method",
                             metavar="<Attribute Name>",
                             default=maximum,
                             const=median,
                             help="select sequence in each group closest to the median of the function")

    optionManager.add_option('--merge',
                             action="append", dest="merge",
                             metavar="<TAG NAME>",
                             type="string",
                             default=[],
                             help="attributes to merge")

    optionManager.add_option('--merge-ids',
                             action="store_true", dest="mergeids",
                             default=False,
                             help="add the merged id data to output")
    


def sortclass(seqs,options):
    cible = float(options.method(seqs))
    for s in seqs:
        s['distance']=math.sqrt((float(s['select'])-cible)**2)
    seqs.sort(lambda s1,s2 : cmp(s1['distance'],s2['distance']))
                                                


if __name__ == '__main__':
    
    optionParser = getOptionManager([addSelectOptions,addInOutputOption,addTaxonomyDBOptions])
    
    (options, entries) = optionParser()
    
    taxonomy=loadTaxonomyDatabase(options)

    writer = sequenceWriterGenerator(options)
    
    classes = {}
    
    for s in entries:
        category = []
        for c in options.categories:
            try:
                if hasattr(options, 'taxonomy') and options.taxonomy is not None:
                    environ = {'taxonomy' : options.taxonomy,'sequence':s,'random':random()}
                else:
                    environ = {'sequence':s,'random':random()}
        
                v = eval(c,environ,s)
                category.append(v)
            except:
                category.append(None)

        category=tuple(category)
        group = classes.get(category,[])
        group.append(s)
        classes[category]= group
            
        if hasattr(options, 'taxonomy') and options.taxonomy is not None:
            environ = {'taxonomy' : options.taxonomy,'sequence':s,'random':random()}
        else:
            environ = {'sequence':s}

        try:    
            select =  eval(options.function,environ,s)
            s['select']=select
        except:
            s['select']=None
 
    mergedKey = options.merge
    mergeIds = options.mergeids 
          
    if mergedKey is not None:
        mergedKey=set(mergedKey)
    else:
        mergedKey=set() 
    
    if taxonomy is not None:
        mergedKey.add('taxid')
                
    
    for c in classes:
        seqs = classes[c]
        sortclass(seqs, options)
        if len(c)==1:
            c=c[0]
            
        if options.number==1:
            s = seqs[0]
            
            for key in mergedKey:
                if key=='taxid' and mergeIds:
                    if 'taxid_dist' not in s:
                        s["taxid_dist"]={}
                    if 'taxid' in s:
                        s["taxid_dist"][s.id]=s['taxid']
                mkey = "merged_%s" % key 
                if mkey not in s:
                    s[mkey]={}
                if key in s:
                    s[mkey][s[key]]=s[mkey].get(s[key],0)+1
                    del(s[key])

            if 'count' not in s:
                s['count']=1
            if mergeIds:        
                s['merged']=[s.id]

            for seq in seqs[1:]:
                
                s['count']+=seq['count']
                
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
 
        if taxonomy is not None:
            mergeTaxonomyClassification(seqs, taxonomy)
                    

        
        
        
        
        
        for s in seqs[0:options.number]:
            s['class']=c
            writer(s)