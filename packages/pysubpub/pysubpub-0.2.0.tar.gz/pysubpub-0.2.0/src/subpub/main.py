"""
    Created on 2013-03-03
    @author: jldupont
"""
from functools import wraps

__all__=["sub", "pub", "upub", "get_subs", "get_queue", "clear_all_subs"]


## The interpreter-wide context dictionaries
SUBS={}
SUB_ALL=[]

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
        
    @param toall: True means that the function will get all the messages 
        
    """
    global SUBS, SUB_ALL
    
    try:    
        topic=handler_topic.__name__.split("_")[1]
    except:
        raise Exception("Invalid topic handler function name: %s" % handler_topic)
    
    @wraps(handler_topic)
    def message_receiver(*pa):
        return handler_topic(*pa)

    #is_new_topic=topic in SUBS

    if topic=="all":
        SUB_ALL.append(("a", message_receiver))
    else:
        lsubs=SUBS.get(topic, set())
        lsubs.update([("n", message_receiver)])
        SUBS[topic]=lsubs
            
    ### add this subscriber to all topics
    ###  and make sure to adjust the subscribers list
    ###  based on new topics introduced
    for lsubs in SUBS.itervalues():
        lsubs.update(SUB_ALL)
            
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
    Returns a copy of the {topic:[subscribers]} data
    
    Useful for debugging
    
    Useful for documenting call flows  
    """
    return dict(SUBS)


def get_queue():
    """
    Returns a copy of the message queue list
    
    Useful for debugging
    """
    return list(QUEUE)


def clear_all_subs():
    """
    Clear all handlers on topics
    
    Useful for nose tests
    """
    global SUBS, SUB_ALL
    
    SUBS={}
    SUB_ALL=[]
    

##
## PRIVATE =============================================================================
##    
    
def _dopub():
    """
    Actually performs the publishing
    """
    global INPROC, QUEUE, SUBS, SUB_ALL
    
    if INPROC:
        return

    INPROC=True
    
    while True:
        try:    msg=QUEUE.pop(0)
        except: break
        
        topic, params=msg

        lsubs=SUBS.get(topic, set())
        try:
            for _type, sub in lsubs:
                if _type=="n":
                    sub(*params)
                else:
                    sub(topic, *params)
        except:
            INPROC=False
            raise
         
    INPROC=False
