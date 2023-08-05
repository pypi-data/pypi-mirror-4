#!/bin/env python
# -*- coding: shift_jis -*-

from Tkinter import *
import tkMessageBox
import tkFileDialog
#import ca
import os
import glob
import popen2
import subprocess
import time
import datetime
import string
import Gnuplot
import math
import  numpy
from scipy import *

import struct

#import visa
import vxi11Device

import array

import pylab as P

from optparse import OptionParser


def gen_mountains(slices=None, usetimeconv=0, usephase=0, phfact=720, plottedslicenum=None):
    if len(slices)==0:
        print "no data yet, return"
        return
    mountains=[]

    if usetimeconv==1:
        usetime=1
    else:
        usetime=0

    unittime=slices.unittime*1.0e9 # in ns
    print "unit time is %f" % unittime

    if usephase==1:
        for num in plottedslicenum:
            try:
                time=unittime*len(slices[num])/1.0e3 # in ms
                if usetime==0:
                    mountains.append(map(lambda x, z: 
                                         (phfact*x/(unittime*len(slices[num])), num, z), \
                                             slices.slicetime, \
                                             slices[num]))
                else:
                    mountains.append(map(lambda x, z: 
                                              (phfact*x/(unittime*len(slices[num])), slices.slicetimelist[num], z), \
                                                  slices.slicetime, \
                                                  slices[num]))
            except IndexError:
                print num
                print "index error, break"
                break
    else:
        for num in plottedslicenum:
            try:
                time=unittime*len(slices[num])/1.0e3 # in ms
                if usetime==0:
                    mountains.append(map(lambda x, z: (x, num, z), slices.slicetime, \
                                                  slices[num]))
                else:
                    mountains.append(map(lambda x, z: (x, slices.slicetimelist[num], z), slices.slicetime, \
                                                  slices[num]))
            except IndexError:
                print num
                print "index error, break"
                break


    tmpfile=open("c:/tmp/tempfile.txt","w")
    for mountain in mountains:
        for xyz in mountain:
            x, y, z = xyz
            if z==None: 
                break
            tmpfile.write("%.9f\t%f\t%s\n" % (x, y, z))
        tmpfile.write("\n")


def genuniqfolder_file_set(datefilename=True, prefix="wfm", suffix1="ch1", suffix2="ch2",
                           ext="txt"):
    date=datetime.date.today().strftime('%y%m%d')
    if not os.path.isdir(date):
        print "generate folder '%s'." % date
        os.makedirs(date)
    else:
        print "use existing folder."
    i=0
    while True:
        if datefilename:
            tempfilename1=os.path.join(".",date,prefix+date+"_%02d_%s."% (i, suffix1)+ext)
            tempfilename2=os.path.join(".",date,prefix+date+"_%02d_%s."% (i, suffix2)+ext)
        else:
            tempfilename1=os.path.join(".",date,prefix+"_%02d_%s."%(i, suffix1)+ext)
            tempfilename2=os.path.join(".",date,prefix+"_%02d_%s."%(i, suffix1)+ext)
        if not (os.path.exists(tempfilename1) or os.path.exists(tempfilename2)):
            break
        i+=1
    filenamewithpath1=tempfilename1
    filenamewithpath2=tempfilename2
#    print filenamewithpath1, filenamewithpath2
    return filenamewithpath1, filenamewithpath2


def genuniqplot(prefix="plot", ext="png"):
    date=datetime.date.today().strftime('%y%m%d')
    i=0
    while True:
        tempfilename=prefix+date+"_%02d."%(i)+ext
        if not os.path.exists(tempfilename):
            break
        i+=1
    filename=tempfilename
    return filename

def genuniqfilename(prefix="temp", ext="txt"):
    date=datetime.date.today().strftime('%y%m%d')
    i=0
    while True:
        tempfilename=prefix+date+"_%02d."%(i)+ext
        if not os.path.exists(tempfilename):
            break
        i+=1
    filename=tempfilename
    return filename



def lecroy_wfm_analyze(waveform, withtimes=False, withwavedesc=False):
    offset=15 # for ALL blocks both WP950, WP715i, KIME-UCHI
    instrument_name=array.array('c',waveform[offset+76:offset+92]).tostring().strip('\x00')
    cord = struct.unpack('b',waveform[offset+34])[0]
    endian, endiandouble = endian_set(cord, instrument_name)

#    print instrument_name, len(instrument_name)
    wavedesclen=struct.unpack('%sl'%endian,waveform[offset+36:offset+40])[0]
    usertextlen=struct.unpack('%sl'%endian,waveform[offset+40:offset+44])[0]
    regdesclen=struct.unpack('%sl'%endian,waveform[offset+44:offset+48])[0]
    trigtimearraylen=struct.unpack('%sl'%endian,waveform[offset+48:offset+52])[0]
    ristimearraylen=struct.unpack('%sl'%endian,waveform[offset+52:offset+56])[0]
    resarraylen=struct.unpack('%sl'%endian,waveform[offset+52:offset+56])[0]
    wavearray1len=struct.unpack('%sl'%endian,waveform[offset+60:offset+64])[0]
    wavearray2len=struct.unpack('%sl'%endian,waveform[offset+64:offset+68])[0]

    wavearrayoffset=offset+wavedesclen+usertextlen+regdesclen+trigtimearraylen+ristimearraylen+resarraylen
#    print wavearrayoffset
#    print array.array('c',waveform[wavearrayoffset:wavearrayoffset+100]).tolist()


    vgain=struct.unpack('%sf'%endian,waveform[156+offset:160+offset])[0]
    voffset=struct.unpack('%sf'%endian,waveform[160+offset:164+offset])[0]
    vunit=struct.unpack('c',waveform[196+offset])[0]
#    print "vertical gain = %e" % vgain
#    print "vertical offset = %e" % voffset
#    print "vertical unit = %r" % vunit

    hinterval=struct.unpack('%sf'%endian,waveform[176+offset:180+offset])[0]
    hoffset=struct.unpack('%sd'%endiandouble,waveform[180+offset:188+offset])[0]
    hunit=struct.unpack('c',waveform[244+offset])[0]
    sparcing_factor=struct.unpack('%sl'%endian,waveform[136+offset:140+offset])[0]
#    print "spacing factor = %d" % sparcing_factor
#    print "horizontal interval = %e" % hinterval
#    print "horizontal offset = %e" % hoffset
#    print "horizontal unit = %r" % hunit

    datanum=struct.unpack('%sl'%endian,waveform[116+offset:120+offset])[0]
#    print "wavearraydatalen:", wavearray1len
    dataarray=numpy.fromstring(waveform[wavearrayoffset:wavearrayoffset+wavearray1len], dtype=numpy.int8)
    data=dataarray*vgain-voffset
    if sparcing_factor==0:
        tdata=numpy.array(map(lambda i: hinterval*i+hoffset, range(0,datanum)))
    else:
        tdata=numpy.array(map(lambda i: hinterval*i*sparcing_factor+hoffset, range(0,datanum)))
#    print len(data)
#    print datanum

    if withtimes==False:
        if withwavedesc==False:
            return data
        else:
            return data, waveform[:offset+wavedesclen]
    else:
        if withwavedesc==False:
            return tdata, data
        else:
            return tdata, data, waveform[:offset+wavedesclen]



def endian_set(cord, instrument_name):
    if cord==1: # LO FIRST
        endian="<"
        if instrument_name=="LECROYWP950VL":
            endiandouble="<"
        else:
#            print "WP715zi"
            endiandouble="<"
    else: # HI FIRST
        endian=">"
        if instrument_name=="LECROYWP950VL":
            endiandouble=">"
        else:
#            print "WP715zi"
            endiandouble=">"
    return endian, endiandouble

class WfmSlice(list):
    def __init__(self):
        list.__init__(self)


    def set_param_from_lecroy_wfm(self, waveform):
        offset=15
        instrument_name=array.array('c',waveform[offset+76:offset+92]).tostring().strip('\x00')
        cord = struct.unpack('b',waveform[offset+34])[0]

        endian, endiandouble = endian_set(cord, instrument_name)

        self.hinterval=struct.unpack('%sf'%endian,waveform[176+offset:180+offset])[0]
        self.sparcing_factor=struct.unpack('%sl'%endiandouble,waveform[136+offset:140+offset])[0]
        if self.sparcing_factor != 0:
            self.unittime=self.hinterval*self.sparcing_factor
        else:
            self.unittime=self.hinterval

        self.subarray_count=struct.unpack('%sl'%endian,waveform[offset+144:offset+148])[0]
