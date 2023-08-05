#!/usr/local/bin/python
'''
Created on 25 nov. 2011

@author: merciece
'''

from obitools.graph.rootedtree import RootedTree


def main(BcValues,errors,tax) :
    
    tree = RootedTree()
    tset = set(BcValues)
    
    for taxon in BcValues:
        if taxon in errors :
            forErr = errors[taxon][0]
            revErr = errors[taxon][1]
            totErr = errors[taxon][2]
        else :
            forErr = -1.0
            revErr = -1.0
            totErr = -1.0
                     
        tree.addNode(taxon, rank=tax.getRank(taxon),
                       name=tax.getScientificName(taxon),
                       bc = BcValues[taxon],
                       errors = str(forErr)+' '+str(revErr),
                       totError = totErr
                    )

    for taxon in BcValues:
        piter = tax.parentalTreeIterator(taxon)
        taxon = piter.next()
        for parent in piter:
            if taxon[0] in tset and parent[0] in BcValues:
                tset.remove(taxon[0])
                tree.addEdge(parent[0], taxon[0])
                taxon=parent
                    
    return tree
