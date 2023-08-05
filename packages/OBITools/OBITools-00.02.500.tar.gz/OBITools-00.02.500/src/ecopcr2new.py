#!/usr/local/bin/python
'''
Created on 22 janv. 2010

@author: coissac
'''

from obitools.utils import ColumnFile
from obitools.thermo import calcTMTwoSeq,calcSelfTM
from obitools.options import getOptionManager
from itertools import chain

import re

if __name__ == '__main__':
    optionParser = getOptionManager([],
                                   )
    
    
    (options, entries) = optionParser()

    primermatch = re.compile('oligo([0-9]) +: +([^ ]+)')
    
    primer1=None
    primer2=None
    
    line=entries.next()
    while (line[0]=='#'):
        data = primermatch.findall(line)
        if data:
            if data[0][0]=='1':
                primer1=data[0][1]
            else:
                primer2=data[0][1]
        print line.strip()
        line = entries.next()
        
    primer1=primer1.replace("#","")
    primer2=primer2.replace("#","")

    print "# optimal Tm for primers 1 : %5.2f" % calcSelfTM(primer1)
    print "# optimal Tm for primers 2 : %5.2f" % calcSelfTM(primer2)

            
    entries=chain([line],entries)

    entries=ColumnFile(entries, '|', True, 
                                  (str,int,int,
                                   str,int,str,
                                   int,str,int,
                                   str,int,str,
                                   str,str,int,
                                   str,int,
                                   int,
                                   str,str), "#")
    
    template = "%-15s | %9d | %8d | %-20s | %8d | %-30s | %8d | %-30s | %8d | %-30s | %8d | %-30s | %c | %-32s | %2d | %5.2f | %-32s | %2d | %5.2f | %5d | %s | %s"
    for product in entries:
        try:
            tm1=calcTMTwoSeq(primer1, product[13])
        except KeyError:
            tm1=-1
        try:
            tm2=calcTMTwoSeq(primer2, product[15])
        except KeyError:
            tm2=-1
        product.insert(15,tm1)
        product.insert(18,tm2)
        print template % tuple(product)
           
    
