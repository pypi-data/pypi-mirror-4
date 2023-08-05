'''
Created on 29 aout 2009

@author: coissac
'''

from _fastq import fastqQualitySangerDecoder,fastqQualitySolexaDecoder
from _fastq import qualityToSangerError,qualityToSolexaError
from _fastq import errorToSangerFastQStr
from _fastq import formatFastq
from _fastq import fastqParserGenetator
from _fastq import fastqAAIterator,fastqIlluminaIterator,fastqSolexaIterator, \
                   fastqSangerIterator, fastqIterator, fastqEntryIterator
from _fastq import fastFastqParserGenetator
from _fastq import fastFastqIlluminaIterator,fastFastqSolexaIterator, \
                   fastFastqSangerIterator, fastFastqIterator



