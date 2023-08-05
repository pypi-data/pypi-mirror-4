#
#-*- coding:utf-8 -*-
"""
A module to support LeCroy Osciloscope
(C) Noboru Yamamoto,2009. KEK, Ibaraki, JAPAN
Reference:
 LeCroy WM-RCM-E_Rev.D 
jkjblade05.16: ../vxi11scan 10.8.47.32

 Get RPC info
   program vers proto   port
    395183    1   tcp    641
    395184    1   tcp    641
    395183    1   udp    638
    395184    1   udp    638

 START scanning.
link created to gpib0,0 
	 Error code:9
	 LinkID:-1
	 port 0
	 MaxRecvSize:29491
Device is remote. RC:0
wrote *IDN?;

	 Error code:0
	 Size:7
start to read
41 bytes data read:*IDN LECROY,WP760ZI,LCRY0715N47661,5.9.0

IP:10.64.105.64
host:osc-mon-d116.mr.jkcont
"""

import vxi11Device
import time,types,struct,exceptions
import array,struct,numpy

class WP700Z(vxi11Device.Vxi11Device):
    def __init__(self, device, timeout=5):
        #visa.Instrument.__init__(self, device, timeout=timeout)
        vxi11Device.Vxi11Device.__init__(self, host=device, device="inst0")
        self.device=device
        self.timeout=timeout
        self.write("CHDR OFF") # always header off
        self.IDN_Str=self.IDN()
        ID=self.IDN_Str[:-1].split(",")
        self.Make=ID[0]
        self.Model=ID[1]
        self.Option=ID[3]

    def IDN(self):
        return self.ask("*IDN?;")

    def respToDict(self, lables,resp):
        v=resp[:-1].split(";")
        d={}
        d.update(zip(lables,v))
        return d

    def qALST(self):
        return self.ask("ALST?")

    def ATTN(self,ch="C1",att=1):
        """
        <channel> : = {C1, C2, C3, C4, EX, EX10}
        <attenuation> : = {1, 2, 5, 10, 20, 25, 50, 100, 200,500, 1000, 10000}
        """
        return self.write("%s:ATTN %d;"%(ch,att))

    def qATTN(self,ch="C1"):
        return self.ask("%s:ATTN?;"%ch)

    def ACAL(self, state="ON"):
        """<state> : = {ON, OFF}"""
        return self.write("ACAL %s;"%state)

    def qACAL(self):
        return self.ask("ACAL?;")

    def ASET(self, ch="C1",FIND=False):
        """
        <channel> : = {C1, C2, C3, C4}
        """
        if FIND:
            self.write("%s:ASET FIND"%ch)
        else:
            self.write("%s:ASET"%ch)
            
    def qBWL(self):
        return self.ask("BWL?")
    
    def BWL(self,mode="OFF"):
        """
        BandWidth_Limit <mode>
        BandWidth_Limit <channel>,<mode>[,<channel>,<mode>[,<channel>,<mode>[,<channel>,<mode>]]]
        <mode> : = {OFF, ON, 200MHZ,1GHZ,3GHZ*,4GHZ*}
        Note: OFF = Full, ON = 20MHz
        <channel> : = {C1, C2, C3, C4}
        """
        return self.write("BLW %s"%mode)
    
    def ARM(self):
        self.ask("ARM;")
        
    def BUZZ(slef,state="BEEP"):
        """
        <state>:= {BEEP, ON, OFF}
        """
        return self.write("BUZZ %s;"%state)


    def qCAL(self):
        return self.ask("*CAL?")

    def COUT(self,mode,level="",rate="",width=""):
        """
        Cal_OUTput <mode>[,<level>[,<rate>]]
        Cal_OUTput PULSE[,<width>]
        <mode> : = {OFF, CALSQ, PF, TRIG, LEVEL,ENABLED}
        <level> : = 5 mV to 1.00 V into 1 MOhm
        <rate> : = 5 Hz to 5 MHz.
        """
        if mode == "PULSE":
            if width:
                return self.write("COUT PULSE,%s"%width)
            else:
                return self.write("COUT PULSE;")
        else:
            if rate:
                return self.write("COUT %s,%s,%s"%(mode,level,rate))
            elif level:
                return self.write("COUT %s,%s"%(mode,level))
            else:
                return self.write("COUT %s"%mode)
            
    def CLM(self,memory):
        """
        CLear_Memory < memory>
        <memory> : = {M1, M2, M3, M4}
        """
        return self.write("CLM %s"%memory)

    def CLSW(self):
        """
        CLear SWeeps
        """
        return self.write("CLSW;")
    
    def qCMR(self):
        """
        The CMR? query reads and clears the contents of the CoMmand errorRegister (see table next page) which specifies the last syntax error typedetected by your oscilloscope.
        COMMAND ERROR STATUS REGISTER STRUCTURE (CMR)
        Value Description
        1 Unrecognized command/query header
        2 Illegal header path
        3 Illegal number
        4 Illegal number suffix
        5 Unrecognized keyword
        6 String error
        7 GET embedded in another message
        10 Arbitrary data block expected
        11 Non-digit character in byte count field of arbitrary data block
        12 EOI detected during definite length data block transfer
        13 Extra bytes detected during definite length data block transfer
        """
        return self.ask("CMR?;")

    def COMB(self, state="AUTO"):
        """
        COMBine_channels <state>
        <state> : = {1, 2, AUTO}
        Selecting 1 means no combining of channels will take place; i.e., inthe Timebase (Horizontal) dialog, 4 channels will be shown as theselection.
        """
        return self.write("COMB %s"%state)
    

    def CFMT(self, block_format, data_type, encoding):
        """
        Comm_ForMaT <block_format>,<data_type>,<encoding>
        <block_format> : = {DEF9}
        <data_type> : = {BYTE, WORD}
        <encoding> : = {BIN}
        """
        return self.write("CFMT %s,%s,%s"%(block_format, data_type, encoding))
    
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
        """
        WAVEFORM_SETUP, WFSU:The WAVEFORM_SETUP command specifies the amount of data ina waveform to be transmitted to the controller. The commandcontrols the settings of the parameters listed below.
        
        np:number of points
        fp:first point(0..N-1)
        sp:sparsing(0..N). Sends every SP data point
        sn:segment number (0..Nseg-1)
        """
        trace=("C1","C2","C3","C4", "TA", "TB", "TC","TD",
               "M1","M2","M3","M4")
        if (ch in trace):
            self.write("WFSU NP, %d, FP, %d, SP, %d" % (np,fp,sp))
            return self.ask("%s:WAVEFORM?" % ch)
        elif (ch in (1,2,3,4)):
            self.write("WFSU NP, %d, FP, %d, SP, %d" % (np,fp,sp))
            return self.ask("C%d:WAVEFORM?" % ch)

    def Run(self):
        self.write(":ACQ:STATE RUN;")

    def Stop(self):
        self.write(":ACQ:STATE STOP;")

    def clear(self):
        self.write("*CLS;")
        
    def wait(self):
        self.write("*WAI;")
        
    def device_clear(self,flags=0,lock_timeout=0,io_timeout=5):
        vxi11Device.Vxi11Device.clear(self, flags, lock_timeout, io_timeout)


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
def endian_set(cord, instrument_name):
    if cord==1: # LO FIRST
        endian="<"
        endiandouble="<"
    else: # HI FIRST
        endian=">"
        endiandouble=">"
    return endian, endiandouble