#        print self.subarray_count

    def gen_segment(self, clkdata=None, wfmdata=None, seg_point=5002, rfclkharmonic=1):
        # making slices
        samples=len(wfmdata)
        unittime=self.unittime

        print "one segment length is %d points" % seg_point
        
        hldcnt=0
#        hldoff=self.hldoff.get()
#        clkfifo=self.fifoinit(self.clkdelay.get())
#        datafifo=self.fifoinit(self.datadelay.get())

        self.slicetimelist=[]
        del(self[:])
        tempslice=[]
        slicenum=0

        if rfclkharmonic==1:
            harmonic=1
        else: 
            harmonic=2
#        print "use rf clk of h=%d" % harmonic

        totaltime=0.0

        cnt=1
        for i in range(1,samples):
            if i%seg_point==0:
                #print len(tempslice)
                slicenum+=1
                self.append(tempslice)
                self.slicetimelist.append(totaltime)
#                totaltime=totaltime+len(tempslice)*unittime*1.0e-6
                totaltime=totaltime+len(tempslice)*unittime
#                print totaltime
                tempslice=[]
                cnt+=1
            tempslice.append(wfmdata[i])

        if slicenum<=0:
            print "no slice found, change threshold?"
            return

        if self==[]:
            print "no slice found, change threshold?"
            return

        print "number of slices: ", len(self)
        self.slicelen=len(self)

        self.imax=max(map(len, self))

        self.slicetime=map(lambda x: unittime*x*1e9 , range(0,self.imax))


    def gen_slice(self, clkdata=None, wfmdata=None, thlevel=0.5, hldoff=0, clkdelay=0, datadelay=0, rfclkharmonic=1):
        unittime=self.unittime

        waiting=False # 0: not waiting, 1: waiting
        samples=len(clkdata)
        
        hldcnt=0
        clkfifo=self.fifoinit(clkdelay)
        datafifo=self.fifoinit(datadelay)

        self.slicetimelist=[]
        del(self[:]) # delete all slices
        tempslice=[]
        slicenum=0

        harmonic=rfclkharmonic
        print "use rf clk of h=%d" % harmonic

        totaltime=0.0

        cnt=1
        for i in range(0,samples):
            clkfifo.append(clkdata[i])
            rfclk=clkfifo.pop(0)
            if waiting and rfclk>thlevel:
                if not cnt%harmonic:
                    slicenum+=1
                    waiting=False
                    hldcnt=0
                    self.append(tempslice)
                    self.slicetimelist.append(totaltime)
                    totaltime=totaltime+len(tempslice)*unittime*1.0e3
                    tempslice=[]
                    cnt+=1
#                    print cnt, cnt % harmonic
                else:
                    waiting=False
                    hldcnt=0
                    cnt+=1
#                    print cnt, cnt % harmonic
            elif rfclk<=thlevel and hldcnt > hldoff:
                waiting=True
            datafifo.append(wfmdata[i])
            tempslice.append(datafifo.pop(0))
            hldcnt+=1

        if slicenum<=1:
            print "no slice found, change threshold?"
            return

        if self==[]:
            print "no slice found, change threshold?"
            return
        self.pop(0) # the first does not make sense

        print "number of slices: ", len(self)
        self.slicelen=len(self)

        self.imax=max(map(len, self))

        self.slicetime=map(lambda x: unittime*x*1e9 , range(0,self.imax))


    def fifoinit(self, fifolen):
        fifo=[]
        for i in range(0, fifolen):
            fifo.append(0)
        return fifo

class FileSel(Frame):
    def init(self):
        Label(self, text=self.text).pack(anchor='w')
        e=Entry(self, textvariable=self.filename, width=20)
        e.pack(side=LEFT)
        Button(self, text = "browse", command = self.browse).pack(side=LEFT)

  # ボタンが押されたときの処理
    def browse(self): 
        filename = tkFileDialog.askopenfilename(parent=self.master,\
                                                    title='Choose a file')
        if filename:
            print filename
            self.filename.set(filename)
#            self.basename.set(os.path.basename(filename))
#            print self.basename.get()

    def getFullPath(self):
        return self.filename.get()

  # ここから後も定石ということで
    def __init__(self, master=None, defaultfilename=None, text=None):
        Frame.__init__(self, master)
#        self.basename=StringVar()
#        self.basename.set(defaultfilename)
        self.filename=StringVar()
        self.filename.set(defaultfilename)
        self.text=text
        self.init()
        self.pack()


class FileIn(LabelFrame):
    def __init__(self, master):
        LabelFrame.__init__(self, master)
        self.configure(text="input file")
        self.init()
        self.pack()

    def init(self):
        self.infileSel_clk=FileSel(self, defaultfilename="wfm_ch1.trc",\
                               text="clk file for replot")
        self.infileSel_clk.pack()
        self.infileSel_beam=FileSel(self, defaultfilename="wfm_ch2.trc",\
                               text="beam signal file for replot")
        self.infileSel_beam.pack()
        self.clkfilename=self.infileSel_clk.filename
        self.beamfilename=self.infileSel_beam.filename
        

class LecroyOSC(vxi11Device.Vxi11Device):
    def __init__(self, device, timeout=5):
        #visa.Instrument.__init__(self, device, timeout=timeout)
        vxi11Device.Vxi11Device.__init__(self, host=device, device="inst0,0")
        self.device=device
        self.timeout=timeout
        self.write("CHDR OFF") # always header off

        self.IDN_Str=self.IDN()
        ID=self.IDN_Str[:-1].split(",")
        self.Make=ID[0]
        self.Model=ID[1]
        self.Option=ID[3]

    def reconnect(self):
        vxi11Device.Vxi11Device.__init__(self, host=self.device,
                                         device="inst0,0")
        #visa.Instrument.__init__(self, self.device, timeout=self.timeout)
        self.write("CHDR OFF") # always header off

        self.IDN_Str=self.IDN()
        ID=self.IDN_Str[:-1].split(",")
        self.Make=ID[0]
        self.Model=ID[1]
        self.Option=ID[3]
        

    def IDN(self):
        return self.ask("*IDN?;")

    def time_div(self, value=None, tonum=False):
        if value==None:
            if tonum==True:
                return float(self.ask("TDIV?"))
            else:
                return self.ask("TDIV?")
        else:
            try:
                self.write("TDIV %f" % value)
            except TypeError:
                self.write("TDIV %s" % value)

    def volt_div(self, ch=1, value=None, tonum=False):
        trace=("C1","C2","C3","C4", "TA", "TB", "TC","TD",
               "M1","M2","M3","M4")
        if (ch in trace):
            chstr="%s" % ch
        elif (ch in (1,2,3,4)):
            chstr="C%d" % ch

        if value==None:
            if tonum==True:
                return float(self.ask("%s:VDIV?"%chstr))
            else:
                return self.ask("%s:VDIV?"%chstr)
        else:
            try:
                self.write("%s:VDIV %f" % (chstr,value))
            except TypeError:
                self.write("%s:VDIV %s" % (chstr,value))

    def offset(self, ch=1, value=None, tonum=False):
        trace=("C1","C2","C3","C4", "TA", "TB", "TC","TD",
               "M1","M2","M3","M4")
        if (ch in trace):
            chstr="%s" % ch
        elif (ch in (1,2,3,4)):
            chstr="C%d" % ch
        if value==None:
            if tonum==True:
                return float(self.ask("%s:OFST?"%chstr))
            else:
                return self.ask("%s:OFST?"%chstr)
        else:
            try:
                self.write("%s:OFST %f" % (chstr,value))
            except TypeError:
                self.write("OFST %s" % (chstr,value))


    def trig_delay(self, value=None, tonum=False):
        if value==None:
            if tonum==True:
                return float(self.ask("TRDL?"))
            else:
                return self.ask("TRDL?")
        else:
            try:
                self.write("TRDL %f" % value)
            except TypeError:
                self.write("TRDL %s" % value)


    def trig_mode(self, mode=None):
        trig=("AUTO","NORM","SINGLE","STOP")
        if mode==None:
            return self.ask("TRMD?")
        else:
            if (mode in trig):
                self.write("TRMD %s" % mode)
            elif isinstance(mode, int):
                self.write("TRMD %s" % trig[mode])

    def memory_size(self):
        """mem size set is not yet implemented yet"""
        return self.ask("MSIZ?")

    def comm_order(self):
        """comm order set set is not yet implemented yet"""
        return self.ask("CORD?")

    def sequence(self):
        # MSIZE 
        return self.ask("SEQ?")

    def get_waveform(self, ch, np=0, fp=0, sp=0):
        trace=("C1","C2","C3","C4", "TA", "TB", "TC","TD",
               "M1","M2","M3","M4")
        if (ch in trace):
            self.write("WFSU NP, %d, FP, %d, SP, %d" % (np,fp,sp))
            return self.ask("%s:WAVEFORM?" % ch)
        elif (ch in (1,2,3,4)):
            self.write("WFSU NP, %d, FP, %d, SP, %d" % (np,fp,sp))
            return self.ask("C%d:WAVEFORM?" % ch)

