#!/usr/local/bin/python
'''
:py:mod:`obicount` : Count the number of sequences 
==================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obicount` count the number of sequences in a sequence file and/or their total count (use the 'count' annotation tag).

Example: To get the number of sequences in a file :

.. code-block:: bash

   > obicount seq.fasta 


Example: To get the total count of the sequences in a file:

.. code-block:: bash

   > obicount -a seq.fasta
   
Example: To get both the number and the total count of the sequences in a file :

.. code-block:: bash

   > obicount -s seq.fasta
    
'''

from obitools.options import getOptionManager
from obitools.format.options import addInOutputOption

def addCountOptions(optionManager):
    optionManager.add_option('-s','--sequence',
                             action="store_true", dest="sequence",
                             default=False,
                             help="Print the number sequences and their total count"
                             )
 
    optionManager.add_option('-a','--all',
                             action="store_true", dest="all",
                             default=False,
                             help="Print the total count of the sequences (if a sequence has no 'count' tag its default count is 1)"
                             )


if __name__ == '__main__':
    optionParser = getOptionManager([addCountOptions,addInOutputOption], progdoc=__doc__)
    
    (options, entries) = optionParser()
    
    count1=0
    count2=0
    
    for s in entries:
        count1+=1
        if 'count' in s:
            count2+=s['count']
        else:
            count2+=1
            
    if options.all==options.sequence:
        print count1,count2
    elif options.all:
        print count2
    else:
        print count1
        