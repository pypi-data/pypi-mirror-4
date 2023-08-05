#!/bin/env python

from struct import *
#import sys
import array
#import Gnuplot
#import matplotlib
#matplotlib.use("TkAgg")
#import pylab as P
import time

#import numpy

stime=time.time()

print "hoge"


ipaddstr="10.33.41.74"
ipaddstr="10.64.105.64"

try:
    import visa
    osc=visa.instrument(device=ipaddstr, timeout=5)
except:
    import vxi11Device
    osc=vxi11Device.Vxi11Device(host=ipaddstr, device="inst0,0")
#


stime=time.time()

#### COMMAND & RESPONSE TEST ####
print osc.ask("*IDN?")
print osc.ask("TRDL?")
print osc.ask("TDIV?")
print osc.ask("MSIZ?")
print osc.write("WFSU NP, 20000")
print osc.ask("WFSU?")
#### WORKS WELL ####

##### ANALYZING WAVEFORM DESC TEST #####
#
offset=16
osc.write('C1:WAVEFORM? DESC')
#descbin=osc.read()
#time.sleep(0.05)
for i in range(0,6):
    temp=osc.read_raw()
    if temp==None:
        print i, temp
    else:
        print i, array.array('c',temp[:]).tolist()
#print len(descbin)
#print unpack('ccccc',descbin[0:5])
#print array.array('c',descbin[6:16]).tolist()
#print array.array('c',descbin[:]).tolist()

#sys.exit()