class ScopeControl(Frame):
    def __init__(self, master, osc=("10.8.47.32","inst0,0")):
        Frame.__init__(self, master)

        self.osc=LecroyOSC(osc, timeout=30)

        self.init()
        self.pack()

    def init(self):
        self.IDN_str=StringVar()
        self.memory_size_str=StringVar()
        self.trig_delay_str=StringVar()
        self.time_div_str=StringVar()

#        self.volt_div_str=StringVar()
#        self.offset_str=StringVar()

        self.trig_mode_str=StringVar()
        self.sequence_str=StringVar()

        self.trig_delay_set=DoubleVar()
        self.time_div_set=DoubleVar()
#        self.volt_div_set=DoubleVar()
#        self.offset_set=DoubleVar()
        self.trig_mode_set=StringVar()


        ftemp=LabelFrame(self, text="readback"); ftemp.pack()
        ftemp2=Frame(ftemp); ftemp2.pack(anchor=NW)
        Label(ftemp2, text="IDN: ").pack(side=LEFT)
        Label(ftemp2, textvariable=self.IDN_str).pack()
        ftemp2=Frame(ftemp); ftemp2.pack(anchor=NW)
        Label(ftemp2, text="memory size: ").pack(side=LEFT)
        Label(ftemp2, textvariable=self.memory_size_str).pack()
        ftemp2=Frame(ftemp); ftemp2.pack(anchor=NW)
        Label(ftemp2, text="trig delay [s]: ").pack(side=LEFT)
        Label(ftemp2, textvariable=self.trig_delay_str).pack()
        ftemp2=Frame(ftemp); ftemp2.pack(anchor=NW)
        Label(ftemp2, text="time div [s]: ").pack(side=LEFT)
        Label(ftemp2, textvariable=self.time_div_str).pack()
#         ftemp2=Frame(ftemp); ftemp2.pack(anchor=NW)
#         Label(ftemp2, text="volt div [V]: ").pack(side=LEFT)
#         Label(ftemp2, textvariable=self.volt_div_str).pack()
#         ftemp2=Frame(ftemp); ftemp2.pack(anchor=NW)
#         Label(ftemp2, text="volt offset [V]: ").pack(side=LEFT)
#         Label(ftemp2, textvariable=self.offset_str).pack()
        ftemp2=Frame(ftemp); ftemp2.pack(anchor=NW)
        Label(ftemp2, text="trig mode: ").pack(side=LEFT)
        Label(ftemp2, textvariable=self.trig_mode_str).pack()
        ftemp2=Frame(ftemp); ftemp2.pack(anchor=NW)
        Label(ftemp2, text="sequence mode: ").pack(side=LEFT)
        Label(ftemp2, textvariable=self.sequence_str).pack()


        Button(ftemp, text="readback", bg="white", command=self.readback).pack()

        self.readback()
        self.readback_to_set_val()


        ftemp=LabelFrame(self, text="setting"); ftemp.pack()
        Label(ftemp, text="trig mode: ").pack(anchor=W)
        ftemp2=Frame(ftemp); ftemp2.pack(anchor=NW)
        self.trmdtuple=("NORM","SINGLE","STOP","AUTO")
        for text in self.trmdtuple:
             b=Radiobutton(ftemp2, text=text, variable=self.trig_mode_set, value=text)
             b.pack()
        Button(ftemp2, text="set", bg="white", command=self.set_trig_mode).pack(side=LEFT)
        ftemp2=Frame(ftemp); ftemp2.pack(anchor=NW)
        Label(ftemp2, text="time div [s]: ", width=15).pack(side=LEFT)
        Entry(ftemp2, width=10, textvariable=self.time_div_set).pack(side=LEFT)
        Button(ftemp2, text="set", bg="white", command=self.set_time_div).pack(side=LEFT)
        ftemp2=Frame(ftemp); ftemp2.pack(anchor=NW)
        Label(ftemp2, text="trig delay [s]: ", width=15).pack(side=LEFT)
        Entry(ftemp2, width=10, textvariable=self.trig_delay_set).pack(side=LEFT)
        Button(ftemp2, text="set", bg="white", command=self.set_trig_delay).pack(side=LEFT)
#         ftemp2=Frame(ftemp); ftemp2.pack(anchor=NW)
#         Label(ftemp2, text="volt div [V]: ", width=15).pack(side=LEFT)
#         Entry(ftemp2, width=10, textvariable=self.volt_div_set).pack(side=LEFT)
#         Button(ftemp2, text="set", bg="white", command=self.set_volt_div).pack(side=LEFT)
#         ftemp2=Frame(ftemp); ftemp2.pack(anchor=NW)
#         Label(ftemp2, text="volt offset [V]: ", width=15).pack(side=LEFT)
#         Entry(ftemp2, width=10, textvariable=self.offset_set).pack(side=LEFT)
#         Button(ftemp2, text="set", bg="white", command=self.set_offset).pack(side=LEFT)

        Button(self, text="recconect scope", command=self.reconnect, bg="white").pack()

    def reconnect(self):
        self.osc.reconnect()

    def readback_to_set_val(self):
        self.trig_mode_set.set(self.trig_mode_str.get())
        self.trig_delay_set.set(self.trig_delay_str.get())
        self.time_div_set.set(self.time_div_str.get())
#        self.volt_div_set.set(self.volt_div_str.get())
#        self.offset_set.set(self.offset_str.get())

    def readback(self):
        self.IDN_str.set(self.osc.IDN())
        self.memory_size_str.set(self.osc.memory_size())
        self.trig_delay_str.set(self.osc.trig_delay())
        self.time_div_str.set(self.osc.time_div())
#        self.volt_div_str.set(self.osc.volt_div())
#        self.offset_str.set(self.osc.offset())
        self.trig_mode_str.set(self.osc.trig_mode())
        self.sequence_str.set(self.osc.sequence())

    def set_trig_mode(self):
        self.osc.trig_mode(self.trig_mode_set.get())

    def set_trig_delay(self):
        self.osc.trig_delay(self.trig_delay_set.get())

#    def set_volt_div(self):
#        self.osc.volt_div(self.volt_div_set.get())

    def set_time_div(self):
        self.osc.time_div(self.time_div_set.get())

#    def set_offset(self):
#        self.osc.offset(self.offset_set.get())

class SliceGenerator(LabelFrame):
    def __init__(self, master=None):
        LabelFrame.__init__(self, master)
        self.configure(text="slice parameter")
        self.init()
        self.pack()

    def init(self):
        self.thlevel=DoubleVar()
        self.thlevel.set(0.5)
        self.hldoff=IntVar()
        self.hldoff.set(0)

        self.clkdelay=IntVar()
        self.clkdelay.set(484)
        self.datadelay=IntVar()
        self.datadelay.set(0)

        self.numpoint_slice=IntVar() # for segment
        self.numpoint_slice.set(5002)

        f1=Frame(self)
        f1.pack()
        Label(f1,text="clk threshold [V]").pack()
        Entry(f1, textvariable=self.thlevel, width=10).pack()
        Label(f1,text="trig holdoff [samples]").pack()
        Entry(f1, textvariable=self.hldoff, width=10).pack()
        Label(f1,text="clk delay [samples]").pack()
        Entry(f1, textvariable=self.clkdelay, width=10).pack()
        Label(f1,text="data delay [samples]").pack()
        Entry(f1, textvariable=self.datadelay, width=10).pack()

        Label(f1,text="num of points in each segment\n(only segment)").pack()
        Entry(f1, textvariable=self.numpoint_slice, width=10).pack()

    def analyze_desc_gen_slices(self, slices=None, wavedesc=None, rfclkdata=None, beamdata=None):
        self.slices=slices
        self.wavedesc=wavedesc
        self.rfclkdata=rfclkdata
        self.beamdata=beamdata

