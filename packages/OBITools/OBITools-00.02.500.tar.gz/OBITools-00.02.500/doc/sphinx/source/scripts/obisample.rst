.. automodule:: obisample
   
   .. include:: ../optionsSet/defaultoptions.txt
   
   .. include:: ../optionsSet/inputformat.txt

   :py:mod:`obisample` specific options
   ------------------------------------   

   .. cmdoption::  -s <INT>, --sample-size <INT>   
   
                   Total count of sequences to be printed [default : number of provided sequences]
                   If -a option is set size is expressed as fraction
   
   .. cmdoption::  -a, --approx-sampling   
   
                   Switch to an approximative algorithm, useful for large files

   .. cmdoption::  -w, --without-replacement   
   
                   Ask for sampling without replacement
