#!/usr/local/bin/python

import unittest

from obitools.unit import tests_group


if __name__=='__main__':
    
    print
    print
    
    for x in tests_group:
        if x.__doc__ is not None:
            print x.__doc__.strip()
            print "-" * len(x.__doc__.strip())
        testset =unittest.TestLoader().loadTestsFromTestCase(x)
        tests = unittest.TestSuite([testset])
        unittest.TextTestRunner(verbosity=3).run(tests)
        print