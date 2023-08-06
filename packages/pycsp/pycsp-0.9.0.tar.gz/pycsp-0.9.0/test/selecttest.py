"""
Copyright (c) 2009 John Markus Bjoerndalen <jmb@cs.uit.no>,
      Brian Vinter <vinter@nbi.dk>, Rune M. Friborg <rune.m.friborg@gmail.com>.
See LICENSE.txt for licensing details (MIT License). 
"""

from pycsp_import import *
import time
import random

@io
def sleep_random():
    time.sleep(random.random()/10)

@process
def writer(cout, id, cnt, sleeper):
    for i in range(cnt):
        if sleeper: sleeper()
        cout((id, i))
    
@process
def par_reader(cin1,cin2,cin3,cin4, cnt, sleeper):
    for i in range(cnt*4):
        if sleeper: sleeper()
        
        c, msg = AltSelect(
            InputGuard(cin1),
            InputGuard(cin2),
            InputGuard(cin3),
            InputGuard(cin4)
            )
            
        print 'From ',c ,'got',msg

@process
def par_reader_pri(cin1,cin2,cin3,cin4, cnt, sleeper):
    for i in range(cnt*4):
        if sleeper: sleeper()
        
        c, msg = PriSelect(
            InputGuard(cin1),
            InputGuard(cin2),
            InputGuard(cin3),
            InputGuard(cin4)
            )
            
        print 'From ',c ,'got',msg

@process
def par_reader_fair(cin1,cin2,cin3,cin4, cnt, sleeper):
    for i in range(cnt*4):
        if sleeper: sleeper()
        
        c, msg = FairSelect(
            InputGuard(cin1),
            InputGuard(cin2),
            InputGuard(cin3),
            InputGuard(cin4)
            )
            
        print 'From ',c ,'got',msg


def Any2One_Alting_Test(par_reader, read_sleeper, write_sleeper):
    c1=Channel()
    c2=Channel()
    c3=Channel()
    c4=Channel()

    cnt = 10
    
    Parallel(par_reader(+c1,+c2,+c3,+c4,cnt, read_sleeper),
             writer(-c1,0,cnt, write_sleeper),
             writer(-c2,1,cnt, write_sleeper),
             writer(-c3,2,cnt, write_sleeper),
             writer(-c4,3,cnt, write_sleeper))

if __name__ == '__main__':
    print "Any2One_Alting_Test - AltSelect"
    Any2One_Alting_Test(par_reader, sleep_random, sleep_random)
    print "Any2One_Alting_Test - PriSelect"
    Any2One_Alting_Test(par_reader_pri, sleep_random, sleep_random)
    print "Any2One_Alting_Test - FairSelect"
    Any2One_Alting_Test(par_reader_fair, sleep_random, sleep_random)

    shutdown()
