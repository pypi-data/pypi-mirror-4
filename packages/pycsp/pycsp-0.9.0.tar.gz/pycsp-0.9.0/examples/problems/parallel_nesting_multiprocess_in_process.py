#!/usr/bin/env python
# -*- coding: latin-1 -*-
"""
Copyright (c) 2009 John Markus Bjoerndalen <jmb@cs.uit.no>,
      Brian Vinter <vinter@diku.dk>, Rune M. Friborg <runef@diku.dk>
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:
  
The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.  THE
SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from pycsp_import import *
import time

@multiprocess
def Prefix(cin, cout, prefixItem=None):
    t = prefixItem
    while True:
        cout(t)
        t = cin()

@multiprocess
def Delta2(cin, cout1, cout2):
    while True:
        t = cin()
        cout1(t)
        cout2(t)

@multiprocess
def Successor(cin, cout):
    """Adds 1 to the value read on the input channel and outputs it on the output channel.
    Infinite loop.
    """
    while True:
        cout(cin()+1)

@multiprocess
def Consumer(cin):
    "Commstime consumer process"
    N = 1000
    ts = time.time
    t1 = ts()
    cin()
    t1 = ts()
    for i in range(N):
        cin()
    t2 = ts()
    dt = t2-t1
    tchan = dt / (4 * N)
    print "DT = %f.\nTime per ch : %f/(4*%d) = %f s = %f us" % \
        (dt, dt, N, tchan, tchan * 1000000)
    print "consumer done, posioning channel"
    poison(cin)

@process
def CommsTimeBM():
    # Create channels
    a = Channel("a")
    b = Channel("b")
    c = Channel("c")
    d = Channel("d")

    print "Running commstime test"
    Parallel(Prefix(+c, -a, prefixItem = 0),  # initiator
             Delta2(+a, -b, -d),         # forwarding to two
             Successor(+b, -c),               # feeding back to prefix
             Consumer(+d))                         # timing process

N_BM = 10
for i in range(N_BM):
    print "----------- run %d/%d -------------" % (i+1, N_BM)
    Parallel(CommsTimeBM())

shutdown()
