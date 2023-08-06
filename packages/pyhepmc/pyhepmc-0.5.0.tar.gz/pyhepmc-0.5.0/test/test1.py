#! /usr/bin/env python

from hepmc import *

reader = IO_GenEvent("../LEP10.hepmc", "r")

evtnum = 0
evt = GenEvent()
reader.fill_next_event(evt)
while evt.particles_size():
    evtnum += 1
    print "Event %d: " % evtnum, evt
    print "Particles: ", evt.particles()
    print "Num particles: ", evt.particles_size()
    print "Num vertices: ", evt.vertices_size()
    for p in evt.particles():
        print p
        m = p.momentum()
        print m
    fsps = evt.fsParticles()
    print "FS particles: ", fsps
    print "Num FS particles: ", len(fsps)
    for p in fsps:
        print p
    print "\n\n"
    evt.clear()
    evt = reader.get_next_event()
