#!/usr/local/bin/python

from obitools.options import getOptionManager

from obitools.seqdb.genbank.ncbi import Genbank,Genpep,NCBIAccession
from obitools.seqdb.genbank.parser import genpepIterator,genbankIterator

from obitools.fasta import formatFasta
from obitools.blast import Blast,NetBlast,BlastCovMinFilter
from obitools.parallel import TaskPool

from threading import Lock
from time import sleep

import os
import shelve
import sys
import socket


def addBlasterOptions(optionManager):
    
    optionManager.add_option('-d','--database',
                             action="store", dest="database",
                             metavar="<DB_NAME>",
                             type="string",
                             default='nr',
                             help="name of the queried database (default nr)")

    optionManager.add_option('-i','--input-file',
                             action="store", dest="filename",
                             metavar="<SEQFILE>",
                             type="string",
                             default=None,
                             help="file name containing query sequences")

    optionManager.add_option('-C','--cache',
                             action="store", dest="cache",
                             metavar="<CACHE_NAME>",
                             type="string",
                             default='vaccumblaster',
                             help="prefix of the cache file names")

    optionManager.add_option('-N','--no-cache',
                             action="store", dest="cache",
                             metavar="<CACHE_NAME>",
                             const=None,
                             help="run vaccumblaster without database caching")

    optionManager.add_option('-e','--evalue',
                             action="store", dest="evalue",
                             metavar="#.##",
                             type="float",
                             default=1e-10,
                             help="evalue thresold for blast query")

    optionManager.add_option('-c','--covmin',
                             action="store", dest="covmin",
                             metavar="#.##",
                             type="float",
                             default=0,
                             help="minimal fraction of the query sequence covered by the blast match")

    optionManager.add_option('-v','--result-by-blast',
                             action="store", dest="voption",
                             metavar="#.##",
                             type="int",
                             default=100,
                             help="maximum result count by blast (default 100)")

    optionManager.add_option('-p','--protein-mode',
                             action="store_true", dest="protein",
                             default=False,
                             help="indicate if query are made with blastp")

    optionManager.add_option('-l','--local',
                             action="store_true", dest="local",
                             default=False,
                             help="run blast on local computer")

    optionManager.add_option('-g','--gene',
                             action="store_false", dest="gene",
                             default=True,
                             help="get gene sequence in protein mode")

    optionManager.add_option('-r','--recover',
                             action="store_false", dest="cleancache",
                             default=True,
                             help="run vaccumblaster in recovery mode")



def queryIterator(stack,blastdb,seqdb,protein,evalue,covmin,local,done,v,count=2):

    
    if protein:
        mode = 'blastp'
    else:
        mode = 'blastn'
        
    if local:
        blaster=Blast(mode,blastdb,e=evalue,v=v,b=v)
    else:
        blaster=NetBlast(mode, blastdb,e=evalue,v=v,b=v)
        
    stacklock = Lock()
    
    acdb = NCBIAccession()
        
    def runBlast(seq):
        q = seq.id
        
        run  = blaster(seq)
        good = BlastCovMinFilter(run, covmin, seq)
        acs= set(acdb[set(m['Subject id'] for m in good)])
        print >>sys.stderr,"End query = %s (match count = %d)" % (q,len(acs))
        res = set()
        new = set()
        for s in acs:
            done.setdefault(q,set()).add(s)
            print >>sys.stderr,"==== > Query = %s  Subject = %s" % (q,s),
            stacklock.acquire()
            if s not in done and s not in stack:
                stack.add(s)
                new.add(s)
                print >>sys.stderr,' --> new (queries on stack = %d)' % len(stack)
            else:
                print >>sys.stderr,''
            stacklock.release()
            res.add((s,q))
        print >>sys.stderr,'Query DB for %s' % str(tuple(new))
        seqdb[new]
        return res
            
    def queryIterator():   
        while stack:
            nextid = stack.pop()
            print >>sys.stderr,"Start query = %s (remaining on query stack = %d)" % (nextid,len(stack))
            seq = seqdb[nextid]
            yield[seq]
            while not stack and tasks.queue:
                sleep(0.5)
            
        raise StopIteration
            

    tasks = TaskPool(queryIterator(), runBlast, count)
    
    return tasks
        

if __name__=='__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([addBlasterOptions])
    (options, entries) = optionParser()
    
    socket.setdefaulttimeout(180)
    
    if options.cleancache and options.cache is not None:
        try:
            os.remove("%s.answers.cache" % options.cache)
            os.remove("%s.done.cache" % options.cache)
        except:
            pass
        
    if options.protein:
        if options.filename is not None:
            entries=genpepIterator(options.filename)
        else:
            entries=[]
        if options.cache is not None:
            db = Genpep("%s.genpep.cache" % options.cache)
        else:
            db = Genpep()
        if options.gene:
            if options.cache is not None:
                dbg = Genbank("%s.genbank.cache" % options.cache)
            else:
                dbg = Genbank()
            
    else:
        if options.filename is not None:        
            entries=genbankIterator(options.filename)
        else:
            entries=[]
        if options.cache is not None:
            db = Genbank("%s.genbank.cache" % options.cache)
        else:
            db = Genbank()
        
    if options.cache is not None:
        rep  = shelve.open("%s.answers.cache" % options.cache)
        done = shelve.open("%s.done.cache" % options.cache)
    else:
        rep  = {}
        done = {}
        
    stack = set()
        
    for seq in entries:
        if seq.id not in rep:
            s0 = seq
            s0.extractTaxon()
            s0['query']='initial'
            if options.gene:
                s1 = s0.getCDS(dbg)
                s1['query']='initial'
                print formatFasta(s1)
            else:
                s1=None
                print formatFasta(s0)
            rep[seq.id]=(s0,s1)
            
        if seq.id not in done:
            stack.add(seq.id)

    for id in rep:
        if options.gene:
            if rep[id][1] is not None:
                print formatFasta(rep[id][1])
            else:
                print >>sys.stderr,"I can not retrieve gene from protein %s" % id
        else:
            print formatFasta(rep[id][0])
        if id not in done:
            stack.add(id)
            
    count = 2
    results = queryIterator(stack, options.database, 
                            db, options.protein, 
                            options.evalue, 
                            options.covmin, 
                            options.local, done,
                            options.voption,
                            count)
    
    for bl in results:
        for s,q in bl:
            answer = db[s]
            if answer.id not in rep:
                answer.extractTaxon()
                answer['query']=q
                if options.gene:
                    try:
                        gene = answer.getCDS(dbg)
                        gene['query']=q
                        print formatFasta(gene)
                    except AssertionError:
                        print >>sys.stderr,"I can not retrieve gene from protein %s" % q
                        gene = None
                else:
                    gene=None
                    print formatFasta(answer)
                rep[id]=(answer,gene)
        