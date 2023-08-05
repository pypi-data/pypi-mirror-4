'''
Created on 2 juil. 2012

@author: coissac
'''
import unittest

from obitools.lazzy import Tag,WrappedTag

class AbstractTagTest(unittest.TestCase):
    
    def testIteritems(self):
        k = [x for x in self.tag.iteritems()]
        k2= [(x[0],x[1]) for x in self.items]

                
        k.sort()
        k2.sort()
        
        self.assertEqual(k,k2,"Error in interitems()")
        
    def testItems(self):
        k = self.tag.items()
        k2= [(x[0],x[1]) for x in self.items]
        
        k.sort()
        k2.sort()
        
        self.assertEqual(k,k2, 'Error in items()')
        
    def testIterkeys(self):
        k = [x for x in self.tag.iterkeys()]
        k2= [x[0] for x in self.items]
        
        k.sort()
        k2.sort()
        
        self.assertEqual(k, k2, "Error in iterkeys()")
        
    def testIterDict(self):
        k = [x for x in self.tag]
        k2= [x[0] for x in self.items]
        
        k.sort()
        k2.sort()
        
        self.assertEqual(k, k2, "Error in __iter__()")
        
    def testKeys(self):
        k = self.tag.keys()
        k2= [x[0] for x in self.items]
        
        k.sort()
        k2.sort()
        
        self.assertEqual(k, k2, "Error in keys()")
        
    def testItervalues(self):
        k = [x for x in self.tag.itervalues()]
        k2= [x[1] for x in self.items]
        
        k.sort()
        k2.sort()
        
        self.assertEqual(k, k2, "Error in itervalues()")

    def testValues(self):
        k = self.tag.values()
        k2= [x[1] for x in self.items]
        
        k.sort()
        k2.sort()
        
        self.assertEqual(k, k2, "Error in values()")

    def testIn(self):
        k2= [x[0] for x in self.items]
        for k in k2:
            self.assert_(k in self.tag,"Not able to find %s in tag" % k)
            
    def testHasKey(self):
        k2= [x[0] for x in self.items]
        for k in k2:
            self.assert_(self.tag.has_key(k),"Not able to find %s in tag" % k)

    def testGetitem(self):
        for k,v,t in self.items:
            self.assert_(isinstance(self.tag[k], t),"Type of value %s (%s) is not recognized as %s" % (k,str(type(self.tag[k])),str(t)))
            self.assertEqual(self.tag[k], v, "Value associated to key %s (%s) is not well evaluated to %s" % (k,str(self.tag[k]),str(v)))
        
    def testGet(self):
        k = set(x[0] for x in self.items)
        for k,v,t in self.items:
            self.assert_(isinstance(self.tag.get(k), t),"Type of value %s (%s) is not recognized as %s" % (k,str(type(self.tag[k])),str(t)))
            self.assertEqual(self.tag.get(k), v, "Value associated to key %s (%s) is not well evaluated to %s" % (k,str(self.tag[k]),str(v)))
        ak="_a_b_b_"
        v="wxcvbn,"
        self.assert_( ak not in k,"Unexpected inconsistancy") 
        self.assertEqual(self.tag.get(ak,v), v, "the default value %s cannot be retreive" % v)
        self.assert_(self.tag.get(ak) is None, "the default default value None cannot be retreive")

    def testSetItem(self):
        ak="_a_b_b_"
        v="wxcvbn,"
        self.assert_( ak not in self.tag,"Unexpected inconsistancy") 
        self.tag[ak]=v 
        self.assert_( ak in self.tag,"Key %s was not add into the tags" % ak)
        self.assertEqual(self.tag[ak], v, "Value %s is not correctely assigned to tag %s" % (v,ak))
         
    def testUpdateItem(self):
        nv="wxcvbn,"
        for k,v,t in self.items:
            self.assert_( k in self.tag,"Unexpected inconsistancy") 
            self.tag[k]=nv
            self.assertEqual(self.tag[k], nv, "Value associated to key %s (%s) is not well evaluated to %s" % (k,str(self.tag[k]),str(v)))
        
        
    def testDelItem(self):
        for k,v,t in self.items:
            self.assert_(k in self.tag,"Unexpected inconsistancy")
            del self.tag[k]
            self.assert_(k not in self.tag,"Key %s is still present in tag" % k)

    def testLen(self):
        l1=len(self.tag)
        l2=len(self.items)
        self.assertEqual(l1, l2, "len is not returning the good length (%d instead of %d)" % (l1,l2))
        
    def testClear(self):
        l1=len(self.tag)
        l2=len(self.items)
        self.assertEqual(l1, l2, "Unexpected inconsistancy")
        self.tag.clear()
        l1=len(self.tag)
        self.assertEqual(l1, 0, "tag is not empty after clear call remains %d items over %d" % (l1,l2))
        
    def testCopy(self):
        c = self.tag.copy()
        k = [x for x in c.iteritems()]
        k2= [(x[0],x[1]) for x in self.items]
        
        k.sort()
        k2.sort()

        self.assertEqual(k,k2,"Error in copy()")
        
    def testPop(self):
        for k,v,t in self.items:
            self.assert_( k in self.tag,"Unexpected inconsistancy") 
            rep = self.tag.pop(k)
            self.assertEqual(rep, v, "Value associated to key %s (%s) is not well evaluated to %s" % (k,str(rep),str(v)))
            self.assert_(k not in self.tag,"pop() was not able to remove key %s" % k)
        
    def testPopDefault(self):
        ak="_a_b_b_"
        v="wxcvbn,"
        self.assert_( ak not in self.tag,"Unexpected inconsistancy") 
        x = self.tag.pop(ak,v)
        self.assertEqual(x, v, "Default value (%s) is not well evaluated to %s" % (str(x),str(v)))
        
    def testPopItem(self):
        k2= [(x[0],x[1]) for x in self.items]
        
        rep = []
        try:
            while(1):
                rep.append(self.tag.popitem())
        except KeyError:
            pass
        
        k2.sort()
        rep.sort()
        
        self.assertEqual(rep,k2,"Error in popitem()")
        
    def testSetDefault(self):
        d = self.class_()
        for k,v,t in self.items:
            x = d.setdefault(k,v)
            self.assertEqual(v, x, "I have not retreve the good value (%s instead of %s)" % (str(x),str(v)))
            x = d.setdefault(k)
            self.assertEqual(v, x, "I have not retreve the good value (%s instead of %s)" % (str(x),str(v)))
            
    def testUpdate(self):
        k2= [(x[0],None) for x in self.items]
        d = self.class_()
        d.update(k2)
        k=d.items()
        
        k2.sort()
        k.sort()
        
        self.assertEqual(k,k2,"Error in update() during key creation")
        
        k2= [(x[0],x[1]) for x in self.items]

        d.update(k2)
        k=d.items()
        
        k2.sort()
        k.sort()
        
        self.assertEqual(k,k2,"Error in update() during key update")
      
        
        

