#
#-*- coding:utf-8 -*-
"""
A module to support
for Algilent DSO
(C) Noboru Yamamoto,2009. KEK, Ibaraki, JAPAN
Reference:
jkjblad04.14: vxi11scan 

 Get RPC info
   program vers proto   port
    100000    2   udp    111  portmapper
    100000    2   tcp    111  portmapper
    395180    1   tcp   1024
    395183    1   tcp   1024

link created to gpib0,7 
	 Error code:0
	 LinkID:22529568
	 port 999
	 MaxRecvSize:16384
Device is remote. RC:0
wrote *IDN?;

	 Error code:0
	 Size:7
start to read
52 bytes data read:AGILENT TECHNOLOGIES,DSO6014L,MY47090019,05.10.0284
"""

import vxi11Device
import time,types,struct,exceptions

class AglDSO(vxi11Device.Vxi11Device):
    def __init__(self,host,device="gpib0,7"):
        vxi11Device.Vxi11Device.__init__(self, host,device)
        self.IDN_Str=self.qIDN()
        self.write("VERBOSE ON;")
        self.write("HEADER OFF;")
        ID=self.IDN_Str[:-1].split(",")
        self.Make=ID[0]
        self.Model=ID[1]
        self.Option=ID[3]

    def respToDict(self, lables,resp):
        v=resp[:-1].split(";")
        d={}
        d.update(zip(lables,v))
        return d
    
    def qACQMODE(self):
        return self.qAcqMode()

    def qAcqMode(self):
        "<mode> ::= {RTIMe | ETIMe | SEGMented}"
        self.write("ACQ:MODE?;")
        return self.read()

    def qAcqType(self):
        self.write("ACQ:TYPE?;")
        return self.read()

    def AcqType(self,atype="HRES"):
        """
        <type> ::= {NORMal | AVERage | HRESolution | PEAK}
        """
        self.write(":ACQ:TYPE %s;"%atype)

    def qAcqComplete(self):
        self.write(":ACQ:COMP;")
        return self.read()

    def AcqComplete(self,n=100):
        """
        AQUIRE_COMPLETE - Specifies the minimum completion criteria
        for an acquisition.  The parameter determines the percentage
        of time buckets needed to be "full" before an acquisition is
        considered to be complete.
        """
        self.write(":ACQ:COMP %d;"%n)

    def AcqMode(self,mode):
        """
        mode ::= RTIM | ETIM
        """
        modes= ("RTIM","ETIM")
        if type(mode) == type(0):
            mode=modes[mode]
        self.write(":ACQ:MODE %s;"%mode)

    def digitize(self,chan=1):
        self.write(":DIGITIZE CHAN%d;"%chan)
        
    def qBusy(self):
        return self.ask(":ACT?;")

    def qActivity(self):
        return self.ask(":ACT?;")

    def Activity(self):
        " Clears the cumulative edge variables. "
        return self.write(":ACT;")

    def qOPC(self,io_timeout=10000):
        self.write("*OPC?;")
        return self.read(io_timeout=io_timeout)

    def Run(self):
        self.write("RUN;")

    def Single(self):
        self.write("SINGLE;")

    def Stop(self):
        self.write("STOP;")

    def qSetup(self):
        self.write(":SYSTEM:SETUP?")
        return self.read()

    def Status(self,disp="CHAN1"):
        """
        <display> ::= {CHANnel<n>
        |DIGital0,..,DIGital15
        | POD{1 |2}
        | BUS{1 | 2}
        | FUNCtion
        | MATH| SBUS}
        <n> ::= 1-2 or 1-4 in NR1 format
        """
        return self.ask(":STAT? %s ;"%disp)

    def qTER(self):
        return self.ask(":TER?;")

    def clear(self):
        self.write("*CLS;")
        
    def wait(self):
        self.write("*WAI;")
        
    def device_clear(self,flags=0,lock_timeout=0,io_timeout=5):
        vxi11Device.Vxi11Device.clear(self, flags, lock_timeout, io_timeout)

    def clear_all(self):
        self.clear()
        self.device_clear()
        
    def get_cursor_mode(self):
        return self.ask(":MARK:MODE?;")

    def set_cursor_mode(self,mode="OFF"):
        return self.write(":MARK:MODE %s;"%mode)

    def get_cursor_x1pos(self):
        return self.ask(":MARK:X1P?;")

    def set_cursor_x1pos(self,pos="0"):
        return self.write(":MARK:X1P %s;"%mode)

    def get_cursor_x2pos(self):
        return self.ask(":MARK:X2P?;")

    def set_cursor_x2pos(self,pos="0"):
        return self.write(":MARK:X2P %s;"%mode)

    def get_cursor_xdelta(self):
        return self.ask(":MARK:XDEL?;")
    
    def get_cursor_y1pos(self):
        return self.ask(":MARK:Y1P?;")

    def set_cursor_y1pos(self,pos="0"):
        return self.write(":MARK:Y1P %s;"%mode)

    def get_cursor_y2pos(self):
        return self.ask(":MARK:Y2P?;")

    def set_cursor_y2pos(self,pos="0"):
        return self.write(":MARK:Y2P %s;"%mode)

    def get_cursor_ydelta(self):
        return self.ask(":MARK:YDEL?;")
    #
    def set_wf_ByteOrder(self,order="LSBF"):
        "order = LSBF | MSBF"
        self.write(":WAV:BYT %s;"%order)

    def get_wf_ByteOrder(self):
        "order = LSBF | MSBF"
        return self.ask(":WAV:BYT?;")
        
    def get_wf_format(self):
        "fmt = ASCII|WORD | BYTE"
        return self.ask(":WAV:FORM?;")

    def set_wf_format(self,fmt="ASCII"):
        "fmt = ASCII | WORD | BYTE"
        self.write(":WAV:FORM %s;"%fmt)

    def set_wf_binary(self,fmt="BYTE"):
        "fmt = WORD | BYTE"
        self.write(":WAV:FORM %s;"%fmt)

    def set_wf_ascii(self):
        self.write(":WAV:FORM ASCII;")
        
    def get_wf_point(self):
        return self.ask(":WAV:POIN?;")

    def set_wf_point(self,point="1000"):
        """
        <# points> ::= {100 | 250 | 500 |1000 | <points_mode>} if waveformpoints mode is NORMal
        <# points> ::= {100 | 250 | 500 |1000 | 2000 ... 8000000 in 1-2-5sequence | <points_mode>} ifwaveform points mode is MAXimum or RAW
        <points_mode> ::= {NORMal |MAXimum | RAW}
        The raw acquisition record can only betransferred when the oscilloscope is not running and can only be retrieved from the analog or digital sources.
        """
        self.write(":WAV:POIN %s;"%point)

    def get_wf_point_mode(self):
        return self.ask(":WAV:POIN:MODE?;")

    def set_wf_point_mode(self,mode="NORM"):
        """
        mode= NORM | MAX | RAW
        """
        self.write(":WAV:POIN:MODE %s;"%mode)

    def get_wave_preamble(self):
        """
        <preamble_block> ::= <formatNR1>, <type NR1>,<pointsNR1>,<count NR1>,
        <xincrementNR3>, <xorigin NR3>, <xreferenceNR1>,
        <yincrement NR3>, <yoriginNR3>, <yreference NR1>
        <format> ::= an integer in NR1format:
          0 for BYTE format
          1 for WORD format
          2 for ASCii format
        <type> ::= an integer in NR1format:
          0 for NORMal type
          1 for PEAK detect type
          2 for AVERage type
          3 for HRESolution type
        <count> ::= Average count, or 1if PEAK detect type or NORMal; aninteger in NR1 format
        """
        return wpreamble(self.ask(":WAV:PRE?;"))
    
    def get_waveform(self,ch=1,io_timeout=5):
        """
        it is better to stop scanning before get waveform data on TDS.
        """
        if (type(ch) ==types.StringType):
            self.write(":WAV:SOUR %s;\n"%ch)
        else:
            self.write(":WAV:SOUR CHAN%d;\n"%ch)
        import time
        header=self.get_wave_preamble()
        enc=self.get_wf_format().strip()
        byteo=self.get_wf_ByteOrder().strip()
        self.write(":WAV:DATA?;\n")
        r=self.readResponce(io_timeout=io_timeout)
        wf=waveform(r,format=enc,byteo=byteo,preamble=header)
        return wf

    def get_curve(self,ch=1,io_timeout=5):
        self.write(":WAV:SOUR CHAN%d;\n"%ch)
        self.write(":WAV:DATA?")
        return self.readResponce(io_timeout=io_timeout)

    def get_SESR(self):
        self.write("*ESR?;")
        return SESR(int(self.read()))

    def get_SBR(self):
        self.write("*STB?;")
        return SBR(int(self.read()))

    def get_DESER(self):
        self.write(":DESE?;")
        return DESER(self.read())

    def get_ESER(self):
        self.write("*ESE?;")
        return ESER(self.read())

    def get_SRER(self):
        self.write("*SRE?;")
        return SRER(self.read())


