"""
Copyright (c) 2009 John Markus Bjoerndalen <jmb@cs.uit.no>,
      Brian Vinter <vinter@nbi.dk>, Rune M. Friborg <rune.m.friborg@gmail.com>.
See LICENSE.txt for licensing details (MIT License). 
"""

from pycsp_import import *
import check
import time
import random

@choice
def action(assertCheck, id, channel_input=None):
    if assertCheck:
        assertCheck(id)

@process
def reader(cin, id,  sleeper, assertCheck=None):
    while True:
        if sleeper: sleeper()
        got = cin()
        if assertCheck:
            assertCheck(id)
    
@process
def writer(cout, id, cnt, sleeper):
    for i in range(cnt):
        if sleeper: sleeper()
        cout((id, i))
    retire(cout)

@process
def par_reader(cin1,cin2,cin3,cin4, sleeper, assertCheck=None):
    while True:
        if sleeper: sleeper()
        AltSelect(
            InputGuard(cin1, action(assertCheck, 0)),
            InputGuard(cin2, action(assertCheck, 1)),
            InputGuard(cin3, action(assertCheck, 2)),
            InputGuard(cin4, action(assertCheck, 3))
            )

@process
def par_writer(cout1,cout2,cout3,cout4, cnt, sleeper):
    for i in range(cnt*4):
        if sleeper: sleeper()
        AltSelect(
            OutputGuard(cout1, i),
            OutputGuard(cout2, i),
            OutputGuard(cout3, i),
            OutputGuard(cout4, i)
            )
        
    retire(cout1, cout2, cout3, cout4)

@io
def sleep_random():
    time.sleep(random.random()/100)

@io
def sleep_one():
    time.sleep(0.01)

def One2One_Test(read_sleeper, write_sleeper):
    x = Channel()
    Spawn(check.Assert(x.reader(), "One2One_Test"+str(read_sleeper)+str(write_sleeper), count=40, vocabulary=[0,1,2,3]))

    c1=Channel()
    c2=Channel()
    c3=Channel()
    c4=Channel()

    cnt = 10
    
    Parallel(reader(+c1,0, read_sleeper, x.writer()), writer(-c1,0,cnt, write_sleeper),
             reader(+c2,1, read_sleeper, x.writer()), writer(-c2,1,cnt, write_sleeper),
             reader(+c3,2, read_sleeper, x.writer()), writer(-c3,2,cnt, write_sleeper),
             reader(+c4,3, read_sleeper, x.writer()), writer(-c4,3,cnt, write_sleeper))

def Any2One_Test(read_sleeper, write_sleeper):
    x = Channel()
    Spawn(check.Assert(x.reader(), "Any2One_Test"+str(read_sleeper)+str(write_sleeper), count=40, vocabulary=[0]))

    c1=Channel()

    cnt = 10
    
    Parallel(reader(c1.reader(),0, read_sleeper, x.writer()),
             writer(c1.writer(),0,cnt, write_sleeper),
             writer(c1.writer(),1,cnt, write_sleeper),
             writer(c1.writer(),2,cnt, write_sleeper),
             writer(c1.writer(),3,cnt, write_sleeper))

def One2Any_Test(read_sleeper, write_sleeper):
    x = Channel()
    Spawn(check.Assert(x.reader(), "One2Any_Test"+str(read_sleeper)+str(write_sleeper), count=40, vocabulary=[0,1,2,3]))

    c1=Channel()

    cnt = 10
    
    Parallel(writer(c1.writer(),0,cnt*4, write_sleeper),
             reader(c1.reader(),0, read_sleeper, x.writer()),
             reader(c1.reader(),1, read_sleeper, x.writer()),
             reader(c1.reader(),2, read_sleeper, x.writer()),
             reader(c1.reader(),3, read_sleeper, x.writer()))


def One_Alting2Any_Test(read_sleeper, write_sleeper):
    x = Channel()
    Spawn(check.Assert(x.reader(), "One_Alting2Any_Test"+str(read_sleeper)+str(write_sleeper), count=40, vocabulary=[0,1,2,3]))

    c1=Channel()
    c2=Channel()
    c3=Channel()
    c4=Channel()

    cnt = 10
    
    Parallel(par_writer(c1.writer(),c2.writer(),c3.writer(),c4.writer(),cnt, write_sleeper),
             reader(c1.reader(),0, read_sleeper, x.writer()),
             reader(c2.reader(),1, read_sleeper, x.writer()),
             reader(c3.reader(),2, read_sleeper, x.writer()),
             reader(c4.reader(),3, read_sleeper, x.writer()))

def Any2Any_Test(read_sleeper, write_sleeper):
    x = Channel()
    Spawn(check.Assert(x.reader(), "Any2Any_Test"+str(read_sleeper)+str(write_sleeper), count=40, vocabulary=[0,1,2,3]))

    c1=Channel()
    cnt = 10

    Parallel(reader(+c1,0, read_sleeper, x.writer()), writer(-c1,0,cnt, write_sleeper),
             reader(+c1,1, read_sleeper, x.writer()), writer(-c1,1,cnt, write_sleeper),
             reader(+c1,2, read_sleeper, x.writer()), writer(-c1,2,cnt, write_sleeper),
             reader(+c1,3, read_sleeper, x.writer()), writer(-c1,3,cnt, write_sleeper))

def Any_Alting2Any_Alting_Test(read_sleeper, write_sleeper):
    x = Channel()
    Spawn(check.Assert(x.reader(), "Any_Alting2Any_Alting_Test"+str(read_sleeper)+str(write_sleeper), count=160, minimum=40, vocabulary=[0,1,2,3]))

    c1=Channel()
    c2=Channel()
    c3=Channel()
    c4=Channel()

    cnt = 10
    
    Parallel(par_writer(-c1, -c2, -c3, -c4,cnt, write_sleeper),
             par_writer(-c1, -c2, -c3, -c4,cnt, write_sleeper),
             par_writer(-c1, -c2, -c3, -c4,cnt, write_sleeper),
             par_writer(-c1, -c2, -c3, -c4,cnt, write_sleeper),
             par_reader(+c1, +c2, +c3, +c4, read_sleeper, x.writer()),
             par_reader(+c1, +c2, +c3, +c4, read_sleeper, x.writer()),
             par_reader(+c1, +c2, +c3, +c4, read_sleeper, x.writer()),
             par_reader(+c1, +c2, +c3, +c4, read_sleeper, x.writer()))



def commtest():
    for read_sleep in [('Zero', None), ('One',sleep_one), ('Random',sleep_random)]:
        for write_sleep in [('Zero', None), ('One',sleep_one), ('Random',sleep_random)]:
            rname, rsleep = read_sleep
            wname, wsleep = write_sleep
            if not rsleep==wsleep==sleep_one: #No reason to test with both sleep_one
                One2One_Test(rsleep, wsleep)
                Any2One_Test(rsleep, wsleep)
                One2Any_Test(rsleep, wsleep)
                One_Alting2Any_Test(rsleep, wsleep)
                Any2Any_Test(rsleep,wsleep)
                Any_Alting2Any_Alting_Test(rsleep, wsleep)

if __name__ == '__main__':
    commtest()
    shutdown()
