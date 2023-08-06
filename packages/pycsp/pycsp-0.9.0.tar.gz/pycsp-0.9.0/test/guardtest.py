"""
Copyright (c) 2009 John Markus Bjoerndalen <jmb@cs.uit.no>,
      Brian Vinter <vinter@nbi.dk>, Rune M. Friborg <rune.m.friborg@gmail.com>.
See LICENSE.txt for licensing details (MIT License). 
"""

from pycsp_import import *
import time
import random

@io
def sleep_long():
    time.sleep(2)

@io
def sleep_random():
    time.sleep(random.random()/2)

@io
def sleep_long_random():
    time.sleep(random.random()*2)


@process
def writer(cout, id, cnt, sleeper):
    for i in range(cnt):
        if sleeper: sleeper()
        cout((id, i))

@process
def par_reader_skip_sel(cin1,cin2,cin3,cin4, cnt, sleeper):
    for i in range(cnt*4):
        if sleeper: sleeper()

        c, msg = PriSelect(
            InputGuard(cin1),
            InputGuard(cin2),
            SkipGuard(),
            InputGuard(cin3),
            InputGuard(cin4)
            )

        print 'From ',c ,'got',msg
    retire(cin1, cin2, cin3, cin4)

@process
def par_reader_timeout_sel(cin1,cin2,cin3,cin4, cnt, sleeper):
    for i in range(cnt*4):
        if sleeper: sleeper()

        c, msg = PriSelect(
            InputGuard(cin1),
            InputGuard(cin2),
            InputGuard(cin3),
            InputGuard(cin4),
            TimeoutGuard(seconds=0.1)
            )

        print 'From ',c ,'got',msg
    retire(cin1, cin2, cin3, cin4)

@process
def par_reader_skip_exec(cin1,cin2,cin3,cin4, cnt, sleeper):
    for i in range(cnt*4):
        if sleeper: sleeper()

        PriSelect(
            InputGuard(cin1, action="print 'From cin1 got', channel_input"),
            InputGuard(cin2, action="print 'From cin2 got', channel_input"),
            SkipGuard(action="print 'SkipGuard()'"),
            InputGuard(cin3, action="print 'From cin3 got', channel_input"),
            InputGuard(cin4, action="print 'From cin4 got', channel_input")
            )

    retire(cin1, cin2, cin3, cin4)

@process
def par_reader_timeout_exec(cin1,cin2,cin3,cin4, cnt, sleeper):
    for i in range(cnt*4):
        if sleeper: sleeper()

        PriSelect(
            InputGuard(cin1, action="print 'From cin1 got', channel_input"),
            InputGuard(cin2, action="print 'From cin2 got', channel_input"),
            InputGuard(cin3, action="print 'From cin3 got', channel_input"),
            InputGuard(cin4, action="print 'From cin4 got', channel_input"),
            TimeoutGuard(seconds=0.1, action="print 'TimeoutGuard(seconds=0.1)'")
            )

    retire(cin1, cin2, cin3, cin4)


def Any2One_Alting_Test(par_reader, read_sleeper, write_sleeper):
    c1=Channel()
    c2=Channel()
    c3=Channel()
    c4=Channel()

    cnt = 10
    
    Parallel(par_reader(c1.reader(),c2.reader(),c3.reader(),c4.reader(),cnt, read_sleeper),
             writer(c1.writer(),0,cnt, write_sleeper),
             writer(c2.writer(),1,cnt, write_sleeper),
             writer(c3.writer(),2,cnt, write_sleeper),
             writer(c4.writer(),3,cnt, write_sleeper))


def Any2Any_Alting_Test(par_reader, read_sleeper, write_sleeper):
    c1=Channel()
    c2=Channel()
    c3=Channel()
    c4=Channel()

    cnt = 40
    
    Parallel(par_reader(+c1,+c2,+c3,+c4,cnt, read_sleeper),
             writer(-c1,0,cnt, write_sleeper),
             writer(-c1,1,cnt, write_sleeper),
             writer(-c1,2,cnt, write_sleeper),
             writer(-c1,3,cnt, write_sleeper),
             writer(-c2,4,cnt, write_sleeper),
             writer(-c2,5,cnt, write_sleeper),
             writer(-c2,6,cnt, write_sleeper),
             writer(-c2,7,cnt, write_sleeper),
             writer(-c3,8,cnt, write_sleeper),
             writer(-c3,9,cnt, write_sleeper),
             writer(-c3,10,cnt, write_sleeper),
             writer(-c3,11,cnt, write_sleeper),
             writer(-c4,12,cnt, write_sleeper),
             writer(-c4,13,cnt, write_sleeper),
             writer(-c4,14,cnt, write_sleeper),
             writer(-c4,15,cnt, write_sleeper))


if __name__ == '__main__':
    print "Any2One_Alting_Test(par_reader_skip_sel, sleep_random, sleep_random)"
    Any2One_Alting_Test(par_reader_skip_sel, sleep_random, sleep_random)
    print

    print "Any2One_Alting_Test(par_reader_timeout_sel, sleep_random, sleep_long_random)"
    Any2One_Alting_Test(par_reader_timeout_sel, sleep_random, sleep_long_random)
    print

    print "Any2One_Alting_Test(par_reader_skip_exec, sleep_random, sleep_random)"
    Any2One_Alting_Test(par_reader_skip_exec, sleep_random, sleep_random)
    print

    print "Any2One_Alting_Test(par_reader_timeout_exec, sleep_random, sleep_long_random)"
    Any2One_Alting_Test(par_reader_timeout_exec, sleep_random, sleep_long_random)
    print

    print "Any2Any_Alting_Test(par_reader_skip_sel, None, sleep_long)"
    Any2Any_Alting_Test(par_reader_skip_sel, None, sleep_long)
    print

    print "Any2Any_Alting_Test(par_reader_timeout_sel, None, sleep_long)"
    Any2Any_Alting_Test(par_reader_timeout_sel, None, sleep_long)
    print

        
    shutdown()