def bit(n,d):
    return (d>>n)&1
    
class Register:
    def __init__(self,ini_data):
        self.val=int(ini_data)
    def __str__(self):
        s=""
        for item in self.__dict__.items():
            if item[0] == "val":
                continue
            s+="%s:%d, "%item
        return s

class SESR(Register):
    """Standard Event Status Register
    bit7...................................bit.0
    PON | URQ | CME | EXE | DDE| QYE| RQC | OPC
    """
    def __init__(self,ini_data):
        Register.__init__(self,ini_data)
        self.pon=bit(7,self.val)
        self.urq=bit(6,self.val)
        self.cme=bit(5,self.val)
        self.exe=bit(4,self.val)
        self.dde=bit(3,self.val)
        self.qye=bit(2,self.val)
        self.rqc=bit(1,self.val)
        self.opc=bit(0,self.val)
        
class SBR(Register):
    """Status Byte Register
    bit7..................................bit.0
    - | RQS/MSS | ESB| MAV | - |  - |  - |  - 
    """
    def __init__(self,ini_data):
        Register.__init__(self,ini_data)
        self.rqs=bit(6,self.val)
        self.mss=bit(6,self.val)
        self.esb=bit(5,self.val)
        self.mav=bit(4,self.val)

class DESER(Register):
    """ Device Event Status Enable Register"
    bit7..................................bit.0
    PON | URQ | CME | EXE | DDE | QYE | RQC | OPC
    """
    def __init__(self,ini_data):
        Register.__init__(self,ini_data)
        self.pon=bit(7,self.val)
        self.urq=bit(6,self.val)
        self.cme=bit(5,self.val)
        self.exe=bit(4,self.val)
        self.dde=bit(3,self.val)
        self.qye=bit(2,self.val)
        self.rqc=bit(1,self.val)
        self.opc=bit(0,self.val)