class TagTest(AbstractTagTest):

    def setUp(self):
        
        self.class_ = Tag
        
        self.tag=Tag("A=32; B_1=12.3; C=True; D=toto; E=(1,2,3);"
                     " F=['titi',3]; G={'aa':10,'bb':100};")
        
        self.items=[('A',32,int),
                    ('B_1',12.3,float),
                    ('C',True,bool),
                    ('D',b'toto',bytes),
                    ('E',(1,2,3),tuple),
                    ('F',['titi',3],list),
                    ('G',{'aa':10,'bb':100},dict)]


    def tearDown(self):
        pass
    
    def testFromkeys(self):
        k = set(x[0] for x in self.items)
        t = Tag.fromkeys(k,100)

        k = t.items()
        k2= [(x[0],100) for x in self.items]

        k.sort()
        k2.sort()

        self.assertEqual(k,k2,"Error in fromkeys()")

    def testFromkeysNone(self):
        k = set(x[0] for x in self.items)
        t = Tag.fromkeys(k)

        k = t.items()
        k2= [(x[0],None) for x in self.items]

        k.sort()
        k2.sort()

        self.assertEqual(k,k2,"Error in fromkeys() with a default value")

class WrappedTagTest(AbstractTagTest):

    def setUp(self):
        
        self.class_ = WrappedTag
        
        tag=Tag("A=32; B_1=12.3; C=True; D=toto; E=(1,2,3);"
                     " F=['titi',3]; G={'aa':10,'bb':100};")
        
        self.tag=WrappedTag(tag)
        
        self.items=[('A',32,int),
                    ('B_1',12.3,float),
                    ('C',True,bool),
                    ('D',b'toto',bytes),
                    ('E',(1,2,3),tuple),
                    ('F',['titi',3],list),
                    ('G',{'aa':10,'bb':100},dict)]


tests_group = [TagTest,WrappedTagTest]

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()