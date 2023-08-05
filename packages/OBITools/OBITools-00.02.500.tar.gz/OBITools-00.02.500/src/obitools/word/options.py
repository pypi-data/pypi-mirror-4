from obitools.word import wordSelector
from obitools.word import allDNAWordIterator,encodeWord
from obitools.word import predicate




def _acceptedOptionCallback(options,opt,value,parser):
    if not hasattr(parser.values, 'acceptedOligo'):
        parser.values.acceptedOligo=[]
    parser.values.acceptedOligo.append(predicate.predicateMatchPattern(value,))
    
def _rejectedOptionCallback(options,opt,value,parser):
    if not hasattr(parser.values, 'rejectedOligo'):
        parser.values.rejectedOligo=[]
    parser.values.rejectedOligo.append(predicate.predicateMatchPattern(value))
    


def addOligoOptions(optionManager):
    
    optionManager.add_option('-L','--oligo-list',
                             action="store", dest="oligoList",
                             metavar="<filename>",
                             type="str",
                             help="filename containing a list of oligonucleotide")

    
    optionManager.add_option('-s','--oligo-size',
                             action="store", dest="oligoSize",
                             metavar="<###>",
                             type="int",
                             help="Size of oligonucleotide to generate")

    optionManager.add_option('-f','--family-size',
                             action="store", dest="familySize",
                             metavar="<###>",
                             type="int",
                             help="Size of oligonucleotide family to generate")

    optionManager.add_option('-d','--distance',
                             action="store", dest="oligoDist",
                             metavar="<###>",
                             type="int",
                             default=1,
                             help="minimal distance between two oligonucleotides")

    optionManager.add_option('-g','--gc-max',
                             action="store", dest="gcMax",
                             metavar="<###>",
                             type="int",
                             default=0,
                             help="maximum count of G or C nucleotide acceptable in a word")

    optionManager.add_option('-a','--accepted',
                             action="append",dest="acceptedPattern",
                             metavar="<regular pattern>",
                             default=[],
                             type="str",
                             help="pattern of accepted oligonucleotide")

    optionManager.add_option('-r','--rejected',
                             action="append",dest="rejectedPattern",
                             metavar="<regular pattern>",
                             default=[],
                             type="str",
                             help="pattern of rejected oligonucleotide")

    optionManager.add_option('-p','--homopolymer',
                             action="store", dest="homopolymere",
                             metavar="<###>",
                             type="int",
                             default=0,
                             help="reject oligo with homopolymer longer than.")

    optionManager.add_option('-P','--homopolymer-min',
                             action="store", dest="homopolymere_min",
                             metavar="<###>",
                             type="int",
                             default=0,
                             help="accept only oligo with homopolymer longer or equal to.")

def dnaWordIterator(options):
    
    assert options.oligoSize is not None or options.oligoList is not None,"option -s or --oligo-size must be specified"
    assert options.familySize is not None,"option -f or --family-size must be specified"
    assert options.oligoDist is not None,"option -d or --distance must be specified"
    
    if options.oligoList is not None:
        words = (encodeWord(x.strip().lower()) for x in open(options.oligoList))
    else:
        words = allDNAWordIterator(options.oligoSize)
    #seed  = 'a' * options.oligoSize
    options.acceptedOligo=[]
    for p in options.acceptedPattern:
        assert len(p)==options.oligoSize,"Accept pattern with bad lenth : %s" % p
        options.acceptedOligo.append(predicate.predicateMatchPattern(p, options.oligoSize))
        
    options.rejectedOligo=[]
    for p in options.rejectedPattern:
        assert len(p)==options.oligoSize,"Reject pattern with bad lenth : %s" % p
        options.rejectedOligo.append(predicate.predicateMatchPattern(p, options.oligoSize))
    
        
    #options.acceptedOligo.append(predicat.distMinGenerator(seed, options.oligoDist))
    
    if options.homopolymere:
        options.rejectedOligo.append(predicate.predicateHomoPolymerLarger(options.homopolymere, options.oligoSize))
        
    if options.homopolymere_min:
        options.acceptedOligo.append(predicate.predicateHomoPolymerLarger(options.homopolymere_min-1, options.oligoSize))
        
    if options.gcMax:
        options.rejectedOligo.append(predicate.predicateGCUpperBond(options.gcMax, options.oligoSize))
    
    return wordSelector(words, options.acceptedOligo, options.rejectedOligo)