#        print len(self.wavedesc)

        self.slices.set_param_from_lecroy_wfm(self.wavedesc)
        if self.slices.subarray_count<=1:
            print "mountain is generated by clk"
            clkdelay=self.clkdelay.get()
            thlevel=self.thlevel.get()
            hldoff=self.hldoff
            datadelay=self.datadelay.get()
            self.slices.gen_slice(clkdata=self.rfclkdata, wfmdata=self.beamdata, thlevel=thlevel, hldoff=hldoff, 
                                  clkdelay=clkdelay, datadelay=datadelay)
        else:
            print "segment mountain"
            seg_point=self.numpoint_slice.get()
            self.slices.gen_segment(clkdata=self.rfclkdata, wfmdata=self.beamdata, seg_point=seg_point)
        
class WaveformTransfer(LabelFrame):
    def __init__(self, master=None, osc=None):
        LabelFrame.__init__(self, master)
        self.configure(text="WF transfer")
        self.osc=osc
        self.init()
        self.pack()
    
    def init(self):
        Label(self,text=self.osc.Model).pack()
        self.rfclkch=IntVar()
        self.rfclkch.set(1)
        self.datach=IntVar()
        self.datach.set(2)
        self.maxsample=IntVar()
        self.maxsample.set(1000000)

        self.firstpoint=IntVar()
        self.firstpoint.set(0)
        self.firstpoint_million=IntVar()
        self.firstpoint_million.set(0)

        self.sparcing=IntVar()
        self.sparcing.set(1)

        self.rfclkwaveform=numpy.array([])
        self.beamwaveform=numpy.array([])



        ftemp5=Frame(self); ftemp5.pack()
        Label(ftemp5,text="RF/revolutin clk channel").pack()
        Spinbox(ftemp5, from_=1, to=4, increment=1, \
                textvariable=self.rfclkch, width=2).pack()
        
        Label(ftemp5,text="beam signal channel").pack()
        Spinbox(ftemp5, from_=1, to=4, increment=1, \
                textvariable=self.datach, width=2).pack()

        Label(ftemp5,text="transfer points").pack()
        Entry(ftemp5, textvariable=self.maxsample, width=8).pack()

        Label(ftemp5,text="transfer first point").pack()
        Entry(ftemp5, textvariable=self.firstpoint, width=8).pack()

        ftemp=Frame(ftemp5)
        ftemp.pack()
        Label(ftemp, text="in M:").pack(side=LEFT)
        Spinbox(ftemp, from_=0, to=4, increment=1, \
                    textvariable=self.firstpoint_million, \
                    width=2).pack(side=LEFT)
        self.firstpoint_million.trace_variable("w", self.cbfp)

        Label(ftemp5,text="transfer sparcing factor").pack()
        Spinbox(ftemp5, textvariable=self.sparcing, from_=1, to=100, \
                    increment=1,width=3).pack()

    def cbfp(self,*args):
#        print "set first point."
        self.firstpoint.set(self.firstpoint_million.get()*10**6)

    def get_waveforms(self):
        trig_mode_before=self.osc.trig_mode()
        self.osc.trig_mode("STOP")
        maxiter=1000
        while 1:
            if self.osc.trig_mode()=="STOP":
                break
            time.sleep(0.1)
        np=self.maxsample.get()
        fp=self.firstpoint.get()
        sp=self.sparcing.get()
        rfclkch=self.rfclkch.get()
        beamch=self.datach.get()
        self.rfclkwaveform=self.osc.get_waveform(rfclkch, fp=fp, np=np, sp=sp)
        self.beamwaveform=self.osc.get_waveform(beamch, fp=fp, np=np, sp=sp)
        self.osc.trig_mode(trig_mode_before)

        return self.rfclkwaveform, self.beamwaveform

class BfPlotGen(LabelFrame):
    def __init__(self, master, slices=None):
        LabelFrame.__init__(self, master)
        self.configure(text="bf plot parameter")
        self.slices=slices
        self.init()
        self.pack()
    def init(self):
        self.usetimeconv=IntVar() # 0: unuse, 1: use
        self.usetimeconv.set(0)

        self.turnfrom=IntVar()
        self.turnfrom.set(0)
        self.turnto=IntVar()
        self.turnto.set(1000)
        self.turnevery=IntVar()
        self.turnevery.set(1)

        f7=Frame(self)
        f7.pack()
        ftemp=Frame(f7)
        ftemp.pack(anchor=NE)
        Label(ftemp, text="index from: ").pack(side=LEFT)
        Entry(ftemp, textvariable=self.turnfrom, width=6).pack(side=LEFT)
        ftemp=Frame(f7)
        ftemp.pack(anchor=NE)
        Button(ftemp, text="use last slice", command=lambda: self.turnto.set(len(self.slices)))\
            .pack(side=LEFT)
        Label(ftemp, text="index to: ").pack(side=LEFT)
        Entry(ftemp, textvariable=self.turnto, width=6).pack(side=LEFT)
        ftemp=Frame(f7)
        ftemp.pack(anchor=NE)
        Label(ftemp, text="every: ").pack(side=LEFT)
        Entry(ftemp, textvariable=self.turnevery, width=6).pack(side=LEFT)

        # calc bunching factor
        self.numofbunch=IntVar()
        self.numofbunch.set(2)
        self.harmonicnum=IntVar()
        self.harmonicnum.set(2)

        self.wcmgain=DoubleVar()
        self.wcmgain.set(50.0)
        self.basecalcstart=DoubleVar() # in nsec
        self.basecalcstart.set(300.0)
        self.basecalcdur=DoubleVar() # in nsec
        self.basecalcdur.set(50.0)
        self.usetcrange=IntVar()
        self.usetcrange.set(0) # 0: not used, 1:used
        self.tcst=DoubleVar()
        self.tcst.set(0)
        self.tcend=DoubleVar()
        self.tcend.set(500)
        self.bfplotrangemin=DoubleVar()
        self.bfplotrangemin.set(0)
        self.bfplotrangemax=DoubleVar()
        self.bfplotrangemax.set(0.5)

        ftemp=Frame(self)
        ftemp.pack()
        fparam=Frame(ftemp)
        fparam.pack()
        Label(fparam, text="WCM gain factor [mV/A]:").pack(side=LEFT)
        Entry(fparam, width=5, textvariable=self.wcmgain).pack(side=LEFT)
        fparam=Frame(ftemp)
        fparam.pack()
        Label(fparam, text="num of bunches in one slice:").pack(side=LEFT)
        Entry(fparam, width=2, textvariable=self.numofbunch).pack(side=LEFT)
        Label(fparam, text="harmonic number:").pack(side=LEFT)
        Entry(fparam, width=2, textvariable=self.harmonicnum).pack(side=LEFT)
        fparam=Frame(ftemp)
        fparam.pack()
