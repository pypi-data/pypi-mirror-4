#!/usr/local/bin/python

'''
Created on 27 avr. 2012

@author: coissac
'''
from obitools.format.options import addInputFormatOption, addOutputFormatOption, sequenceWriterGenerator,\
    addOutputFormatOption
from obitools.options import getOptionManager
import re
import pprint


stops = (('TAA','TAG','TGA'),
         ('TAA','TAG','AGA','AGG'),
         ('TAA','TAG'),
         ('TGA',),
         ('TAA','TGA'),
         ('TCA','TAA','TGA'),
         ('TTA','TAA','TAG','TGA'))

fstop=set(['AGA','AGG','TAA','TAG','TCA','TGA','TTA'])
rstop={'CCT':'AGG','CTA':'TAG','TAA':'TTA','TCA':'TGA','TCT':'AGA','TGA':'TCA','TTA':'TAA'}
automata = re.compile('AG[AG]|C(CT|TA)|T(A[AG]|C[AT]|GA|TA)',re.IGNORECASE)

fstop=set(['TAA','TAG','TGA'])
rstop={'TTA':'TAA','CTA':'TAG','TCA':'TGA'}
automata = re.compile('CTA|T(A[AG]|CA|GA|TA)',re.IGNORECASE)




if __name__=='__main__':
    
    optionParser = getOptionManager([addInputFormatOption,addOutputFormatOption],progdoc=__doc__)
    
    (options, entries) = optionParser()

    writer = sequenceWriterGenerator(options)
    
    for seq in entries:
        s = str(seq).upper()
        istop = automata.finditer(s)
        matches={}
        for m in istop:
            stop = m.group(0)
            pos  = m.start(0)
            phase = pos % 3
            print stop,pos,phase
            if stop in fstop:
                p=phase+1
                s = matches.get(p,dict((x,[]) for x in fstop))
                s[stop].append(pos)
                matches[p]=s
                
            if stop in rstop:
                p=phase-3
                stop = rstop[stop]
                s = matches.get(p,dict((x,[]) for x in fstop))
                s[stop].append(pos)
                matches[p]=s
                
        print pprint.pformat(matches)
