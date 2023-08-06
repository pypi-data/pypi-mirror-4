"""
    Created on 2013-03-03
    @author: jldupont
"""
__all__=["push_event"]

import unittest

import os, sys
ap=os.path.abspath(__file__)
dn=os.path.dirname
base=dn(dn(dn(ap)))
sys.path.insert(0, base)
from subpub import sub, pub, upub, get_subs



def push_event(e):
    global EVENTS
    EVENTS.append(e)

@sub
def on_test1(param):   
    global EVENTS
    
    EVENTS.append(("test1", param))

@sub
def on_test2(param1, param2):
    global EVENTS
    
    EVENTS.append(("test2", (param1, param2)))

@sub
def on_test3(param1):
    global EVENTS
    
    EVENTS.append(("test3", param1))
    
    ## the next one goes on the queue, at the end, as normal
    pub("test5",  param1)
    
    ## but this one would be queued in front of the previous
    upub("test4", param1)
    


@sub
def on_test4(param1):
    global EVENTS
    
    EVENTS.append(("test4", param1))

@sub
def on_test5(param1):
    global EVENTS
    
    EVENTS.append(("test5", param1))

    
@sub
def on_test6():
    raise Exception("Some exception in test6")


@sub
def on_test99(param):   
    global EVENTS
    
    EVENTS.append(("test99", param))


class TestCases(unittest.TestCase):
    
    def setUp(self):
        global EVENTS
        EVENTS=[]
    
            
    
    def test_a1_simple(self):
        """
        Simple 1 topic, 2 msgs
        """
        global EVENTS
        
        pub("test1", "value1")
        pub("test1", "value2")

        self.assertEqual(len(EVENTS), 2)
        
        topic1, val1=EVENTS.pop(0)
        self.assertEqual(topic1, "test1")
        self.assertEqual(val1, "value1")
        
        topic2, val2=EVENTS.pop(0)
        self.assertEqual(topic2, "test1")
        self.assertEqual(val2, "value2")
        
    def test_a2_two_topics(self):
        """
        Two topics, 2 msgs
        """
        
        pub("test1", "value1")
        pub("test2", "param1", "param2")
        self.assertEqual(len(EVENTS), 2)

        topic1, val1=EVENTS.pop(0)
        self.assertEqual(topic1, "test1")
        self.assertEqual(val1, "value1")
        
        topic2, val2=EVENTS.pop(0)
        self.assertEqual(len(val2), 2)
        
        self.assertEqual(topic2, "test2")
        
        a,b=val2
        self.assertEqual(a, "param1")
        self.assertEqual(b, "param2")
        
    def test_a3_simple_urgent(self):
        """
        Simple urgent, 1 topics, 3msgs
        """
        
        pub("test3", "value3")
        
        self.assertEqual(len(EVENTS), 3)
        
        topic1, val1=EVENTS.pop(0)
        self.assertEqual(topic1, "test3")
        self.assertEqual(val1,   "value3")
        
        topic2, val2=EVENTS.pop(0)
        self.assertEqual(topic2, "test4")
        self.assertEqual(val2,   "value3")
                
        topic3, val3=EVENTS.pop(0)
        self.assertEqual(topic3, "test5")
        self.assertEqual(val3,   "value3")
        
    def test_a4_donotcalldirectly(self):
        """
        Do not call sub function directly
        """
        with self.assertRaises(Exception) as _context:
            on_test1("value1")
            
    def test_z1_2modules(self):
        """
        Simple 2 modules, 1 msg
        """
        import test2
        
        pub("test99", "value1")
        self.assertEqual(len(EVENTS), 2)
        
        topic1, val1=EVENTS.pop(0)
        self.assertEqual(topic1, "test99")
        self.assertEqual(val1,   "value1")
        
        topic2, val2=EVENTS.pop(0)
        self.assertEqual(topic2, "test2/test99")
        self.assertEqual(val2,   "value1")

            
    def test_z2_get_subs(self):
        """
        Test for get_subs
        """
        print
        subs=get_subs()

        for topic in subs:
            liste=subs[topic]
            for sub in liste:
                print "sub: mod=", sub.__module__,", fnc=",sub.__name__

    ## need to put this test towards the end (hence the 'x')
    ## If not, the rest of the tests fail...
    def test_z3_raise(self):
        """
        Raise an exception
        """
        with self.assertRaises(Exception) as _context:
            pub("test6")
        
     
if __name__ == '__main__':
    unittest.main()

