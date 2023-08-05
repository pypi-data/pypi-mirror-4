#!/usr/local/bin/python
'''
Created on 3 fevr. 2011

@author: coissac
'''
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager

def addSortOptions(optionManager):
    optionManager.add_option('-k','--key',
                             action="append", dest="key",
                             metavar="<TAG NAME>",
                             type="string",
                             default=[],
                             help="sequence attribute used as sort keys")
    
    optionManager.add_option('-r','--reverse',
                             action="store_true", dest="reverse",
                             default=False,
                             help="sort in reverse order")
    
def cmpGenerator(options):

    keys=options.key
    lk=len(keys)-1

    def cmpkeys(x,y,i=0):
        k=keys[i]
        c=cmp(x[k],y[k])
        if c==0 and i < lk:
            i+=1
            c=cmpkeys(x, y,i+1)
        if i==lk:
            i=0
        return c
    
    return cmpkeys

            

if __name__ == '__main__':

    optionParser = getOptionManager([addSortOptions,addInOutputOption])
    
    (options, entries) = optionParser()

    cmpk=cmpGenerator(options)
    
    seqs = [seq for seq in entries]
    seqs.sort(cmpk, reverse=options.reverse)

    writer = sequenceWriterGenerator(options)
    
    for seq in seqs:
        writer(seq)
