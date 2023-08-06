"""
Configuration module

Copyright (c) 2009 John Markus Bjoerndalen <jmb@cs.uit.no>,
      Brian Vinter <vinter@nbi.dk>, Rune M. Friborg <rune.m.friborg@gmail.com>.
See LICENSE.txt for licensing details (MIT License). 
"""

# Constants
SOCKETS_CONNECT_TIMEOUT = 0
SOCKETS_CONNECT_RETRY_DELAY = 1
SOCKETS_BIND_TIMEOUT = 2
SOCKETS_BIND_RETRY_DELAY = 3
PYCSP_PORT = 5
PYCSP_HOST = 6

SOCKETS_STRICT_MODE = 4

# Classes
class Configuration(object):
    """
    Configuration is a singleton class.
    
    >>> A = Configuration()
    >>> B = Configuration()
    >>> A == B
    True

    Retrieve value ( default is 10)
    >>> Configuration().get(SOCKETS_CONNECT_TIMEOUT)
    10

    Set value to 200
    >>> Configuration().set(SOCKETS_CONNECT_TIMEOUT, 200) 
    >>> Configuration().get(SOCKETS_CONNECT_TIMEOUT)
    200
    """

    __instance = None  # the unique instance
    __conf = {}

    def __new__(cls, *args, **kargs):
        return cls.getInstance(cls, *args, **kargs)

    def __init__(self):
        pass
    
    def getInstance(cls, *args, **kwargs):
        '''Static method to have a reference to **THE UNIQUE** instance'''
        if cls.__instance is None:
            # Initialize **the unique** instance
            cls.__instance = object.__new__(cls)
            
            cls.__conf = {
                SOCKETS_CONNECT_TIMEOUT:2,
                SOCKETS_CONNECT_RETRY_DELAY:0.2,
                SOCKETS_BIND_TIMEOUT:2,
                SOCKETS_BIND_RETRY_DELAY:0.2,
                PYCSP_PORT:0,
                PYCSP_HOST:'',
                SOCKETS_STRICT_MODE:False
                }
            
        return cls.__instance
    getInstance = classmethod(getInstance)

    def get(self, conf_id):
        return self.__conf[conf_id]

    def set(self, conf_id, value):
        self.__conf[conf_id] = value
    