#        Button(fparam, text= "use default for h=1/2 clk",
#               command=lambda: self.basecalcstart.set(400.0 if self.h1rfclk.get()==0 else 300.0)).pack()
        fparam=Frame(ftemp)
        fparam.pack()
        Label(fparam, text="baseline calc start (nsec):").pack(side=LEFT)
        Entry(fparam, width=5, textvariable=self.basecalcstart).pack(side=LEFT)
        Label(fparam, text="dur (nsec):").pack(side=LEFT)
        Entry(fparam, width=5, textvariable=self.basecalcdur).pack(side=LEFT)
        def change_state(): 
            e1.configure(state=["disabled", "normal"][self.usetcrange.get()])
            e2.configure(state=["disabled", "normal"][self.usetcrange.get()])
        Checkbutton(ftemp, text="use range for calc total curr", 
                    variable=self.usetcrange, onvalue=1, offvalue=0, 
                    command=change_state).pack()
        fparam=Frame(ftemp)
        fparam.pack()
        Label(fparam, text="total current calc start (nsec):").pack(side=LEFT)
        e1=Entry(fparam, width=5, textvariable=self.tcst, state="disabled")
        e1.pack(side=LEFT)
        Label(fparam, text="end (nsec):").pack(side=LEFT)
        e2=Entry(fparam, width=5, textvariable=self.tcend, state="disabled")
        e2.pack(side=LEFT)
        fparam=Frame(ftemp)
        fparam.pack()
        Label(fparam, text="Bf plot range min: ").pack(side=LEFT)
        Entry(fparam, width=5, textvariable=self.bfplotrangemin).pack(side=LEFT)
        Label(fparam, text="max: ").pack(side=LEFT)
        Entry(fparam, width=5, textvariable=self.bfplotrangemax).pack(side=LEFT)

        Checkbutton(ftemp, text="use turn-to-time conv", 
                    variable=self.usetimeconv, onvalue=1, offvalue=0).pack()
        Button(ftemp, text="calc curr/Bf", command=lambda: self.cbcalcbf(plotbf=True, fileout=False),\
               bg="yellow").pack()
        Button(ftemp, text="fileout curr/Bf", command=lambda: self.cbcalcbf(plotbf=False, fileout=True),\
               bg="light blue").pack()


        self.plotext=StringVar()
        self.plotext.set("png")
        ftemp=Frame(f7)
        ftemp.pack()
        Label(ftemp, text="plot file format: ").pack(side=LEFT)
        for text in ("png", "eps"):
            b=Radiobutton(ftemp, text=text, variable=self.plotext, value=text)
            b.pack(side=LEFT)

    def cbcalcbf(self, plotbf=True, fileout=False):
        print "calc bunching factor"
        if len(self.slices)==0:
            print "no data yet, return."
            return

        tf=self.turnfrom.get()
        tt=self.turnto.get()
        te=self.turnevery.get()

        if tf<0 or tt>len(self.slices) or te <=0:
            print "out of range"
            return

        print "from", tf,
        print "to", tt,
        print "every", te
        self.plottedslicenum=range(tf,tt,te)

        basest=self.basecalcstart.get()
        basedur=self.basecalcdur.get()
        tcst=self.tcst.get()
        tcend=self.tcend.get()
        wcmgain=self.wcmgain.get()
        print "baseline calc start: ", basest, ", dur: ", basedur
        
        self.bf_calcset=self.gen_bf_list(slices=self.slices, wcmgain=wcmgain, 
                                         basest=basest, basedur=basedur, tcst=tcst, tcend=tcend, 
                                         usetcrange=self.usetcrange.get(),
                                         numofbunch=self.numofbunch.get(),
                                         harmonicnum=self.harmonicnum.get())
        # turn, time, totalcurr, peakcurr, bf <= lists

        if plotbf==True:
            self.do_plot_bf_multi()
        elif fileout==True:
            self.do_fileout_bf()

    def gen_bf_list(self, slices=None, wcmgain=1.0, basest=500, basedur=100, tcst=0.0, tcend=600.0, usetcrange=0,
                    harmonicnum=2, numofbunch=2):
        unittime=slices.unittime*1.0e9 # in ns

#        print len(slices)
#        print slices[1]

        basestpt=int(basest/unittime)
        basedurpt=int(basedur/unittime)
        tcstpt=int(tcst/unittime)
        tcendpt=int(tcend/unittime)
#        print tcstpt, tcendpt
#        print basestpt, basedurpt
#        numofbunch=self.numofbunch.get()
        print "number of bunches = %d (accelerating RF is h=%d)" % (numofbunch, harmonicnum)
        avecurfactor=float(harmonicnum)/float(numofbunch)
        print "avecurfactor = %f" % avecurfactor

        baselinelist=[]
        totalcurrlist=[]
        peakcurrlist=[]
        bflist=[]
        selectedtimelist=[]

        for num in self.plottedslicenum:
            try:
                period=len(slices[num])*unittime
#                print unittime, period
#                print integperiod
                a=numpy.array(slices[num][basestpt:basestpt+basedurpt])
                baseline=numpy.sum(a)/len(a)
#                print "baseline:",baseline
                baselinelist.append(baseline)
                wfa=numpy.array(slices[num])
#                print wfa
#                totalcurr=avecurfactor*sum(wfa-baseline)/(wcmgain * 1e-3) \
#                    *unittime/period
#                totalcharge=sum((wfa-baseline)[tcstpt:tcendpt])/(wcmgain*1e-3)*unittime
#                totalcharge=sum((wfa)[tcstpt:tcendpt])/(wcmgain*1e-3)*unittime
#                print totalcharge

                if usetcrange==1:
                    totalcurr=\
                        avecurfactor*sum((wfa-baseline)[tcstpt:tcendpt])/size(wfa)/(wcmgain*1e-3)
                else:
                    totalcurr=\
                        avecurfactor*sum((wfa-baseline))/size(wfa)/(wcmgain*1e-3)
                    
#                print "average factor, curr:", avecurfactor, totalcurr

                # average current per bunch
                totalcurrlist.append(totalcurr)

#                print wfa-baseline

                peakcurr=numpy.max(wfa-baseline)/(wcmgain*1e-3) # baseline
                peakcurrlist.append(peakcurr)
                bf=totalcurr/peakcurr
                bflist.append(bf)
                time=slices.slicetimelist[num]
                selectedtimelist.append(time)

#                print baseline, totalcurr, peakcurr, bf
#                print "============"

            except IndexError:
                baselinelist.append(baseline)

        return self.plottedslicenum, selectedtimelist, totalcurrlist, peakcurrlist, bflist


    def do_plot_bf_multi(self):
        g=Gnuplot.Gnuplot(debug=0)
#

        g('set data style line') # give gnuplot an arbitrary command
#        g('set mxtics 5')
#        g('set mytics 5')
#        g('set grid xtics ytics mxtics mytics')
        g('set grid')
        g('set autoscale')
        g('set yrange [0:*]')
        if self.usetimeconv.get()==0:
            g('set xlabel "slice number"')
        else:
            g('set xlabel "time [ms]"')

        titlelist=("total curr", "peak curr", "Bf")
        ylabellist=("total current per bunch [A]", "peak current [A]", "bunching factor")

        gdatalist=[]
        if self.usetimeconv.get()==0:
            co=0
        else:
            co=1
        for i in (0,1,2):
            data=Gnuplot.Data(map(None, self.bf_calcset[co], self.bf_calcset[i+2]), 
                              title=titlelist[i])
            gdatalist.append(data)


        # execute plot! 
        g('unset multiplot')
        g('set multiplot layout 2,2')
        i=0
        for data in gdatalist:
            g('set autoscale')
            if i==2:
                g('set yrange [%f:%f]' % (self.bfplotrangemin.get(),self.bfplotrangemax.get()))
            else:
                g('set yrange [0:*]')
            g('set ylabel "%s"' % ylabellist[i])
            g.plot(data)
            i+=1

        # ask & output graphic file
        if self.plotfileyesno():
            g('unset multiplot')
            ext=self.plotext.get()
            plotfilename=genuniqplot(prefix="bfplot",ext=ext)
            print plotfilename
            if ext=="png":
                print "png"
                g("set terminal png tiny")
            elif ext=="eps":
                print "eps"
                g("set terminal postscript color eps")
            else:
                print "undefined"
                return


            # execute plot! 
            g('set output "%s"' % plotfilename)
            g('set multiplot layout 2,2')
            i=0
            for data in gdatalist:
                g('set autoscale')
                if i==2:
                    g('set yrange [%f:%f]' % (self.bfplotrangemin.get(),self.bfplotrangemax.get()))
                else:
                    g('set yrange [0:*]')
#                g('set size 0.5,0.5')
                g('set ylabel "%s"' % ylabellist[i])
                g.plot(data)
                i+=1
            g('unset multiplot')
            tkMessageBox.showinfo(title="plot", message="saved in %s" % plotfilename)
        g('unset multiplot')



    def do_fileout_bf(self):
        print "fileout bunching factor"
        # gen uniq filename
        outfilename=genuniqfilename(prefix="bf")
        if os.path.exists(outfilename):
            if not tkMessageBox.askyesno(\
                'askyesno', '%s exists. overwirte?' % outfilename):
                print "return."
                return(-1)
            else:
                print "overwrite."
        # open file
        print "outputfile: %s" % outfilename 
        outfile=open(outfilename, 'w') 

        outfile.write("# slice time totalcurr peakcurr bf\n")
        outbuf=map(None, self.bf_calcset[0], self.bf_calcset[1],
                   self.bf_calcset[2], self.bf_calcset[3], self.bf_calcset[4])
        for valset in outbuf:
            outline = "%8f\t%8f\t%8f\t%8f\t%8f\n" % valset
            outfile.write(outline)
        print "file output done."
        tkMessageBox.showinfo(title="bf file", message="saved in %s" % outfilename)  


    def plotfileyesno(self):
        return tkMessageBox.askyesno('askyesno','save plot?')



