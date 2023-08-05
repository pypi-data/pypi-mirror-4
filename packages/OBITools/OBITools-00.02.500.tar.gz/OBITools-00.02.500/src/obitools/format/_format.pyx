# cython: profile=True

import sys
from obitools.fasta import formatFasta
from obitools.ecopcr.sequence import EcoPCRDBSequenceWriter

cpdef printOutput(options,seq,output=sys.stdout):
    if options.output is not None:
        r=options.output(seq)
    elif options.outputFormater is not None:
        r=options.outputFormater(seq,upper=options.uppercase)
    else:
        r=formatFasta(seq)

    try:
        output.write(r)
        output.write("\n")
    except IOError:
        sys.exit(0)
