Convert NCBI taxdump to binary formated OBITools taxonomy database
==================================================================

:command:`obitaxonomy` -t <taxdump dir> -d <db name>

Convert an text dump directory of the NCBI Taxonomy database to the binary
format used by ecoPCR and many *OBITools* scripts. An archive corresponding to
this directory can be downloaded at the following URL 

 `ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/ <ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/>`_

.. include:: ../optionsSet/defaultoptions.txt
      
.. include:: ../optionsSet/taxonomyDB.txt

example
-------

for building a new taxonomy database named *ncbitaxonomy* from a taxdump dir ::

    % curl ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz | tar zxf -
    % obitaxonomy --taxonomy-dump taxdump --database ncbitaxonomy
    
    
     