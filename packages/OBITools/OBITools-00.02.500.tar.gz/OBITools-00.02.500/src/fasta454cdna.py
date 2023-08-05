#!/usr/local/bin/python
'''
Created on 18 sept. 2009

@author: coissac
'''

from obitools.options import getOptionManager

from obitools.fasta import fastaNucIterator,formatFasta
from obitools.fast import Fast
from obitools import NucSequence


def condition(cond,v1,v2):
    if cond:
        return v1
    else:
        return v2

def score(seq,base,reward,penalty):
    s=[(reward if b==base else penalty) for b in seq]
    return s

def subvectmax(score):
    debut=0
    d0=0
    fin=0
    smax=0
    sum=0
    for i in xrange(len(score)):
        sum+=score[i]
        if sum < 0:
            sum=0
            d0=i+1
        if sum > smax:
            smax=sum
            fin=i+1
            debut=d0
    return debut,fin,smax

def locateOligoA(seq,reward=1,penalty=-1):
    debut,fin,smax = subvectmax(score(seq,'a',reward,penalty))
    fin=len(seq)
    return slice(debut,fin) ,smax   
        
def locateOligoT(seq,reward=1,penalty=-1):
    debut,fin,smax =  subvectmax(score(seq,'t',reward,penalty))
    debut=0
    return slice(debut,fin) ,smax   
    
def add454Options(optionManager):
    
    optionManager.add_option('-d','--direct',
                             action="store", dest="direct",
                             metavar="<PRIMER SEQUENCE>",
                             type="string",
                             default=None,
                             help="sequence of the direct primer")

#    optionManager.add_option('-r','--reverse',
#                             action="store", dest="reverse",
#                             metavar="<PRIMER SEQUENCE>",
#                             type="string",
#                             default=None,
#                             help="sequence of the reverse primer")

    optionManager.add_option('-k','--kup',
                             action="store", dest="kup",
                             metavar="###",
                             type="int",
                             default=1,
                             help="kup used for fast match")

    optionManager.add_option('-l','--lmin',
                             action="store", dest="lmin",
                             metavar="###",
                             type="int",
                             default=40,
                             help="minimal length of trimmed sequence")

    optionManager.add_option('-o','--oligo-score',
                             action="store", dest="soligo",
                             metavar="###",
                             type="int",
                             default=10,
                             help="minimal score for polyA detection")

    optionManager.add_option('-p','--oligo-penalty',
                             action="store", dest="penalty",
                             metavar="###",
                             type="int",
                             default=-1,
                             help="penalty used in polyA detection")

    optionManager.add_option('-b','--bad-sequences',
                             action="store", dest="bad",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file used to store bad sequences")
    
def checkCDNA(seq,options):
    ddscore,ddpos = options.directMatcher_d(seq)
    ddok = ddscore > len(options.direct) - 5 and ddpos[0] < 10
    
    drscore,drpos = options.directMatcher_r(seq)
    drok = drscore > len(options.direct) - 5 
    
    if ddok:
        debut=max(ddpos)
        if debut >= 0:
            dmatch=debut
            fmatch=debut+len(options.direct)
        else:
            dmatch=0
            fmatch=len(options.direct)-debut
            
        ddirect=seq[dmatch:fmatch]
        seq['ddirect']=ddirect
        if len(ddpos)>1:
            seq['multiddmatch']=True
        debut=fmatch
    else:
        ddirect=None
        debut=0
        
    if drok:
        try :
            start=min(x for x in drpos if x > debut)
        
            if start >= 0:
                dmatch=start
                fmatch=start+len(options.direct)
            else:
                dmatch=0
                fmatch=len(options.direct)-start
                
            rdirect=seq[dmatch:fmatch]
            seq['rdirect']=rdirect
            if len(drpos)>1:
                seq['multirdmatch']=True
            fin=dmatch
        except ValueError:
            drok=False
            fin=len(seq)
    else:
        rdirect=None
        fin=len(seq)
        
    if ddok or drok:
        seq=seq[debut:fin]
        
    oligoA,scoreA=locateOligoA(seq,penalty=options.penalty)
    oligoT,scoreT=locateOligoT(seq,penalty=options.penalty)
        
    if scoreA > scoreT:
        soligo=scoreA
        oligo=oligoA
        ot='A'
    else:
        soligo=scoreT
        oligo=oligoT
        ot='T'
        
    if soligo < options.soligo:
        oligo=None
        soligo=0
        ot=None
        
    if ot=='T' and not ddok:
        seq['rejected']="OligoT without direct primers"
        return False,seq
    
    if ot is not None:
        seq['poly']=ot
        seq['poly_score']=soligo
        seq['poly_length']=oligo.stop - oligo.start
        seq['oligo']=seq[oligo]
        if ot=='T':
            seq=seq[oligo.stop:]
        else:
            seq=seq[0:oligo.start]
    
    if len(seq) < options.lmin:
        seq['rejected']="sequence is too short (length < %d" % options.lmin
        return False,seq
    
    return True,seq    
    
if __name__=='__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([add454Options],
                                    entryIterator=fastaNucIterator
                                    )
    
    (options, entries) = optionParser()
    
    if options.bad is not None:
        badsequences = open(options.bad,"w")
        
    assert options.direct is not None,"You must specified a direct Primer"
    
        
    options.directMatcher_d = Fast(NucSequence("direct",options.direct),options.kup)
    options.directMatcher_r = Fast(NucSequence("direct_r",options.direct).complement(),options.kup)
    
#    if options.reverse is not None:
#        options.reverseMatcher_d = Fast(NucSequence("reverse",options.reverse),options.kup)
#        options.reverseMatcher_r = Fast(NucSequence("reverse_r",options.reverse).complement(),options.kup)
        
    for seq in entries:
        good,seq = checkCDNA(seq,options)
        if good :
            print formatFasta(seq)
        elif options.bad is not None:
            print >>badsequences,formatFasta(seq)


        
    

    