class MountainPlotGen(LabelFrame):
    def __init__(self, master, slices=None):
        LabelFrame.__init__(self, master)
        self.configure(text="mountain plot parameter")
        self.slices=slices
        self.init()
        self.pack()

    def init(self):
        self.zmin=DoubleVar()
        self.zmin.set(-0.5)
        self.zmax=DoubleVar()
        self.zmax.set(1)

        self.usexrange=IntVar() # 0: unuse, 1: use
        self.usexrange.set(0)
        self.xmin=DoubleVar()
        self.xmin.set(0)
        self.xmax=DoubleVar()
        self.xmax.set(720)        

        self.usephase=IntVar() # 0: unuse, 1: use
        self.usephase.set(0)
        self.phfact=DoubleVar()
        self.phfact.set(720)

        self.usetimeconv=IntVar() # 0: unuse, 1: use
        self.usetimeconv.set(0)

        ftemp=Frame(self)
        ftemp.pack()
        Label(ftemp, text="beam volt range min: ").pack(side=LEFT)
        Entry(ftemp, textvariable=self.zmin, width=4).pack(side=LEFT)
        Label(ftemp, text=" max: ").pack(side=LEFT)
        Entry(ftemp, textvariable=self.zmax, width=4).pack(side=LEFT)
        ftemp=Frame(self)
        ftemp.pack()
        Checkbutton(ftemp, text="use time axis range", 
                    variable=self.usexrange, onvalue=1, offvalue=0).pack()
        Label(ftemp, text="time axis min: ").pack(side=LEFT)
        Entry(ftemp, textvariable=self.xmin, width=4).pack(side=LEFT)
        Label(ftemp, text="max: ").pack(side=LEFT)
        Entry(ftemp, textvariable=self.xmax, width=4).pack(side=LEFT)
        ftemp=Frame(self)
        ftemp.pack()
        Checkbutton(ftemp, text="use phase", 
                    variable=self.usephase, onvalue=1, offvalue=0).pack()
        Label(ftemp, text="phase factor: ").pack(side=LEFT)
        Entry(ftemp, textvariable=self.phfact, width=4).pack(side=LEFT)
        ftemp=Frame(self)
        ftemp.pack()
        Checkbutton(ftemp, text="use turn-to-time conv", 
                    variable=self.usetimeconv, onvalue=1, offvalue=0).pack()


        self.turnsel=IntVar()
        self.turnsel.set(100)

        ftemp=Frame(self)
        ftemp.pack()
        Label(ftemp, text="index number: ").pack(side=LEFT)
        Entry(ftemp, textvariable=self.turnsel, width=6).pack(side=LEFT)
        Button(ftemp, text="plot single turn", command=self.plotselected,\
                   bg="light blue").pack()
        Button(ftemp, text="export single turn", command=self.fileoutselected,\
                   bg="light blue").pack(side=BOTTOM)


        self.turnfrom=IntVar()
        self.turnfrom.set(0)
        self.turnto=IntVar()
        self.turnto.set(1000)
        self.turnevery=IntVar()
        self.turnevery.set(5)

        f7=Frame(self)
        f7.pack()
        ftemp=Frame(f7)
        ftemp.pack(anchor=NE)
        Label(ftemp, text="index from: ").pack(side=LEFT)
        Entry(ftemp, textvariable=self.turnfrom, width=6).pack(side=LEFT)
        ftemp=Frame(f7)
        ftemp.pack(anchor=NE)
        Button(ftemp, text="use last slice", command=lambda: self.turnto.set(len(self.slices)))\
            .pack(side=LEFT)
        Label(ftemp, text="index to: ").pack(side=LEFT)
        Entry(ftemp, textvariable=self.turnto, width=6).pack(side=LEFT)
        ftemp=Frame(f7)
        ftemp.pack(anchor=NE)
        Label(ftemp, text="every: ").pack(side=LEFT)
        Entry(ftemp, textvariable=self.turnevery, width=6).pack(side=LEFT)


        self.contour=IntVar()
        self.contour.set(1)
        Checkbutton(f7, text="contour", 
                    variable=self.contour, onvalue=1, offvalue=0).pack(anchor=W)
        Button(f7, text="plot contour/mountain SELECTED", command=self.mountain_plot_selected,\
               bg="light blue").pack()

        self.plotext=StringVar()
        self.plotext.set("png")
        ftemp=Frame(f7)
        ftemp.pack()
        Label(ftemp, text="plot file format: ").pack(side=LEFT)
        for text in ("png", "eps"):
            b=Radiobutton(ftemp, text=text, variable=self.plotext, value=text)
            b.pack(side=LEFT)


        # para-para manga
        self.makeanimefile=IntVar()
        self.makeanimefile.set(0)
#        Button(f7, text="plot para-para-manga", command=self.cutoff_anime_selected,\
#               bg="light blue").pack()
#        Button(f7, text="gen para-para-manga files", command=self.cutoff_anime_gif,\
#               bg="light blue").pack()
        Button(f7, text="gen para-para-manga gif", command=self.cutoff_anime_gif_direct,\
               bg="light blue").pack()

        
        ftemp=Frame(f7)
        ftemp.pack()
        Button(f7, text="turn vs time plot", command=self.do_plot_time,\
               bg="yellow").pack()


    def mountain_plot_selected(self):
        if len(self.slices)==0:
            print "no data yet, return."
            return
        tf=self.turnfrom.get()
        tt=self.turnto.get()
        te=self.turnevery.get()

        if tf<0 or tt>len(self.slices) or te <=0:
            print "out of range"
            return

        print "plot from", tf,
        print "to", tt,
        print "every", te
        self.plottedslicenum=range(tf,tt,te)

        

        gen_mountains(slices=self.slices, plottedslicenum=self.plottedslicenum, usephase=self.usephase.get(),
                      phfact=self.phfact.get(), usetimeconv=self.usetimeconv.get())
        self.do_mountain_plot(contour=self.contour.get())

    def do_mountain_plot(self, contour=1):
        g=Gnuplot.Gnuplot(debug=0)
        self.plot_range_set(g)
#        g.title("mountain plot")
        g('set data style line') # give gnuplot an arbitrary command
        g('set nokey')
        g('set noytic')
        g('set noztic')

        g('set nomultiplot')
        if self.usephase.get()==1:
            g('set xlabel "phase [deg]"')
        else:
            g('set xlabel "time [ns]"')
        if self.usetimeconv.get()==0:
            g('set ylabel "slice number"')
        else:
            g('set ylabel "time [ms]"')


        g('set ytic')

        if contour==1:
            g("set pm3d map")
        else:
            g("set contour base")
            g("set view 30,0")

        g('splot "c:/tmp/tempfile.txt"') 

        if self.plotfileyesno():
            ext=self.plotext.get()
            plotfilename=genuniqplot(ext=ext)
            print plotfilename
            if ext=="png":
                print "png"
                g("set terminal png")
            elif ext=="eps":
                print "eps"
                g("set terminal postscript color eps")
            else:
                print "undefined"
                return
            g('set output "%s"' % plotfilename)
            g('splot "c:/tmp/tempfile.txt"')
            tkMessageBox.showinfo(title="plot", message="saved in %s" % plotfilename)

    def plot_range_set(self, g):
        g('set autoscale')
        g('set zrange [%f:%f]' % (self.zmin.get(), self.zmax.get()))
        print self.usexrange.get()
        if self.usexrange.get()==1:
            g('set xrange [%f:%f]' % (self.xmin.get(), self.xmax.get()))

    def fileoutselected(self):
        if len(self.slices)==0:
            print "no data yet, return."
            return
        num=self.turnsel.get()
        try:
            selected=self.slices[num]
        except IndexError:
            print "turn sel out of range"
            return

        unittime=self.slices.unittime*1.0e9
        phfact=self.phfact.get()
        if self.usephase.get()==1:
            tval=filter(lambda item: item[1]!=None, 
                        map(lambda t,val: (phfact*t/(unittime*len(selected)),val), self.slices.slicetime,selected))
        else:
            tval=filter(lambda item: item[1]!=None, map(lambda t,val: (t,val), self.slices.slicetime,selected))


