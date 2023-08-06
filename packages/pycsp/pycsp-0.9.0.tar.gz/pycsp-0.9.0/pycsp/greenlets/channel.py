"""
Channel module

Copyright (c) 2009 John Markus Bjoerndalen <jmb@cs.uit.no>,
      Brian Vinter <vinter@nbi.dk>, Rune M. Friborg <rune.m.friborg@gmail.com>.
See LICENSE.txt for licensing details (MIT License). 
"""

# Imports
try: from greenlet import greenlet
except ImportError, e:
    from py.magic import greenlet
    
from scheduling import Scheduler
from channelend import ChannelEndRead, ChannelEndWrite, ChannelRetireException
from exceptions import *

from pycsp.common.const import *

import time, random

# Classes
class ChannelReq:
    def __init__(self, process, msg=None):
        self.msg = msg
        self.result = FAIL
        self.process = process

    def poison(self):
        if self.result != SUCCESS:
            self.result = POISON
            self.process.notify(POISON)

    def retire(self):
        if self.result != SUCCESS:
            self.result = RETIRE
            self.process.notify(RETIRE)

    def offer(self, recipient):
        if self.process.state == recipient.process.state == ACTIVE:
            recipient.msg= self.msg
            self.result=SUCCESS
            recipient.result=SUCCESS
            self.process.notify(DONE)
            recipient.process.notify(DONE)
            return True
        return False


class Channel(object):
    """ Channel class. Blocking communication
    """

    def __new__(cls, *args, **kargs):
        if kargs.has_key('buffer') and kargs['buffer'] > 0:
            import buffer                      
            chan = buffer.BufferedChannel(*args, **kargs)
            return chan
        else:
            return object.__new__(cls)

    def __init__(self, name=None, buffer=0):

        if name == None:
            # Create unique name
            self.name = str(random.random())+str(time.time())
        else:
            self.name=name

        self.readqueue = []
        self.writequeue = []
        
        # Count, makes sure that all processes knows how many channel ends have retired
        self.readers = 0
        self.writers = 0

        self.ispoisoned = False
        self.isretired = False

        self.s = Scheduler()
        
    def check_termination(self):        
        if self.ispoisoned:
            raise ChannelPoisonException()
        if self.isretired:
            raise ChannelRetireException()

    def _read(self):
        self.check_termination()

        p = self.s.current
        
        # If anyone is on the writequeue and ACTIVE, then we can do the match right away
        # This hack provides a 150% performance improvement and can be removed
        # without breaking anything.
        for w in self.writequeue:
            if w.process.state == ACTIVE:
                msg = w.msg
                w.result = SUCCESS
                w.process.state = DONE
                if p != w.process:
                    self.s.next.append(w.process)
                return msg        

        p.setstate(ACTIVE)
        req = ChannelReq(p)
        self._post_read(req)
        req.process.wait()
        self._remove_read(req)

        if req.result==SUCCESS:
            return req.msg
        
        self.check_termination()
            
        print 'We should not get here in read!!!'
        return None #Here we should handle that a read was cancled...

    
    def _write(self, msg):
        self.check_termination()

        p = self.s.current
        
        # If anyone is on the readqueue and ACTIVE, then we can do the match right away
        # This hack provides a 150% performance improvement and can be removed
        # without breaking anything.
        for r in self.readqueue:
            if r.process.state == ACTIVE:
                r.msg = msg
                r.result = SUCCESS
                r.process.state = DONE
                if p != r.process:
                    self.s.next.append(r.process)
                return True

        p.setstate(ACTIVE)
        req = ChannelReq(p,msg=msg)
        self._post_write(req)
        req.process.wait()
        self._remove_write(req)

        if req.result==SUCCESS:
            return True
    
        self.check_termination()

        print 'We should not get here in write!!!'
        return None #Here we should handle that a read was cancled...

    def _post_read(self, req):
        self.check_termination()
        self.readqueue.append(req)
        self.match()

    def _remove_read(self, req):
        self.readqueue.remove(req)
        
    def _post_write(self, req):
        self.check_termination()
        self.writequeue.append(req)
        self.match()

    def _remove_write(self, req):
        self.writequeue.remove(req)

    def match(self):
        if self.readqueue and self.writequeue:
            for w in self.writequeue:
                for r in self.readqueue:
                    if w.offer(r):
                        # Did an offer
                        # We can guarantee, that there will always be someone to call offer,
                        # since everything is run in a single thread. Thus we break the loop.
                        return

    def poison(self):
        if not self.ispoisoned:
            self.ispoisoned = True
            map(ChannelReq.poison, self.readqueue)
            map(ChannelReq.poison, self.writequeue)

    def __pos__(self):
        return self.reader()

    def __neg__(self):
        return self.writer()

    def __mul__(self, multiplier):
        new = [self]
        for i in range(multiplier-1):
            new.append(Channel(name=self.name+str(i+1)))
        return new

    def __rmul__(self, multiplier):
        return self.__mul__(multiplier)

    def reader(self):
        self.join_reader()
        return ChannelEndRead(self)

    def writer(self):
        self.join_writer()
        return ChannelEndWrite(self)

    def join_reader(self):
        self.readers+=1

    def join_writer(self):
        self.writers+=1

    def leave_reader(self):
        if not self.isretired:
            self.readers-=1
            if self.readers==0:
                # Set channel retired
                self.isretired = True
                for p in self.writequeue[:]:
                    p.retire()

    def leave_writer(self):
        if not self.isretired:
            self.writers-=1
            if self.writers==0:
                # Set channel retired
                self.isretired = True
                for p in self.readqueue[:]: # ATOMIC copy
                    p.retire()

