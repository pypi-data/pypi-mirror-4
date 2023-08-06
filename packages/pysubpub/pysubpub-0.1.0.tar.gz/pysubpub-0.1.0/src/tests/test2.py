"""
    Created on 2013-03-03
    @author: jldupont
"""

import os, sys
ap=os.path.abspath(__file__)
dn=os.path.dirname
base=dn(dn(dn(ap)))
sys.path.insert(0, base)
from subpub import sub

import test1

@sub
def on_test99(param):   
    global EVENTS
    
    test1.push_event(("test2/test99", param))
