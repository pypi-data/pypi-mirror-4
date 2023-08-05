"""
fasta module provides functions to read and write sequences in fasta format.


"""

from _fasta import parseFastaDescription, \
                   fastaParser, fastaNucParser,fastaAAParser, fastFastaParser, \
                   fastaIterator,fastFastaIterator, rawFastaIterator, \
                   fastaNucIterator, fastaAAIterator, \
                   formatFasta, formatSAPFastaGenerator


