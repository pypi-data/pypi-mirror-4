#!/usr/local/bin/python

from obitools.fasta import formatFasta
from obitools.format.sequence.fasta import fastaNucIterator
from obitools.options import getOptionManager
from obitools.utils import ColumnFile, deprecatedScript
from obitools.fast import Fast
from obitools import NucSequence
from obitools.word import wordDist,encodeWord
import re



def add454Options(optionManager):
    
    optionManager.add_option('-d','--direct',
                             action="store", dest="direct",
                             metavar="<PRIMER SEQUENCE>",
                             type="string",
                             default=None,
                             help="sequence of the direct primer")

    optionManager.add_option('-r','--reverse',
                             action="store", dest="reverse",
                             metavar="<PRIMER SEQUENCE>",
                             type="string",
                             default=None,
                             help="sequence of the reverse primer")

    optionManager.add_option('-l','--tag-length',
                             action="store", dest="taglength",
                             metavar="###",
                             type="int",
                             default=6,
                             help="length of the tag")

    optionManager.add_option('-k','--kup',
                             action="store", dest="kup",
                             metavar="###",
                             type="int",
                             default=1,
                             help="kup used for fast match")

    optionManager.add_option('-t','--tag-list',
                             action="store", dest="taglist",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file containing tag used")
    
    optionManager.add_option('-u','--unidentified',
                             action="store", dest="unidentified",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file used to store unidentified sequences")
    
def experiment(tag,tags):
    e=None
    et=None
    if tags is not None:
        if tag in tags:
            e=tags[tag]
            et=tag
        else:
            try :
                etag=encodeWord(tag)
            except RuntimeError:
                return None,None
            candidat = [x for x in tags if wordDist(etag, encodeWord(x))==1]
            if len(candidat)==1:
                et=candidat[0]
                e=tags[et]
    return et,e
   
def checkSequence(seq,direct,reverse=None,taglength=5,tags=None):
    
    # look for direct primer match
    # take into account the first match
    
    dscore,dpos = direct(seq)
    ok = dscore > len(direct) - 5 and dpos[0] > 0 and (len(seq) - dpos[0] > len(direct))
    good = None
    
    if ok:
        dpos = dpos[0]
        
        # Check if there is enough place for the tag
        ok = dpos >= taglength

        seq['scoreDirect']=dscore
        seq['direct']=seq[dpos:dpos+len(direct)]

        if ok :
        
            dtag = str(seq[dpos-taglength:dpos])
            det,dexperiment = experiment(dtag,tags)

            seq["tag"]=dtag
    
            if reverse:
                rscore,rpos = reverse(seq)
                ok = rscore > len(reverse) - 5
                
                    # take the first occurence of the reverse primer
                
                rpos = rpos[0] 
                seq['scoreReverse']=rscore
                
                if rpos > 0 and len(seq)-rpos >len(reverse):
                    seq['reverse']=seq[rpos:rpos+len(reverse)].complement()

        
                if ok:
                    
                    if  len(seq) - rpos - len(reverse) >= taglength:
                        rtag = str(NucSequence('rtag',seq[rpos+len(reverse):rpos+len(reverse)+taglength]).complement())
                        ret,rexperiment = experiment(rtag,tags)
                    
                        ok = dtag==rtag and tags is None or dexperiment==rexperiment
 
                        seq['reverse_tag']=rtag
                        
                        
                        
                        if ok:
                            if tags is not None:
                                seq['experiment_tag']=ret
                                seq['experiment']=rexperiment
                            if dpos+len(direct) < rpos:
                                good = seq[dpos+len(direct):rpos]
                            else:
                                seq["unidentified"]="overlapping primers"
                        else:
                            seq["unidentified"]="non concordant experiment"
                    else:
                        seq['warning']="no reverse tag"
                        if tags is not None:
                            seq['experiment_tag']=det
                            seq['experiment']=dexperiment
                        if dpos+len(direct) < rpos:
                            good = seq[dpos+len(direct):rpos]
                        else:
                            seq["unidentified"]="overlapping primers"
                else:
                    seq["unidentified"]="no reverse match"
            else:
                if tags is not None:
                    seq['experiment_tag']=det
                    seq['experiment']=dexperiment
                good = seq[dpos+len(direct):]
        else:
            seq["unidentified"]="direct tag not readable"
    else:
        seq["unidentified"]="no direct match"
        
            
        
    return good
    


if __name__=='__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    deprecatedScript('ngsfilter')
    
    optionParser = getOptionManager([add454Options],
                                    entryIterator=fastaNucIterator
                                    )
    
    (options, entries) = optionParser()
    
    if options.unidentified is not None:
        unidentified = open(options.unidentified,"w")
        
    assert options.direct is not None,"You must specified a direct Primer"
    
    direct = Fast(options.direct,options.kup)
    
    if options.reverse is not None:
        reverse = Fast(NucSequence("reverse",options.reverse).complement(),
                       options.kup)
    else:
        reverse = None
        
    if options.taglist:
        tags = dict((x[1].lower(),x[0]) for x in ColumnFile(options.taglist, types=(str,str)))
    else:
        tags = None
    
    for seq in entries:
        rep = checkSequence(seq,direct,reverse,options.taglength,tags)
        if rep is not None:
            print formatFasta(rep)
        elif options.unidentified is not None:
            print >>unidentified,formatFasta(seq)
    