class waveform:
    def __init__(self,data,withtimes=False,withwavedesc=False):
        try:
            npos=data.index("#")
        except ValueError:
            raise ValueError,"invalid format"            
        header=data[:npos]
        data=data[npos:]
        self.dsize=int(data[2:][:int(data[1])])
        wfdata=data[2:][int(data[1]):]
        if (len(wfdata) < self.dsize):
            print "Not Enough Data:",
            print data[:12],self.dsize, len(wfdata)
            #raise exceptions.ValueError,"Not enough data"
        instrument_name=array.array('c',wfdata[76:92]).tostring().strip('\x00')
        cord = struct.unpack('b',wfdata[34])[0]
        endian, endiandouble = endian_set(cord, instrument_name)
        wavedesclen=struct.unpack('%sl'%endian,wfdata[36:40])[0]
        usertextlen=struct.unpack('%sl'%endian,wfdata[40:44])[0]
        regdesclen=struct.unpack('%sl'%endian,wfdata[44:48])[0]
        trigtimearraylen=struct.unpack('%sl'%endian,wfdata[48:52])[0]
        ristimearraylen=struct.unpack('%sl'%endian,wfdata[52:56])[0]
        resarraylen=struct.unpack('%sl'%endian,wfdata[52:56])[0]
        wavearray1len=struct.unpack('%sl'%endian,wfdata[60:64])[0]
        wavearray2len=struct.unpack('%sl'%endian,wfdata[64:68])[0]
        wavearrayoffset=wavedesclen+usertextlen+regdesclen+trigtimearraylen+ristimearraylen+resarraylen

        vgain=struct.unpack('%sf'%endian,wfdata[156:160])[0]
        voffset=struct.unpack('%sf'%endian,wfdata[160:164])[0]
        vunit=struct.unpack('c',wfdata[196])[0]
        hinterval=struct.unpack('%sf'%endian,wfdata[176:180])[0]
        hoffset=struct.unpack('%sd'%endiandouble,wfdata[180:188])[0]
        hunit=struct.unpack('c',wfdata[244])[0]
        sparcing_factor=struct.unpack('%sl'%endian,wfdata[136:140])[0]
        datanum=struct.unpack('%sl'%endian,wfdata[116:120])[0]
        
        data=numpy.fromstring(wfdata[wavearrayoffset:wavearrayoffset+wavearray1len], dtype=numpy.int8)
        if len(data) > 10000000:
            for i in xrange(len(data)):
                data[i] =data[i]*vgain-voffset
        else:
            data =data*vgain-voffset
        if withtimes:
            if sparcing_factor==0:
                tdata=numpy.array(map(lambda i: hinterval*i+hoffset, range(0,datanum)))
            else:
                tdata=numpy.array(map(lambda i: hinterval*i*sparcing_factor+hoffset, range(0,datanum)))
            self.x=tdata
        else:
            self.x=None

        ############
        self.y=data
        self.ENC=endian
        self.point_fmt=endian
        #
        self.BIN_FMT="BYTE"   #check!
        self.BYTE_ORDER=cord  #check!
        self.Data_Num=datanum
        self.X_Incr=hinterval
        self.Point_Offset=hoffset
        self.X_Zero=0
        self.X_Unit=hunit
        self.Y_Mult=vgain
        self.Y_Zero=0
        self.Y_Offset=voffset
        self.Y_Unit=vunit
        self.desc=(header, instrument_name,cord, vgain,voffset,vunit, hinterval,hoffset,hunit,sparcing_factor)
        
    def trace(self):
        if self.x:
            return zip(self.x,self.y)
        else:
            return self.y


def test(hostip="10.64.105.64"):
    import Gnuplot
    osc=WP700Z(hostip)
    gp=Gnuplot.Gnuplot()
    return (osc,gp)

if __name__ == "__main__":
    test()
    
