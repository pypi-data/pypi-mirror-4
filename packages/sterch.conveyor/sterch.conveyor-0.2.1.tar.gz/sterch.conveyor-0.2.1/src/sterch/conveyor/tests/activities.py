### -*- coding: utf-8 -*- #############################################
# Developed by Maksym Polshcha (maxp@sterch.net)
# All right reserved, 2012
#######################################################################

""" Activities for test cass for sterch.conveyor
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

from threading import Lock
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

gl_lock = Lock()
gl_jobs_counter = 0
gl_N = 50
gl_queue = Queue() 

def get_jobs_counter(): 
    global gl_jobs_counter
    return gl_jobs_counter

def reset_jobs(): 
    global gl_jobs_counter, gl_queue
    gl_jobs_counter = 0
    try:
        while True: gl_queue.get(False)
    except Empty:
        pass
    
def get_results(): 
    global gl_queue
    return gl_queue

def increment(job): 
    job['value'] +=1
    yield job
    
def mul10(job): 
    job['value'] *=10
    yield job

def neg(job): 
    job['value'] *= -1
    yield job

def jobs():
    """ jobs generator. Generates tasks and expected results for the tests """
    global gl_N
    for i in xrange(0, gl_N):
        yield dict(value = i, 
                   result = -(i * 10 + 1))
        
def check_results(job):
    """ Check value against expected result """
    global gl_jobs_counter, gl_N, gl_lock, gl_queue
    gl_queue.put(job)
    with gl_lock: gl_jobs_counter +=1
    assert gl_jobs_counter <= gl_N    