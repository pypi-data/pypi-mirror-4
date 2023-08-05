'''
**obitools** main module
------------------------

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>



obitools module provides base class for sequence manipulation.

All biological sequences must be subclass of :py:class:`obitools.BioSequence`.
Some biological sequences are defined as transformation of other
biological sequences. For example Reversed complemented sequences
are a transformation of a :py:class:`obitools.NucSequence`. This particular
type of sequences are subclasses of the :py:class:`obitools.WrappedBioSequence`.

.. inheritance-diagram:: BioSequence NucSequence AASequence WrappedBioSequence SubSequence DNAComplementSequence
        :parts: 1


'''

from _obitools import BioSequence,NucSequence,AASequence, \
                      WrappedBioSequence,SubSequence, \
                      DNAComplementSequence,_default_raw_parser, \
                      _isNucSeq,bioSeqGenerator

#try:
#    from functools import partial
#except:
#    #
#    # Add for compatibility purpose with Python < 2.5
#    #
#    def partial(func, *args, **keywords):
#        def newfunc(*fargs, **fkeywords):
#            newkeywords = keywords.copy()
#            newkeywords.update(fkeywords)
#            return func(*(args + fargs), **newkeywords)
#        newfunc.func = func
#        newfunc.args = args
#        newfunc.keywords = keywords
#        return newfunc


 


    

   
    

                
 
   

 
