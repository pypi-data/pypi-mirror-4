#!/usr/local/bin/python

import fileinput
import getopt
import sys

from obitools.fasta import fastaIterator,formatFasta

def dbTagBuilder():
    o,filenames = getopt.getopt(sys.argv[1:],
                                'hr:',
                                ['help',
                                 'reference=',
                                 'tag='])
    
    sys.argv[1:]=filenames

    dbTag = {}
    
    for name,value in o:
        if name in ('-h','--help'):
            printHelp()
            exit()
        elif name in ('-r','--reference'):
            f = fastaIterator(value)
            for seq in f:
                id = seq.id
                if id in dbTag:
                    dbTag[id].update(seq.getTags())
                else:
                    dbTag[id]=seq.getTags()

    return dbTag

if __name__=='__main__':
    
    dbTag = dbTagBuilder()

    file = fastaIterator(fileinput.input())
    
    for seq in file:
        if seq.id in dbTag:
            seq.getTags().update(dbTag[seq.id])
        print formatFasta(seq)
