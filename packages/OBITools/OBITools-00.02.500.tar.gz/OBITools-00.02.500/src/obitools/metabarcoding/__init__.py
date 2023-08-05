from obitools.ecopcr.options import addTaxonomyFilterOptions,\
                                    loadTaxonomyDatabase
from obitools.graph import UndirectedGraph
from obitools.align import lenlcs,isLCSReachable
from obitools.graph.algorithms.component import componentIterator
from obitools.utils.bioseq import uniqSequence
from obitools.utils import progressBar
import math
import sys
from obitools.graph.rootedtree import RootedTree

def average(x):
    x=list(x)
    s = sum(i*j for (i,j) in x)
    n = sum(i[1] for i in x)
    return (float(s)/float(n),n)

def minimum(x):
    x=list(x)
    m = min(i[0] for i in x)
    n = sum(i[1] for i in x)
    return (float(m),n)

def ecoPCRReader(entries,options):
    '''
    
    :param entries: an iterator over the entries to analyze
    :type entries: an iterable element
    :param options: the option structure return by the option manager
    :type options: object
    '''
    
    taxonomy = loadTaxonomyDatabase(options) 
       
    norankid =options.taxonomy.findRankByName('no rank')
    speciesid=options.taxonomy.findRankByName('species')
    genusid  =options.taxonomy.findRankByName('genus')
    familyid =options.taxonomy.findRankByName('family')
    
    
    #
    # to be used a sequence must have at least 
    # a species a genus and a family
    #
    
    minrankseq = set([speciesid,genusid,familyid])
    
    usedrankid   = {}
    
    ingroup = []
    outgroup= []
    
    totalentries     = 0
    entrieswithtaxid = 0
    goodtaxid        = 0
    
    for s in entries:
        totalentries+=1
        if 'taxid' in s :
            entrieswithtaxid+=1
            taxid = s['taxid']
            if taxid in taxonomy:
                goodtaxid+=1
                allrank = set()
                for p in options.taxonomy.parentalTreeIterator(taxid):
                    if p[1]!=norankid:
                        allrank.add(p[1])
                if len(minrankseq & allrank) == 3:
                    if taxonomy.isAncestor(options.ingroup,taxid):
                        for r in allrank:
                            usedrankid[r]=usedrankid.get(r,0) + 1
                        ingroup.append(s)
                    else:
                        outgroup.append(s)
                        
    keptrank = set(r for r in usedrankid 
                   if float(usedrankid[r])/float(len(ingroup)) > options.rankthresold)
                        
    return { 'ingroup' : ingroup,   # The group of interest
             'outgroup': outgroup,  # all other taxa
             'ranks'   : keptrank   # the rank to analyzed (more frequent than  options.rankthresold
           }
                
def buildSimilarityGraph(dbseq,ranks,taxonomy,dcmax=5):
    
    ldbseq = len(dbseq)
    pos = 1
    digit = int(math.ceil(math.log10(ldbseq)))
    header = "Alignment  : %%0%dd x %%0%dd -> %%0%dd " % (digit,digit,digit)
    aligncount = ldbseq*(ldbseq+1)/2
    edgecount = 0
    print >>sys.stderr

    progressBar(1,aligncount,True,"Alignment  : %s x %s -> %s " % ('-'*digit,'-'*digit, '0'*digit))
    
        
    sim = UndirectedGraph()
    
    i=0
    for s in dbseq:
        taxid = s['taxid']
        
        rtaxon = dict((rid,taxonomy.getTaxonAtRank(taxid,rid))
                      for rid in ranks)
        
        sim.addNode(i, seq=s,taxid=taxid,rtaxon=rtaxon) 
        
        i+=1

#    aligner = LCS()
        
    for is1 in xrange(ldbseq):
        s1 = dbseq[is1]
        ls1= len(s1)
#        aligner.seqA=s1
        
        for is2 in xrange(is1+1,ldbseq):

            s2=dbseq[is2]
            ls2=len(s2)
            
            lm = max(ls1,ls2)
            lcsmin = lm - dcmax
            
            if isLCSReachable(s1,s2,lcsmin):
                llcs,lali=lenlcs(s1,s2)
                ds1s2 = lali - llcs
                
                if ds1s2 <= dcmax:
                    sim.addEdge(node1=is1, node2=is2,ds1s2=ds1s2,label=ds1s2)
                    edgecount+=1
                    
        progressBar(pos,aligncount,head=header % (is1,is2,edgecount))
        pos+=(ldbseq-is1-1)
        
    return sim
            
