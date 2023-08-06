"""
    Created on 2013-03-03
    @author: jldupont
"""

from subpub import sub

import test1

@sub
def on_test99(param):       
    test1.push_event(("test2/test99", param))