class ESER(Register):
    """ Event Status Enable Register"
    bit7..................................bit.0
    PON | URQ | CME | EXE | DDE | QYE | RQC | OPC
    """
    def __init__(self,ini_data):
        Register.__init__(self,ini_data)
        self.pon=bit(7,self.val)
        self.urq=bit(6,self.val)
        self.cme=bit(5,self.val)
        self.exe=bit(4,self.val)
        self.dde=bit(3,self.val)
        self.qye=bit(2,self.val)
        self.rqc=bit(1,self.val)
        self.opc=bit(0,self.val)

class SRER(Register):
    """ Service Request Enable Register"
    bit7...........................bit.0
    - | - | ESB | MAV | - | - | - | -
    """
    def __init__(self,ini_data):
        Register.__init__(self,ini_data)
        self.esb=bit(5,self.val)
        self.mav=bit(4,self.val)
#
# data objects
#
class wpreamble:
    pre_block=(
        ("format",int),
        ("type", int),
        ("points",int),
        ("count", int),
        ("xincrement",float),
        ("xorigin",float),
        ("xreference",int),
        ("yincrement",float),
        ("yorigin",float),
        ("yreference",int)
        )

    def __init__(self, data):
        self.str=data
        list=data.split(",")
        for i in xrange(len(list)):
            key,conv=self.pre_block[i]
            self.__dict__[key]=conv(list[i])
            
