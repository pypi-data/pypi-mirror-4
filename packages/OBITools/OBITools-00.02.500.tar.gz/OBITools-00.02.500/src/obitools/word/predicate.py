#@PydevCodeAnalysisIgnore
'''
Created on 14 oct. 2009

@author: coissac
'''

from _binary import wordDist, \
                    homoMax, \
                    countCG, \
                    matchPattern, \
                    encodePattern

def predicateWordDistMin(word,dmin,size):
    def predicate(w):
        return wordDist(word, w) >= dmin
    return predicate

def predicateHomoPolymerLarger(count,size):
    def predicate(w):
        return homoMax(w, size) > count
    return predicate

def predicateHomoPolymerSmaller(count,size):
    def predicate(w):
        return homoMax(w, size) < count
    return predicate

def predicateGCUpperBond(count,size):
    def predicate(w):
        return countCG(w, size) > count
    return predicate

def predicateMatchPattern(pattern,size):
    pattern=encodePattern(pattern)
    def predicate(w):
        return matchPattern(w, pattern)
    return predicate
    