def buildTsr(component):
    '''
    Build for each consider taxonomic rank the list of taxa
    present in the connected component
    
    :param component: the analyzed connected component
    :type component: :py:class:`UndirectedGraph`
    
    :return: a dictionary indexed by rankid containing a `dict` indexed by taxid and containing count of sequences for this taxid
    :rtype: `dict` indexed by `int` containing `dict` indexed by `int` and containing of `int`
     
    '''
    taxalist = {}
    for n in component:
        for r in n['rtaxon']:
            rtaxid = n['rtaxon'][r]
            if rtaxid is not None:
                ts =  taxalist.get(r,{})
                ts[rtaxid]=ts.get(rtaxid,0)+1
                taxalist[r]=ts
        
    return taxalist
    
def edgeDistSelector(dcmax):
    def predicate(e):
        return e['ds1s2'] <= dcmax
    return predicate

def distanceOfConfusion(simgraph,dcmax=5,aggregate=average):
    
    alltaxa = set()
    
    for n in simgraph:
        alltaxa|=set(n['rtaxon'].values())
        
    taxacount = len(alltaxa)
    
    result = {}

    pos = [1]
    header = "Component  : %-5d Identified : %-8d "
    progressBar(1,taxacount,True,header % (0,0))
       
    def _idc(cc,dcmax):
        composante=[]
        for x in cc:
            composante.extend(simgraph.subgraph(c)
                              for c in componentIterator(x, 
                                                         edgePredicat=edgeDistSelector(dcmax)))

        good = set()
        bad  = {}
        
        complexe = []
        
        for c in composante:       
            tsr = buildTsr(c)
            newbad=False
            for r in tsr:
                if len(tsr[r]) == 1:
                    taxid = tsr[r].keys()[0]
                    good.add((taxid,tsr[r][taxid]))
                else:
                    newbad=True
                    for taxid in tsr[r]:
                        bad[taxid]=bad.get(taxid,0)+tsr[r][taxid]
            if newbad:
                complexe.append(c)
                                        
#       good = good - bad
            
        for taxid,weight in good:
            if taxid not in result:
                result[taxid]=[]
            result[taxid].append((dcmax+1,weight))
            

            progressBar(pos[0],taxacount,False,header % (len(composante),pos[0]))
            pos[0]=len(result)
                
        if dcmax > 0:
            dcmax-=1
            _idc(complexe,dcmax)
            
        else:
            for taxid in bad:
                if taxid not in result:
                    result[taxid]=[]
                result[taxid].append((0,bad[taxid]))                

                progressBar(pos[0],taxacount,False,header % (len(composante),pos[0]))
                pos[0]=len(result)
                
    _idc([simgraph],dcmax)
    
    for taxid in result:
        result[taxid]=aggregate(result[taxid])
    return result

def propagateDc(tree,node=None,aggregate=min):
    if node is None:
        node = tree.getRoots()[0]
    dca=aggregate(n['dc'] for n in node.leavesIterator())
    node['dc']=dca
    for n in node:
        propagateDc(tree, n, aggregate)

def confusionTree(distances,ranks,taxonomy,aggregate=min,bsrank='species',dcmax=1):
    '''
    
    :param distances:
    :type distances:
    :param ranks:
    :type ranks:
    :param taxonomy:
    :type taxonomy:
    :param aggregate:
    :type aggregate:
    :param bsrank:
    :type bsrank:
    :param dcmax:
    :type dcmax:
    
    
    '''
    
    def Bs(node,rank,dcmax):
        n = len(node)
        if n:
            g = [int(x['dc']>=dcmax) for x in node.subgraphIterator() if x['rank']==bsrank]
            n = len(g)
            g = sum(g)
            bs= float(g)/float(n)
            node['bs']=bs
            node['bs_label']="%3.2f (%d)" % (bs,n)
            
            for n in node:
                Bs(n,rank,dcmax)
                
    tree = RootedTree()
    ranks = set(ranks)
    tset = set(distances)
    
    for taxon in distances:
        tree.addNode(taxon, rank=taxonomy.getRank(taxon),
                       name=taxonomy.getScientificName(taxon),
                       dc=float(distances[taxon][0]),
                       n=distances[taxon][1],
                       dc_label="%4.2f (%d)" % (float(distances[taxon][0]),distances[taxon][1])
                    )

    for taxon in distances:
        piter = taxonomy.parentalTreeIterator(taxon)
        taxon = piter.next()
        for parent in piter:
            if taxon[0] in tset and parent[0] in distances:
                tset.remove(taxon[0])
                tree.addEdge(parent[0], taxon[0])
                taxon=parent
                
    root = tree.getRoots()[0]
    Bs(root,bsrank,dcmax)
    
    return tree
