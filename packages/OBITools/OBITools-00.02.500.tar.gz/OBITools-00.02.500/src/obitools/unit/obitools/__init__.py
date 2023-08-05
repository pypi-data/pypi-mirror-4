import unittest

import obitools

from utils import tests_group as utils_tests_group

class BioseqTest(unittest.TestCase):

    sequenceId = 'id1'
    sequenceDefinition = 'sequence definition'
    sequenceQualifier = {'extra':3}

    def setUp(self):
        self.bioseq = self.bioseqClass(self.sequenceId,
                                       self.sequenceString,
                                       self.sequenceDefinition,
                                       **self.sequenceQualifier)
        
        title = self.__doc__.strip()
        underline = "=" * len(title)
        
        #print "%s\n%s" % (title,underline)
        
    def tearDown(self):
        pass
        #print "\n"

    def testIdAttribute(self):
        '''
        test if id attribute exists
        '''
        self.failUnless(hasattr(self.bioseq, 'id'), 'id missing attribute')
        
    def testIdValue(self):
        '''
        test if id attribute value is 'id1'
        '''
        self.failUnlessEqual(self.bioseq.id, 'id1', 
                             'identifier is created with good value')
        
    def testDefinitionAttribute(self):
        '''
        test if definition attribute exists
        '''
        self.failUnless(hasattr(self.bioseq, 'definition'), 'definition missing attribute')
        
    def testSequenceIsLowerCase(self):
        '''
        test if sequence is stored as lower case letter
        '''
        self.failUnlessEqual(str(self.bioseq), 
                             str(self.bioseq).lower(), 
                             "Sequence is not stored as lower case string")
        
    def testSequenceQualifier(self):
        '''
        test if the extra qualifier is present and its value is three.
        '''
        self.failUnlessEqual(self.bioseq['extra'], 
                             3, 
                             "Sequence qualifier cannot be successfully retrieve")
        
    def testCreateSequenceQualifier(self):
        self.bioseq['testqualifier']='ok'
        self.failUnlessEqual(self.bioseq['testqualifier'], 
                             'ok', 
                             "Sequence qualifier cannot be successfully created")
        
        

class NucBioseqTest(BioseqTest):
    '''
    Test obitools.NucSequence class
    '''
    
    bioseqClass = obitools.NucSequence
    sequenceString = 'AACGT' * 5
    

class AABioseqTest(BioseqTest):
    '''
    Test obitools.AASequence class
    '''
    
    bioseqClass = obitools.AASequence
    sequenceString = 'MLKCVT' * 5




tests_group = utils_tests_group + [NucBioseqTest,AABioseqTest] 