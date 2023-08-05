# Cerealizer
# Copyright (C) 2005 Jean-Baptiste LAMY
#
# This program is free software.
# It is available under the Python licence.

# Small benchmark

from __future__ import print_function

import cerealizer



import time
#import psyco
#psyco.full()

class O(object):
  def __init__(self):
    self.x = 1
    self.s = "jiba"
    self.o = None
    self.l = [1, 2, 3, 4]
    
cerealizer.register(O)
cerealizer.freeze_configuration()


l = []
for i in range(20000):
  o = O()
  if l: o.o = l[-1]
  l.append(o)

print("cerealizer")
t = time.time()
s = cerealizer.dumps(l)
print("dumps in", time.time() - t, "s,", len(s), "bytes length")

t = time.time()
l2 = cerealizer.loads(s)
print("loads in", time.time() - t, "s")


import pickle

print()
print("pickle")
t = time.time()
s = pickle.dumps(l)
print("dumps in", time.time() - t, "s,", len(s), "bytes length")

t = time.time()
l2 = pickle.loads(s)
print("loads in", time.time() - t, "s")

import cPickle

print()
print("cPickle")
t = time.time()
s = cPickle.dumps(l)
print("dumps in", time.time() - t, "s,", len(s), "bytes length")

t = time.time()
l2 = cPickle.loads(s)
print("loads in", time.time() - t, "s")


import twisted.spread.jelly, twisted.spread.banana

class O(object, twisted.spread.jelly.Jellyable, twisted.spread.jelly.Unjellyable):
  def __init__(self):
    self.x = 1
    self.s = "jiba"
    self.o = None
    self.l = [1, 2, 3, 4]
    
cerealizer.register(O)
cerealizer.freeze_configuration()


l = []
for i in range(20000):
  o = O()
  if l: o.o = l[-1]
  l.append(o)


print()
print("jelly + banana")
t = time.time()
s = twisted.spread.banana.encode(twisted.spread.jelly.jelly(l))
print("dumps in", time.time() - t, "s,", len(s), "bytes length")

t = time.time()
l2 = twisted.spread.jelly.unjelly(twisted.spread.banana.decode(s))
print("loads in", time.time() - t, "s")


import twisted.spread.cBanana
twisted.spread.banana.cBanana = twisted.spread.cBanana
twisted.spread.cBanana.pyb1282int=twisted.spread.banana.b1282int
twisted.spread.cBanana.pyint2b128=twisted.spread.banana.int2b128
twisted.spread.banana._i = twisted.spread.banana.Canana()
twisted.spread.banana._i.connectionMade()
twisted.spread.banana._i._selectDialect("none")



print()
print("jelly + cBanana")
t = time.time()
s = twisted.spread.banana.encode(twisted.spread.jelly.jelly(l))
print("dumps in", time.time() - t, "s,", len(s), "bytes length")

t = time.time()
l2 = twisted.spread.jelly.unjelly(twisted.spread.banana.decode(s))
print("loads in", time.time() - t, "s")