class waveform:
    BFMT={"ASCII":"%d","ASC":"%d","BYTE":"B","WORD":"H"}
    BORD={"MSBF":">","LSBF":"<"}
    DWIDTH={"ASCII":0,"ASC":0,"BYTE":1,"WORD":2}

    def __init__(self,data,format="ASC",byteo="LSBF",preamble=None):
        if preamble:
            if type(preamble) == type(""):
                self.preamble=wpreamble(preamble)
            elif isinstance(preamble,wpreamble):
                self.preamble=preamble
            else:
                raise TypeError,"invalid preamble"
        else:
            self.preamble=None
        if data[0] <> "#":
            raise ValueError,"invalid format"
        hdsize=int(data[1])
        self.dsize=int(data[2:][:hdsize])
        self.rdata=data[2:][hdsize:]
        if (len(self.rdata) < self.dsize):
            raise exceptions.ValueError,"Not enough data %d %d"%(len(self.rdata),self.dsize)
        wfdata=self.rdata
        self.ENC=format # ASC|BYTE|WORD
        self.point_fmt=format
        self.BYTE_ORDER=byteo
        self.BIN_FMT=format

        self.Data_Num=self.dsize
        #self.wfid=self.rdata[6]
        if self.preamble:
            self.X_Incr=self.preamble.xincrement
            self.Point_Offset=self.preamble.xreference
            self.X_Zero=self.preamble.xorigin
            if (self.ENC == "ASC"):
                self.Y_Mult=1
                self.Y_Zero=0
                self.Y_Offset=0
            else:
                self.Y_Mult=self.preamble.yincrement
                self.Y_Zero=self.preamble.yorigin
                self.Y_Offset=self.preamble.yreference
        else:
            self.X_Incr=1
            self.Point_Offset=0
            self.X_Zero=0
            #self.X_Unit=self.rdata[11]
            self.Y_Mult=1
            self.Y_Zero=0
            self.Y_Offset=0
            #self.Y_Unit=self.rdata[15]
        if (self.ENC == "ASCII" or self.ENC == "ASC"):
            self.conv_fmt=float
            self.wfsize=len(self.rdata.split(","))
            self.raw=self.rdata
        else:
            self.conv_fmt=self.BORD[self.BYTE_ORDER]+self.BFMT[self.BIN_FMT]
            self.wfsize=self.dsize
            self.raw=self.rdata
        self._convert()
        
    def update(self,curve):
        if (self.ENC == "ASCII" or self.ENC == "ASC"):
            self.wfsize=""
            if (curve[0] == ":"):
                self.raw=curve[len(":CURVE "):-1]
            else:
                self.raw=curve[:-1]
        else:
            if (curve[0] == "#"):
                sz=2+int(curve[1])
                self.wfsize=dsz=int(curve[2:sz])
                self.raw=curve[sz:-1]
            else:
                self.raw=curve[:-1]
        self._convert()

    def _convert(self):
        if (self.ENC == "ASCII" or self.ENC == "ASC"):
            self.wf=[float(x) for x in self.raw.split(",")]
        else:
            self.byte_width=self.DWIDTH[self.ENC]
            self.wf=[struct.unpack( self.conv_fmt, self.raw[i:i+self.byte_width])[0]
                     for i in range(0,
                                    len(self.raw)-len(self.raw)%self.byte_width,
                                     self.byte_width)]

        self.y=[((y-self.Y_Offset)*self.Y_Mult+self.Y_Zero) for y in self.wf]
        self.x=[ (x*self.X_Incr+self.X_Zero) for x in range(len(self.y))]
        
    def trace(self):
        return zip(self.x,self.y)

class TekCursor:
    def __init__(self,data):
        ent=data.split(";")
        self.function=ent[0]
        self.mode=ent[1]
        self.unit=ent[2]
        self.vpos=(float(ent[3]),float(ent[4]),float(ent[5]))
        self.hdelta=float(ent[6])
        self.select=ent[7]
        self.hpos=(float(ent[8]),float(ent[9]))
        self.hbarspos=(float(ent[10]),float(ent[11]),float(ent[12]))

def test(hostip="10.8.47.30"):
    import Gnuplot
    dso=AglDSO(hostip)
    #tek.set_fulldata()
    gp=Gnuplot.Gnuplot()
    return test_run(dso,gp)

def test_run(dso,gp):
    runstate=dso.qAcqState()
    stopafter=dso.qAcqStopAfter()
    dso.Stop()
    dso.set_AcqStopAfter("SEQ")
    dso.Run();dso.qOPC()
    wf1,wf2=test_update(dso,gp)
    dso.set_AcqStopAfter(stopafter)
    dso.set_AcqState(runstate)
    return (dso,wf1,wf2,gp)

