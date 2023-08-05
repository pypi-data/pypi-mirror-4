#!/usr/local/bin/python
'''
Created on 2 fevr. 2010

@author: coissac
'''

from obitools.options import getOptionManager
from obitools.format.options import addInputFormatOption
from obitools.ecopcr.options import addTaxonomyDBOptions, loadTaxonomyDatabase
import math

def addStatOptions(optionManager):
    optionManager.add_option('-c','--category-attribute',
                             action="append", dest="categories",
                             metavar="<Attribute Name>",
                             default=[],
                             help="Add one attribute to the list of"
                                  " attribute used for categorizing sequences")
    
    optionManager.add_option('-m','--min',
                             action="append", dest="minimum",
                             metavar="<Attribute Name>",
                             default=[],
                             help="compute minimum of attribute")
    
    optionManager.add_option('-M','--max',
                             action="append", dest="maximum",
                             metavar="<Attribute Name>",
                             default=[],
                             help="compute maximum of attribute")

    optionManager.add_option('-a','--mean',
                             action="append", dest="mean",
                             metavar="<Attribute Name>",
                             default=[],
                             help="compute mean of attribute")

    optionManager.add_option('-v','--variance',
                             action="append", dest="var",
                             metavar="<Attribute Name>",
                             default=[],
                             help="compute the estimator of variance of the attribute")

    optionManager.add_option('-s','--std-dev',
                             action="append", dest="sd",
                             metavar="<Attribute Name>",
                             default=[],
                             help="compute the estimator of standard deviation of attribute")

    
def statistics(values,attribute,func):
    stat={}
    lstat={}
    
    for var in attribute:
        if var in values:
            stat[var]={}
            lstat[var]=0
            for c in values[var]:
                v = values[var][c]
                m = func(v)
                stat[var][c]=m
                lm=len(str(m))
                if lm > lstat[var]:
                    lstat[var]=lm
                
    return stat,lstat

def minimum(values,options):
    return statistics(values, options.minimum, min)
    

def maximum(values,options):
    return statistics(values, options.maximum, max)

def mean(values,options):
    def average(v):
        s = reduce(lambda x,y:x+y,v,0)
        return float(s)/len(v)
    return statistics(values, options.mean, average)


def variance(v):
    s = reduce(lambda x,y:(x[0]+y,x[1]+y**2),v,(0.,0.))
    return s[1]/(len(v)-1) - s[0]**2/len(v)/(len(v)-1)

def varpop(values,options):
    return statistics(values, options.var, variance)
    
def sd(values,options):
    def stddev(v):
        return math.sqrt(variance(v))
    return statistics(values, options.sd, stddev)
    

if __name__ == "__main__":
    optionParser = getOptionManager([addStatOptions,addInputFormatOption,addTaxonomyDBOptions])
    
    (options, entries) = optionParser()
    
    loadTaxonomyDatabase(options)

    options.statistics = set(options.minimum) | set(options.maximum) | set(options.mean)
    total = 0
    catcount={}
    totcount={}
    values={}
    lcat=0
    
    for s in entries:
        category = []
        for c in options.categories:
            try:
                if hasattr(options, 'taxonomy') and options.taxonomy is not None:
                    environ = {'taxonomy' : options.taxonomy,'sequence':s}
                else:
                    environ = {'sequence':s}
        
                v = eval(c,environ,s)
                lv=len(str(v))
                if lv > lcat:
                    lcat=lv
                category.append(v)
            except:
                category.append(None)
                if 4 > lcat:
                    lcat=4
        category=tuple(category)
        catcount[category]=catcount.get(category,0)+1
        try: 
            totcount[category]=totcount.get(category,0)+s['count']
        except KeyError:
            totcount[category]=totcount.get(category,0)+1
        for var in options.statistics:
            if var in s:
                v = s[var]
                if var not in values:
                    values[var]={}
                if category not in values[var]:
                    values[var][category]=[]
                values[var][category].append(v)
                
    
    mini,lmini  = minimum(values, options)
    maxi,lmaxi  = maximum(values, options)
    avg ,lavg   = mean(values, options)
    varp ,lvarp = varpop(values, options)
    sigma,lsigma= sd(values, options)
    
            
    pcat  = "%%-%ds" % lcat
    if options.minimum:
        minvar= "min_%%-%ds" % max(len(x) for x in options.minimum)
    else:
        minvar= "%s"
        
    if options.maximum:
        maxvar= "max_%%-%ds" % max(len(x) for x in options.maximum)
    else:
        maxvar= "%s"
        
    if options.mean:
        meanvar= "mean_%%-%ds" % max(len(x) for x in options.mean)
    else:
        meanvar= "%s"
        
    if options.var:
        varvar= "var_%%-%ds" % max(len(x) for x in options.var)
    else:
        varvar= "%s"
        
    if options.sd:
        sdvar= "sd_%%-%ds" % max(len(x) for x in options.sd)
    else:
        sdvar= "%s"
        
    hcat = "\t".join([pcat % x for x in options.categories]) + "\t" +\
           "\t".join([minvar % x for x in options.minimum])  + "\t" +\
           "\t".join([maxvar % x for x in options.maximum])  + "\t" +\
           "\t".join([meanvar % x for x in options.mean])  + "\t" +\
           "\t".join([varvar % x for x in options.var])  + "\t" +\
           "\t".join([sdvar % x for x in options.sd]) + \
           "\t   count" + \
           "\t   total" 
    print hcat
    for c in catcount:
        for v in c:
            print pcat % str(v)+"\t",
        for m in options.minimum:
            print (("%%%dd" % lmini[m]) % mini[m][c])+"\t",
        for m in options.maximum:
            print (("%%%dd" % lmaxi[m]) % maxi[m][c])+"\t",
        for m in options.mean:
            print (("%%%df" % lavg[m]) % avg[m][c])+"\t",
        for m in options.var:
            print (("%%%df" % lvarp[m]) % varp[m][c])+"\t",
        for m in options.sd:
            print (("%%%df" % lsigma[m]) % sigma[m][c])+"\t",
        print "%7d" %catcount[c],
        print "%9d" %totcount[c]
                    

