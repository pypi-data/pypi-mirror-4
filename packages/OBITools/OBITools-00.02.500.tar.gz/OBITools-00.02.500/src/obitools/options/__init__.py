"""
    Module providing high level functions to manage command line options.
"""
import logging
import sys

from logging import debug

from optparse import OptionParser

from obitools.utils import universalOpen
from obitools.utils import fileSize
from obitools.utils import universalTell
from obitools.utils import progressBar
from obitools.format.options import addInputFormatOption, addInOutputOption,\
    autoEntriesIterator
import time
    
from _options import fileWithProgressBar, \
                     currentInputFileName, \
                     currentInputFile, \
                     currentFileSize, \
                     currentFileTell, \
                     allEntryIterator
                     


def getOptionManager(optionDefinitions,entryIterator=None,progdoc=None,checkFormat=False):
    '''
    Build an option manager fonction. that is able to parse
    command line options of the script.
    
    @param optionDefinitions: list of function describing a set of 
                              options. Each function must allows as
                              unique parametter an instance of OptionParser.
    @type optionDefinitions:  list of functions.
    
    @param entryIterator:     an iterator generator function returning
                              entries from the data files. 
                              
    @type entryIterator:      an iterator generator function with only one
                              parametter of type file
    '''
    parser = OptionParser(progdoc)
    parser.add_option('--DEBUG',
                      action="store_true", dest="debug",
                      default=False,
                      help="Set logging in debug mode")

    parser.add_option('--no-psyco',
                      action="store_true", dest="noPsyco",
                      default=False,
                      help="Don't use psyco even if it installed")

    parser.add_option('--without-progress-bar',
                      action="store_false", dest="progressbar",
                      default=True,
                      help="desactivate progress bar")

    for f in optionDefinitions:
        if f == addInputFormatOption or f == addInOutputOption:
            checkFormat=True 
        f(parser)
        
        
    def commandLineAnalyzer():
        options,files = parser.parse_args()
        if options.debug:
            logging.root.setLevel(logging.DEBUG)
            
        if checkFormat:
            if not hasattr(options, "skiperror"):
                options.skiperror=False
            ei=autoEntriesIterator(options)
        else:
            ei=entryIterator
        
            
        options.readerIterator=ei
        
        i = allEntryIterator(files,ei,with_progress=options.progressbar)
        return options,i
    
    return commandLineAnalyzer


        