#        tval=filter(lambda item: item[1]!=None, map(lambda t,val: (t,val), self.slices.slicetime,selected))
        print num

        print "fileout single turn waveform"
        # gen uniq filename
        outfilename=genuniqfilename(prefix="singlewfm")
        if os.path.exists(outfilename):
            if not tkMessageBox.askyesno(\
                'askyesno', '%s exists. overwirte?' % outfilename):
                print "return."
                return(-1)
            else:
                print "overwrite."
        # open file
        print "outputfile: %s" % outfilename 
        outfile=open(outfilename, 'w') 

        outfile.write("# slicenum=%d time signal\n" % num)

        for valset in tval:
            outline = "%.2f\t%.8f\n" % valset
            outfile.write(outline)
        print "file output done."
        tkMessageBox.showinfo(title="bf file", message="saved in %s" % outfilename)              


    def plotselected(self):
        if len(self.slices)==0:
            print "no data yet, return."
            return
        g=Gnuplot.Gnuplot(debug=0)
#        g.title("beam signal")
        g('set data style line') # give gnuplot an arbitrary command
 #       g('set nokey')

        g('set nomultiplot')
#        g('set xlabel "time [ns]"')
        if self.usephase.get()==1:
            g('set xlabel "phase [deg]"')
        else:
            g('set xlabel "time [ns]"')
        g('set ylabel "beam signal [volt]"')

        g('set mxtics 5')
        g('set mytics 5')
#        g('set grid xtics ytics mxtics mytics')
        g('set autoscale')
#        print self.slicetime[-1]
        g('set yrange [%f:%f]' % (self.zmin.get(), self.zmax.get()))
        if self.usexrange.get()==1:
            g('set xrange [%f:%f]' % (self.xmin.get(), self.xmax.get()))
        else:
            g('set xrange [0:%f]' % self.slices.slicetime[-1])

        num=self.turnsel.get()
        try:
            selected=self.slices[num]
        except IndexError:
            print "turn sel out of range"
            return

        unittime=self.slices.unittime*1.0e9
        phfact=self.phfact.get()
        if self.usephase.get()==1:
            tval=filter(lambda item: item[1]!=None, 
                        map(lambda t,val: (phfact*t/(unittime*len(selected)),val), self.slices.slicetime,selected))
        else:
            tval=filter(lambda item: item[1]!=None, map(lambda t,val: (t,val), self.slices.slicetime,selected))


#        tval=filter(lambda item: item[1]!=None, map(lambda t,val: (t,val), self.slices.slicetime,selected))
        print num
        d=Gnuplot.Data(tval, title="%d" % num)
        g.plot(d)
        
#        tkMessageBox.showinfo(title="plot", message="done")
        if self.plotfileyesno():
            ext=self.plotext.get()
            plotfilename=genuniqplot(ext=ext)
            print plotfilename
            if ext=="png":
                print "png"
                g("set terminal png")
            elif ext=="eps":
                print "eps"
                g("set terminal postscript color eps")
            else:
                print "undefined"
                return
            g('set output "%s"' % plotfilename)
            g.replot()
            tkMessageBox.showinfo(title="plot", message="saved in %s" % plotfilename)


    def cutoff_anime_gif_direct(self):
        if len(self.slices)==0:
            print "no data yet, return."
            return
        tf=self.turnfrom.get()
        tt=self.turnto.get()
        te=self.turnevery.get()

        if tf<0 or tt>len(self.slices) or te <=0:
            print "out of range"
            return

        print "plot from", tf,
        print "to", tt,
        print "every", te
        self.plottedslicenum=range(tf,tt,te)

        # make temorary folder
        date=datetime.datetime.today().strftime('%y%m%d%H%M%S')
        tempfoldername="temp"+date
        if not os.path.isdir(tempfoldername):
            print "generate folder '%s'." % tempfoldername
            os.makedirs(tempfoldername)
        else:
            print "use existing folder."

        prefix="anime"
        # open gnuplot script file
        tempgpfilename=string.replace(os.path.join(".",tempfoldername,prefix+date+"."+"plt"),'\\', '/')
        tempgpfilenamecore=prefix+date+"."+"plt"
        gpfile=open(tempgpfilename, 'w')
#        gpfile.write('set title "beam signal"\n')
        gpfile.write('set data style line\n')

        gpfile.write('unset multiplot\n')
        if self.usephase.get()==1:
            gpfile.write('set xlabel "phase [deg]"\n')
        else:
            gpfile.write('set xlabel "time [ns]"\n')
        gpfile.write('set ylabel "beam signal [volt]"\n')

        gpfile.write('set mxtics 5\n')
        gpfile.write('set mytics 5\n')
#        gpfile.write('set grid xtics ytics mxtics mytics\n')
        gpfile.write('set autoscale\n')
        print self.slices.slicetime[-1]
        gpfile.write('set yrange [%f:%f]\n' % (self.zmin.get(), self.zmax.get()))
        if self.usexrange.get()==1:
            gpfile.write('set xrange [%f:%f]\n' % (self.xmin.get(), self.xmax.get()))
        else:
            gpfile.write('set xrange [0:%f]\n' % self.slices.slicetime[-1])

#        gpfile.write('set terminal png\n')
        gpfile.write('set terminal gif animate delay 3\n')
        giffilename='anime'+date+'.gif'
        gpfile.write('set output "..\\\\%s" \n' % giffilename)


        i=0
        
        for num in self.plottedslicenum:
            tempfilename=string.replace(os.path.join(".",tempfoldername,prefix+date+"_%04d."%(i)+"txt"),'\\', '/')
            tempfilenamecore=prefix+date+"_%04d."%(i)+"txt"
            temppngname=string.replace(os.path.join(".",tempfoldername,prefix+date+"_%04d."%(i)+"png"),'\\', '/')
            temppngnamecore=prefix+date+"_%04d."%(i)+"png"
            try:
                selected=self.slices[num]
            except IndexError:
                print "turn sel out of range"
                return

#            unittime=self.sparcing.get()*self.utime # time for one point
            unittime=self.slices.unittime*1.0e9 # in ns
            phfact=self.phfact.get()
            if self.usephase.get()==1:
                tval=filter(lambda item: item[1]!=None, 
                            map(lambda t,val: (phfact*t/(unittime*len(selected)),val), self.slices.slicetime,selected))
            else:
                tval=filter(lambda item: item[1]!=None, map(lambda t,val: (t,val), self.slices.slicetime,selected))

            #time.sleep(0.4)
            fotemp=open(tempfilename, 'w')
            for item in tval:
                fotemp.write("%f\t%f\n" % item)
            fotemp.flush()
#            time.sleep(0.3)

#            gpfile.write('set output "%s"\n' % temppngnamecore)
            gpfile.write('plot "%s" title "turn %d"\n' % (tempfilenamecore, num))
            i+=1

        gpfile.write('unset output\n')
        gpfile.write('set term windows\n')
        #if self.makeanimefile.get()==0:
        #    gpfile.write('# ')
        #gpfile.write('!convert -loop 1 delay=1 *.png ..\\%s' % 'anime'+date+'.gif\n') 
        gpfile.close()

        os.chdir(tempfoldername)
        p1 = subprocess.Popen("wgnuplot %s" % tempgpfilenamecore, shell=False, stderr=subprocess.PIPE)
        r1=p1.wait()
        #r1=os.system('wgnuplot %s' % (tempgpfilenamecore))
        print "wgnuplot return value: ", r1
        for line in  p1.stderr:
            print line
#        if r1:
#            print "process error."
        os.chdir('..')
        print os.getcwd()

#        filenames=' '.join(glob.glob('.\\'+tempfoldername+'\\*.png'))

#        p2=subprocess.Popen('convert -loop 0 %s %s' % (filenames, 'anime'+date+'.gif'), shell=True)
#        r2=p2.wait()
#        print r2

        tkMessageBox.showinfo(title="plot done", message="saved in %s" % (giffilename))
        #g("cd ..")
        #g("set term windows")
        #g("exit")
