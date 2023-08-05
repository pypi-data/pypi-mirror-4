'''
Created on 9 juin 2012

@author: coissac
'''
from esm import Index
from obitools.format.options import addInOutputOption, sequenceWriterGenerator,\
    autoEntriesIterator
from obitools.fastq import formatFastq
from obitools.options import getOptionManager
from obitools.options._options import allEntryIterator
from obitools.utils import progressBar
from itertools import chain
import sys
import shelve
import os

import sqlite3
 
def addWindowsOptions(optionManager):
    
    optionManager.add_option('-l','--window-length',
                             action="store", dest="length",
                             metavar="<WORD SIZE>",
                             type="int",
                             default=90,
                             help="size of the sliding window")

    optionManager.add_option('-s','--step',
                             action="store", dest="step",
                             metavar="<STEP>",
                             type="int",
                             default=1,
                             help="position difference between two windows")
    
    optionManager.add_option('-c','--circular',
                             action="store_true", dest="circular",
                             default=False,
                             help="set for circular sequence")

    optionManager.add_option('-r','--reverse-reads',
                             action="store", dest="reverse",
                             metavar="<FILENAME>",
                             type="str",
                             default=None,
                             help="Filename containing reverse solexa reads "
                            )
    
    optionManager.add_option('-i','--index',
                             action="store", dest="index",
                             metavar="<INDEX>",
                             type="str",
                             default=None,
                             help="Name of the indexed database"
                            )

def cutDirectReverse(entries):
    first = []
    
    for i in xrange(10):
        first.append(entries.next())
        
    lens = [len(x) for x in first]
    clen = {}
    for i in lens:
        clen[i]=clen.get(i,0)+1
    freq = max(clen.values())
    freq = [k for k in clen if clen[k]==freq]
    assert len(freq)==1,"To many sequence length"
    freq = freq[0]
    assert freq % 2 == 0, ""
    lread = freq/2
    
    seqs = chain(first,entries)
    
    for s in seqs:
        d = s[0:lread]
        r = s[lread:]
        yield(d,r)
    
def seqPairs(direct,reverse):
    for d in direct:
        r = reverse.next()
        yield(d,r)

def seq2words(seqs,options):
    nw=set()
    for seq in seqs:
        s = str(seq)
        cs= str(seq.complement())
        ls = len(s) - options.length + 1

        if options.circular:
            s = s + s[0:options.length]
            cs = cs + cs[0:options.length]
 
        for wp in xrange(0,ls,options.step):
            w=s[wp:wp+options.length]
            if len(w)==options.length:
                nw.add(w)
            w=cs[wp:wp+options.length]
            if len(w)==options.length:
                nw.add(w)
                            
    return nw
    
            
if __name__ == '__main__':
    
    optionParser = getOptionManager([addWindowsOptions,addInOutputOption],progdoc=__doc__)
    
    (options, direct) = optionParser()
    
    assert options.index is not None,"You mmust specified -i option"
    
    if options.reverse is None:
        sequences=((x,) for x in direct)
    else:
        reverse = allEntryIterator([options.reverse],options.readerIterator)
        sequences=seqPairs(direct,reverse)
            
    reader = autoEntriesIterator(options)
    
    db = sqlite3.connect("%s.reads" % options.index)
    c = db.execute("""
                   create table sequence (
                       id int primary key,
                       forward text,
                       reverse text
                   );
                   """)
    
    c = db.execute("""
                   create table words (
                      id int primary key,
                      word text unique
                    );
                   """)
    
    c = db.execute("""
                   create table composition (
                      seqid  int,
                      wordid int,
                      primary key (seqid,wordid)
                      );
                   """)
    
    c = db.execute(""" create index seqididx on composition(seqid);""")
    c = db.execute(""" create index wordididx on composition(wordid);""")
    
#    seqidxName = "%s.sidx" % options.index
#    word2seqName = "%s.widx" % options.index
#    wordidx = shelve.open(word2seqName, protocol=2, writeback=True)
#    seqidx = shelve.open(seqidxName)
#    word2seq={}
    seqpair=0
    wordid=0
    nbseq=0
    k=0
    
    for seq in sequences:
        
        tseq = [formatFastq(s) for s in seq]
        words = seq2words(seq,options)
  
        seqid = seqpair
        
        c = db.execute("""
                       insert into sequence (id,forward,reverse)
                       values (?,?,?);
                       """ ,(seqid,tseq[0],tseq[1]))
        
        db.commit()
        
        for w in words:
            try:
                c = db.execute("""select id from words where word=?;""" , (w,))
                wid = c.fetchone()["id"]
            except :
                db.rollback()
                wid = wordid
                c = db.execute("""insert into words (id,word) values (?,?) ;""" , (wid,w))
                wordid+=1

                
            c = db.execute(""" insert into composition (seqid,wordid) values (?,?) ;""" , (seqid,wid))
                            
            db.commit()
                                   
        seqpair+=1
        
       
    db.commit()
    db.close()
        
