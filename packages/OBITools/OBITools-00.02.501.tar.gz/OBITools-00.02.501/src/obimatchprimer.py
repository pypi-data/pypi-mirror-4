#!/usr/local/bin/python
'''
Created on 6 nov. 2010

@author: coissac
'''
from obitools import NucSequence
from string import lower

import math

from obitools.options import getOptionManager
from obitools.utils import ColumnFile
from obitools.align import FreeEndGap
from obitools.format.options import addInOutputOption, printOutput



def addNGSOptions(optionManager):
    
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
                             default=None,
                             help="length of the tag")
    
    optionManager.add_option('--direct-tag',
                             action="store", dest="directlength",
                             metavar="###",
                             type="int",
                             default=None,
                             help="length of the direct tag")
    
    optionManager.add_option('--reverse-tag',
                             action="store", dest="reverselength",
                             metavar="###",
                             type="int",
                             default=None,
                             help="length of the reverse tag")

    optionManager.add_option('-1','--one-tag',
                             action="store_true", dest="onetag",
                             default=False,
                             help="Assert than only one tag in present on the direct primer")
    
    optionManager.add_option('-u','--unidentified',
                             action="store", dest="unidentified",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file used to store unidentified sequences")
    

def locatePrimer(sequence,finder):
    if len(sequence) > len(finder.seqB):
        finder.seqA=sequence
        ali=finder()
    #    print ali
        if ali.score >= len(finder.seqB)*4-4:
            return ali.score,ali[1].gaps[0][1],len(ali[1])-ali[1].gaps[-1][1]
    return None 

def annotate(sequence,options):
    
    alid,alir=None,None
    pdirect,preverse=None,None
    direct,reverse=None,None
    ltag=None
    tdirect,treverse=None,None
    fragment = None
    warning=[]
    good=True
    
    if hasattr(sequence, "quality"):
        q = -reduce(lambda x,y:x+y,(math.log10(z) for z in sequence.quality),0)/len(sequence.quality)*10
        sequence['avg_quality']=q
        q = -reduce(lambda x,y:x+y,(math.log10(z) for z in sequence.quality[0:10]),0)
        sequence['head_quality']=q
        if len(sequence.quality[10:-10]) :
            q = -reduce(lambda x,y:x+y,(math.log10(z) for z in sequence.quality[10:-10]),0)/len(sequence.quality[10:-10])*10
            sequence['mid_quality']=q
        q = -reduce(lambda x,y:x+y,(math.log10(z) for z in sequence.quality[-10:]),0)
        sequence['tail_quality']=q
        
        
    ip = iter(options.finder)
    
                    #
                    # Iterate over the direct primers
                    # until one match on direct or reverse strand
                    #
                    
    while direct is None:
        try:
            alid,alir=ip.next()
            strand=True
            direct = locatePrimer(sequence, alid)
            if direct is None:
                strand = False
                direct = locatePrimer(sequence, alir)
        except StopIteration:
            break 
        
                    # If a direct primer match
                    # look for corresponding reverse primer
                    # on the ooposite strand
                    
    if direct is not None:
        pdirect=str(alid.seqB)
        
        reverse=None
        ip = iter(options.primers[pdirect][1])
        while reverse is None:
            try:
                alid,alir=options.rfinder[ip.next()]
                if strand:
                    alig=alir
                else:
                    alig=alid
                reverse=locatePrimer(sequence, alig)
            except StopIteration:
                break
        
                # if direct and reverse primers are found then 
                # compute the length of the applicon
        
        if reverse is not None:
            preverse=str(alid.seqB)
            if strand :
                lampli = reverse[1]-direct[2]
            else:
                lampli = direct[1]-reverse[2]
        
                # Check for tags if present
            
        ltag = options.primers[pdirect][0]
        
        if ltag :
            if strand:
                endtag = direct[1]
                starttag=endtag - ltag 
                tdirect = str(sequence[starttag:endtag])
            else:
                starttag=direct[2]
                endtag=starttag + ltag
                tdirect = str(sequence[starttag:endtag].complement())
                
            if tdirect is not None and len(tdirect)!=ltag:
                tdirect=None

            if reverse is not None:
                if strand:
                    starttag=reverse[2]
                    endtag=starttag + ltag
                    treverse = str(sequence[starttag:endtag].complement())
                else:
                    endtag = reverse[1]
                    starttag=endtag - ltag 
                    treverse = str(sequence[starttag:endtag])
                    
                if treverse is not None and len(treverse)!=ltag:
                    treverse=None
                    
                    
                # both primers are found
                
    if direct is not None and reverse is not None:
        if strand:
            fragment = sequence[direct[2]:reverse[1]]
        else:
            fragment = sequence[reverse[2]:direct[1]].complement()
            
        if hasattr(sequence, 'quality'):
            if strand:
                quality = sequence.quality[direct[2]:reverse[1]]
            else:
                quality = sequence.quality[reverse[2]:direct[1]]
                quality.reverse()
        else:
            quality=None
            
                # Only direct primer is found
                
    elif direct is not None and reverse is None:
        if strand:
            print "direct partial"
            fragment = sequence[direct[2]:]
        else:
            print "reverse partial"
            fragment = sequence[0:direct[1]].complement()
        if hasattr(sequence, 'quality'):
            if strand:
                quality = sequence.quality[direct[2]:]
            else:
                quality = sequence.quality[0:direct[1]]
                quality.reverse()
                
    
        
    if fragment is not None:
        if len(fragment) > 0:
            if quality is not None:
                fragment.quality=quality
                        
            if direct is not None:
                fragment['direct_primer']=pdirect
                
                if strand:
                    fragment['direct_match']=str(sequence[direct[1]:direct[2]])
                else:
                    fragment['direct_match']=str(sequence[direct[1]:direct[2]].complement())
            
                fragment['direct_score']=direct[0]
                
                if ltag:
                    fragment['tag_length']=ltag
                    if tdirect is not None:
                        fragment['direct_tag']=tdirect
                    else:
                        warning.append('No direct tag')
                        
            if reverse is not None:
                fragment['reverse_primer']=preverse
                
                if strand:
                    fragment['reverse_match']=str(sequence[reverse[1]:reverse[2]].complement())
                else:
                    fragment['reverse_match']=str(sequence[reverse[1]:reverse[2]])
            
                fragment['reverse_score']=reverse[0]
    
                if ltag:
                    if treverse is not None:
                        fragment['reverse_tag']=treverse
                    else:
                        warning.append('No reverse tag')
                        
                        
                    if (tdirect is not None and 
                        (treverse is not None or options.onetag)) :
                        if tdirect!=treverse and not options.onetag:
                            warning.append('discrepancy between tags')
                        elif tdirect in options.primers[pdirect][1][preverse]:
                            fragment['experiment']=options.primers[pdirect][1][preverse][tdirect][0]
                            fragment['sample']=options.primers[pdirect][1][preverse][tdirect][1]
                            extra=options.primers[pdirect][1][preverse][tdirect][3]
                            if extra is not None:
                                for k in extra:
                                    fragment[k]=extra[k]
                        else:
                            warning.append('unused sample tags')
                        
                        
            else:
                warning.append('No reverse primer match')
                
        else:
            fragment['error']="Overlapping Primers"
            good=False
    else:
        fragment=sequence
        fragment['error']="No primer match"
        good=False

    if warning:
        fragment['warning']=warning
        
    #print
    #print pdirect,preverse,strand,direct,reverse,lampli,tdirect,treverse
    return good,fragment
            

if __name__ == '__main__':

    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([addNGSOptions,addInOutputOption])
                                    
    
    (options, entries) = optionParser()
    
    options.direct=options.direct.lower()
    primers={options.direct:(options.taglength,{})}
    alidd = FreeEndGap()
    alidd.match=4
    alidd.mismatch=-2
    alidd.opengap=-2
    alidd.extgap=-2
    alidd.seqB=NucSequence('primer',options.direct)
    alidr = FreeEndGap()
    alidr.match=4
    alidr.mismatch=-2
    alidr.opengap=-2
    alidr.extgap=-2
    alidr.seqB=alidd.seqB.complement()

    if options.reverse is not None:
        options.reverse=options.reverse.lower()
        alird = FreeEndGap()
        alird.match=4
        alird.mismatch=-2
        alird.opengap=-2
        alird.extgap=-2
        alird.seqB=NucSequence('primer',options.reverse)
        alirr = FreeEndGap()
        alirr.match=4
        alirr.mismatch=-2
        alirr.opengap=-2
        alirr.extgap=-2
        alirr.seqB=alird.seqB.complement()
    else:
        alird=None
        alirr=None
        
    options.directmatcher=(alidd,alird)
    options.reversematcher=(alidd,alird)