#        time.sleep(1)
#        if self.removefolderyes.get():
#            os.removedirs(tempfoldername)
#            if result!=0:
#                print "error in removing folder."




    def do_plot_time(self):
        g=Gnuplot.Gnuplot(debug=0)
        g('set data style line') # give gnuplot an arbitrary command
        g('set mxtics 5')
        g('set mytics 5')
#        g('set grid xtics ytics mxtics mytics')
        g('set autoscale')
        g('set xlabel "slice number"')
        g('set ylabel "time [ms]"')

        gdatalist=[]

        data=Gnuplot.Data(map(None, self.slices.slicetimelist), 
                              title="time")
        gdatalist.append(data)
                        
        g.plot(*tuple(gdatalist))
        self.asksave2dplot(g, prefix="timeplot")

    def asksave2dplot(self,g, prefix="plot"):
        if self.plotfileyesno():
            ext=self.plotext.get()
            plotfilename=genuniqplot(prefix=prefix, ext=ext)
            print plotfilename
            if ext=="png":
                print "png"
                g("set terminal png")
            elif ext=="eps":
                print "eps"
                g("set terminal postscript color eps")
            else:
                print "undefined"
                return
            g('set output "%s"' % plotfilename)
            g.replot()
            tkMessageBox.showinfo(title="plot", message="saved in %s" % plotfilename)


    def plotfileyesno(self):
        return tkMessageBox.askyesno('askyesno','save plot?')


class App(Frame):
    def init(self):
#        osc="GPIB::5" # KIME-UCHI (to be modified)

#        osc="TCPIP::10.33.41.74"  # KIME-UCHI (to be modified)
        osc=self.target

        if not self.offline:
            ftemp=Frame(self); ftemp.pack(side=LEFT)
            self.scopecontrol=ScopeControl(ftemp, osc=osc)
            self.scopecontrol.pack()
            self.master.title("%s mountain plot" % self.scopecontrol.osc.Model)
        else:
            self.master.title("mountain plot (offline mode)")

        fftemp=Frame(self);fftemp.pack(side=LEFT)
        if not self.offline:
            ftemp=Frame(fftemp); ftemp.pack()
            self.wftransfer=WaveformTransfer(ftemp, osc=self.scopecontrol.osc)
            self.wftransfer.pack()

        self.rfclkwaveform=numpy.array([])
        self.beamwaveform=numpy.array([])
        self.rfclkdata=numpy.array([])
        self.beamdata=numpy.array([])
        self.tdata=numpy.array([])


        Button(self, text="mountain", command=self.mountain_test).pack() # temp button for test

        Button(self, text="plot clk", command=self.plot_test1).pack() # temp button for test
        Button(self, text="plot data", command=self.plot_test2).pack() # temp button for test

        
        ftemp=Frame(fftemp); ftemp.pack()
        self.slices=WfmSlice()
        self.slicegen=SliceGenerator(ftemp)
        self.slicegen.pack()

        ftemp=Frame(fftemp); ftemp.pack()
        if not self.offline:
            Button(ftemp, text="get waveform and gen slices", command=self.get_waveforms, bg="pink").pack() 
        Button(ftemp, text="regenenerate slices", command=self.gen_slices, bg="pink").pack() 
        ftemp=Frame(fftemp); ftemp.pack()
        self.slicelen=IntVar()
        Label(ftemp, text="num of slices: ").pack(side=LEFT)
        Label(ftemp, textvariable=self.slicelen).pack(side=LEFT)




        ftemp=Frame(self); ftemp.pack(side=LEFT)
        fftemp=LabelFrame(ftemp, text="output file"); fftemp.pack()
        Label(fftemp, text="output filename is automatically generated").pack()
        Button(fftemp, text="output file", command=self.fileout, bg="pink").pack() # temp button for test        
        
        fftemp=Frame(ftemp); fftemp.pack()
        self.filein=FileIn(fftemp)
        self.filein.pack()
        Button(fftemp, text="read from file", command=self.readfile, bg="light blue").pack() # temp button for test


        self.mountainplotgen=MountainPlotGen(ftemp, slices=self.slices)
        self.mountainplotgen.pack()
        ftemp=Frame(self); ftemp.pack(side=LEFT)
        self.bfplotgen=BfPlotGen(ftemp, slices=self.slices)
        self.bfplotgen.pack()


    def mountain_test(self):
        gen_mountains(slices=self.slices, plottedslicenum=range(0,len(self.slices),50))


    def plot_test1(self):
        P.plot(self.tdata, self.rfclkdata)
        P.show()

    def plot_test2(self):
        P.plot(self.tdata, self.beamdata)
        P.show()


    def readfile(self):
        print "read from file"
        clkinfilename=self.filein.clkfilename.get()
        beaminfilename=self.filein.beamfilename.get()
        # if input file does not exist, return
        if not os.path.exists(clkinfilename):
            tkMessageBox.showerror('showerror','input file does not exist.')
            print "return."
            return(-1)
        if not os.path.exists(beaminfilename):
            tkMessageBox.showerror('showerror','input file does not exist.')
            print "return."
            return(-1)
        # open files
        print "clk inputfile: %s" % clkinfilename 
        print "beam inputfile: %s" % beaminfilename 
        clkininfile=open(clkinfilename, 'rb')
        beamininfile=open(beaminfilename, 'rb')
        self.rfclkwaveform=clkininfile.read()
        self.beamwaveform=beamininfile.read()
        self.rfclkdata= lecroy_wfm_analyze(self.rfclkwaveform)
        self.tdata, self.beamdata= lecroy_wfm_analyze(self.beamwaveform, withtimes=True)

        self.gen_slices()

    def fileout(self):
        if len(self.rfclkdata)==0:
            print "no data yet, return"
            return
        filenameclk, filenamebeam=genuniqfolder_file_set(datefilename=True, 
                                                    prefix="wfm", suffix1="clk", suffix2="wcm",
                                                    ext="trc")
        print filenameclk, filenamebeam
        fclk=open(filenameclk, "wb")
        fclk.write(self.rfclkwaveform)
        fclk.close()
        fbeam=open(filenamebeam, "wb")
        fbeam.write(self.beamwaveform)
        fbeam.close()

        print "file output done."
        tkMessageBox.showinfo(title="clk/wcm files", message="saved in %s, %s" % (filenameclk, filenamebeam))

    def get_waveforms(self):
        self.rfclkwaveform=numpy.array([])
        self.beamwaveform=numpy.array([])
        self.rfclkdata=numpy.array([])
        self.beamdata=numpy.array([])
        self.tdata=numpy.array([])

        self.rfclkwaveform, self.beamwaveform = self.wftransfer.get_waveforms()

        self.rfclkdata= lecroy_wfm_analyze(self.rfclkwaveform)
        self.tdata, self.beamdata= lecroy_wfm_analyze(self.beamwaveform, withtimes=True)
#         print len(self.rfclkdata)
#         print len(self.tdata)
#         print len(self.beamdata)

        self.gen_slices()

    def gen_slices(self):
        if len(self.rfclkdata)==0:
            print "no data yet, return"
            return
        self.slicegen.analyze_desc_gen_slices(slices=self.slices, wavedesc=self.rfclkwaveform,\
                                     rfclkdata=self.rfclkdata, beamdata=self.beamdata)
        
        #print len(self.slices)
        self.slicelen.set(len(self.slices))

    def __init__(self, master=None, offline=False, target="TCPIP::10.33.41.74"):
        Frame.__init__(self, master)
        if target=="TCPIP::10.33.41.74":
            self.option_add('*background',"violet")
            self.configure(bg="violet")
        self.offline=offline
        self.target=target
        self.init()
        self.pack()

def main():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-t", "--target", dest="target",
                      help="target oscilloscope, 'GPIB::5' is WP950, 'TCPIP::10.33.41.74' is WP715zi, 'offline' is for offline analysis")

    (options, args) = parser.parse_args()

#    print options
#    print options.target
#    print args, len(args)

    if options==None:
        parser.print_help()
        exit()

    if options.target==None:
        parser.print_help()
        exit()

    if options.target=="offline":
        print "offline mode."
        offline=True
    else:
        offline=False
        target=options.target
        print "target oscilloscope is", target

    app = App(offline=offline, target=target)
    app.pack()
    app.mainloop()

if __name__ == "__main__":
    main()
