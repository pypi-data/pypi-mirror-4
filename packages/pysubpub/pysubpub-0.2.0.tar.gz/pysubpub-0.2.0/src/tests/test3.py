"""
    Created on 2013-03-04
    @author: jldupont
"""
from subpub import sub

from test1 import push_event_all

@sub
def on_all(topic, *p):
    push_event_all(("test3/all", (topic, p)))

