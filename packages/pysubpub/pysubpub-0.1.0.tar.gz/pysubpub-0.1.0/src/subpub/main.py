"""
    Created on 2013-03-03
    @author: jldupont
"""
from functools import wraps

__all__=["sub", "pub", "upub", "get_subs"]

## The interpreter-wide context dictionary
SUBS={}

## The interpreter-wide queue
QUEUE=[]

## For handling re-entrancy during the publishing phase
INPROC=False


def sub(handler_topic):
    """
    Decorator for "topic handler" functions
    
    Keeps track of "topic subscribers"
    
    The name of the input function is used to refer to the topic name e.g.
    
        'on_begin'  ==> topic name='begin'
        
    """
    global SUBS
    
    try:    
        topic=handler_topic.__name__.split("_")[1]
    except:
        raise Exception("Invalid topic handler function name: %s" % handler_topic)
    
    @wraps(handler_topic)
    def message_receiver(*pa):
        return handler_topic(*pa)

    lsubs=SUBS.get(topic, [])
    lsubs.append(message_receiver)
    SUBS[topic]=lsubs
    
    def do_not_call_directly(*p, **k):
        raise Exception("Do not call a 'topic subscriber' function directly: %s" % handler_topic.__name__)
    
    return do_not_call_directly


def pub(topic, *pa):
    """
    Publish function
    
    Queues the message
    """
    global QUEUE
    
    QUEUE.append((topic, pa))
    
    _dopub()
    
    
    
def upub(topic, *pa):
    """
    Urgent publish function
    
    Inserts the message up front i.e. not at the end of the queue
    """
    global QUEUE
    
    QUEUE.insert(0, (topic, pa))
    
    _dopub()

##
## DEBUG  ==============================================================================
##

def get_subs():
    """
    Returns the {topic:[subscribers]
    
    Useful for debugging
    
    Useful for documenting call flows  
    """
    return SUBS


##
## PRIVATE =============================================================================
##    
    
def _dopub():
    """
    Actually performs the publishing
    """
    global INPROC, QUEUE, SUBS
    
    if INPROC:
        return

    INPROC=True
    
    while True:
        try:    msg=QUEUE.pop(0)
        except: break
        
        topic, params=msg
        
        lsubs=SUBS.get(topic, [])
        for sub in lsubs:
            sub(*params)
        
    INPROC=False
