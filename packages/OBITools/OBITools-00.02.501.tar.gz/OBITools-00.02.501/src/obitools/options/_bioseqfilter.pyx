# cython: profile=True

from obitools.options.taxonomyfilter import taxonomyFilterGenerator


def filterGenerator(options):
    taxfilter = taxonomyFilterGenerator(options)
    
    if options.idlist is not None:
        idset=set(x.strip() for x in  open(options.idlist))
    else:
        idset=None

    
    def sequenceFilter(seq):
        cdef bint good = True
        
        if hasattr(options, 'sequencePattern'):
            good = <bint>(options.sequencePattern.search(str(seq)))
        
        if good and hasattr(options, 'identifierPattern'):
            good = <bint>(options.identifierPattern.search(seq.id))
            
        if good and idset is not None:
            good = seq.id in idset
            
        if good and hasattr(options, 'definitionPattern'):
            good = <bint>(options.definitionPattern.search(seq.definition))
            
        if good :
            good = reduce(lambda bint x, bint y:x and y,
                           (k in seq for k in options.has_attribute),
                           True)
            
        if good and hasattr(options, 'attributePatterns'):
            good = (reduce(lambda bint x, bint y : x and y,
                           (<bint>(options.attributePatterns[p].search(str(seq[p])))
                            for p in options.attributePatterns
                             if p in seq),True)
                    and
                    reduce(lambda bint x, bint y : x and y,
                           (bool(p in seq)
                            for p in options.attributePatterns),True)
                   )
            
        if good and hasattr(options, 'predicats') and options.predicats is not None:
            if options.taxonomy is not None:
                e = {'taxonomy' : options.taxonomy,'sequence':seq}
            else:
                e = {'sequence':seq}
                
            good = (reduce(lambda bint x, bint y: x and y,
                           (bool(eval(p,e,seq))
                            for p in options.predicats),True)
                   )

        if good and hasattr(options, 'lmin') and options.lmin is not None:
            good = len(seq) >= options.lmin
            
        if good and hasattr(options, 'lmax') and options.lmax is not None:
            good = len(seq) <= options.lmax
        
        if good:
            good = taxfilter(seq)
            
        if hasattr(options, 'invertedFilter') and options.invertedFilter:
            good=not good
                       
        
        return good
    
    return sequenceFilter

def sequenceFilterIteratorGenerator(options):
    filter = filterGenerator(options)
    
    def sequenceFilterIterator(seqIterator):
        for seq in seqIterator:
            if filter(seq):
                yield seq
            
    return sequenceFilterIterator
