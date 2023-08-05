#!/usr/local/bin/python
'''
Created on 24 nov. 2011

@author: merciece
'''


def main(seqs, keptRanks, tax):
    errorsBySeq = getErrorsOnLeaves(seqs)
    errorsByTaxon = propagateErrors(errorsBySeq, keptRanks, tax)
    return errorsBySeq, errorsByTaxon
    

def getErrorsOnLeaves(seqs) :    
    errors = {}
    for s in seqs :
        taxid = s['taxid']
        forErrs = s['forward_error']
        revErrs = s['reverse_error']
        total = forErrs + revErrs
        seqNb = 1
        errors[s.id] = [forErrs,revErrs,total,seqNb,taxid]
    return errors


def propagateErrors(errorsOnLeaves, keptRanks, tax) :
    allErrors = {}
    for seq in errorsOnLeaves :
        taxid = errorsOnLeaves[seq][4]
        p = [a for a in tax.parentalTreeIterator(taxid)]
        for a in p :
            if a[1] in keptRanks :
                group = a[0]
                if group in allErrors :
                    allErrors[group][0] += errorsOnLeaves[seq][0]
                    allErrors[group][1] += errorsOnLeaves[seq][1]
                    allErrors[group][2] += errorsOnLeaves[seq][2]
                    allErrors[group][3] += 1
                else :
                    allErrors[group] = errorsOnLeaves[seq]
    
    for group in allErrors :
        allErrors[group][0] /= float(allErrors[group][3])
        allErrors[group][1] /= float(allErrors[group][3])
        allErrors[group][2] /= float(allErrors[group][3])
        
        allErrors[group][0] = round(allErrors[group][0], 2)
        allErrors[group][1] = round(allErrors[group][1], 2)
        allErrors[group][2] = round(allErrors[group][2], 2)
        
    return allErrors