def test_update(dso,gp):
    wf1=dso.get_waveform(1)
    wf2=dso.get_waveform(2)
    gp.title("Python VXI-11 module example from %s"%dso.Model)
    gp.plot(wf1.trace(),wf2.trace())
    return (wf1,wf2)

# for segmented data
def test_segment(ip="10.8.47.30"):
    dso=AglDSO(ip)
    messages=(
        "*RST;*CLS;\n", 
        ":ACQUIRE:TYPE NORMAL;\n", 
        ":ACQUIRE:MODE SEGMENTED;\n", 
        ":ACQUIRE:SEGMENTED:COUNT 10;\n", 
        ":TRIGGER:SWEEP NORMAL;\n", 
        ":TRIGGER:EDGE:SOURCE CHANNEL1;\n", 
        ":TRIGGER:EDGE:SLOPE NEGATIVE;\n", 
        ":TRIGGER:EDGE:LEVEL 1E+0;\n", 
        ":TIMEBASE:SCALE 1E-4;\n", 
        ":CHANNEL1:SCALE 1E+0;\n", 
        ":CHANNEL1:OFFSET 1E+0;\n", 
        ":CHANNEL1:DISPLAY ON;\n", 
        ":DISPLAY:CLEAR;\n", 
        ":WAVEFORM:FORMAT ASCII;\n", 
#        "*OPC?;\n", 
        )

    for message in messages:
        print message
        time.sleep(0.2)
        dso.write(message)
    print dso.ask("*OPC?\n", io_timeout=30000)
    dso.write(":SINGLE;\n")
    return dso

def get_segment(dso,n):
    dso.write(":ACQuire:SEGMented:INDex %d ;\n"%n)
    dso.write(":WAVEFORM:DATA?;\n")
    r=dso.readResponce()
    return r

# 
def test_mem_leak(ip="10.8.46.23"):
    import time,gc,resource, Gnuplot
    dso=AglDSO(ip)
    gp=Gnuplot.Gnuplot()
    gp('set term x11 noraise')
    dso.Stop()
    dso.Single()
    dso.set_wf_binary()
    dso.set_wf_format("WORD")
    dso.Single()
    dso.set_wf_point_mode("MAX")
    dso.Single()
    dso.set_wf_point("200000")
    dso.Single()
    print "data size:",dso.get_wf_point()
    dso.Single()
    w=None
    while 1:
        try:
            dso.Stop()
            dso.Single()
            time.sleep(2.0)
            #w=None
            del w
            w=dso.get_waveform()
            time.sleep(4)
            print "size of WF:", w.dsize
            gp.plot(w.trace())
        except:
            pass
        finally:
            try:
                dso.Single()
                #dso.Run()
            except:
                pass
        time.sleep(1.0)
        gc.collect()
        print time.ctime(), gc.get_count() , resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss

if __name__ == "__main__":
    test("10.8.46.23")
    """
    host:osc-mon-01.mr.jkcont
    ip:10.64.105.65
    MAC:00-30-d3-10-55-18

    host:osc-mon-02.mr.jkcont
    ip:10.64.105.66
    MAC:00-30-d3-10-55-19
    
    """
    messages=(
#        "*RST;*CLS;\n", 
        ":ACQUIRE:TYPE NORMAL;\n", 
        ":ACQUIRE:MODE SEGMENTED;\n", 
        ":ACQUIRE:SEGMENTED:COUNT 10;\n", 
        ":TRIGGER:SWEEP NORMAL;\n", 
        ":TRIGGER:EDGE:SOURCE CHANNEL1;\n", 
        ":TRIGGER:EDGE:SLOPE NEGATIXOVE;\n", 
        ":TRIGGER:EDGE:LEVEL 1E+0;\n", 
        ":TIMEBASE:SCALE 1E-4;\n", 
        ":CHANNEL1:SCALE 1E+0;\n", 
        ":CHANNEL1:OFFSET 1E+0;\n", 
        ":CHANNEL1:DISPLAY ON;\n", 
        ":DISPLAY:CLEAR;\n", 
        ":WAVEFORM:FORMAT ASCII;\n", 
        )

