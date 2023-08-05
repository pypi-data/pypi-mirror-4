#!/bin/env python
#-* coding:utf-8 -*-
from VXI11 import *
from vxi11Exceptions import *
from socket import *
import time
import struct

class Vxi11Device:
    def __init__(self,host,device="gpib0,0",proto="tcp"):
        self.clnt=None
        try:
            self.clnt=clnt_create(host,
                                  device_core_prog, device_core_version,
                                  proto)
        except:
            raise IOError
        if not self.clnt:
            raise IOError
        
        self.abt=clnt_create(host,
                             device_async_prog, device_async_version,
                             proto)
        self.intr=clnt_create(host,device_intr_prog, device_intr_version, "udp")
        self.host=host
        self.device=device
        
        parm=Create_LinkParms()
        parm.lockDevice=0
        parm.lock_timeout=0
        parm.device=device

        res= create_link_1(parm, self.clnt)
        if (not res) or (res.error !=0):
            raise IOError,res.error

        self.lid=res.lid
        self.abortPort=res.abortPort
        self.maxRecvSize=res.maxRecvSize

    def create_intr_chan(self,host,intr_port):
        self.intr_host,self.intr_port=self.create_intr_handler()
        parm=Device_RemoteFunc()
        parm.progFamily=DEVICE_UDP
        parm.progNum=device_intr_prog
        parm.progVers=device_intr_version
        parm.hostAddr=self.intr_host
        parm.hostPort=self.intr_port
        res=create_intr_chan_1(parm,self.clnt)
        if (not res) or res.error != 0:
            raise RuntimeError,res
        parm=Device_GenericParms()
        parm.lid=self.lid
        parm.flags=flags
        parm.lock_timeout=lock_timeout
        parm.io_timeout=io_timeout
        res=device_trigger_1(parm, self.clnt)
        if (not res) or (res.error != 0):
            raise RuntimeError

    def intr_srq(self, handle_val=""):
        parm=Device_SrqParms()
        parm.handle.handle_val=handle_val
        parm.handle.handle_len=len(handle_val)
        res=device_intr_srq_1(parm,self.clnt)
        return res

    def abort(self):
        # need long *
        parm=longp()
        parm.assign(self.lid)
        res=device_abort_1(parm, self.abt)
        if res and res.error == 0:
            return
        else:
            raise RuntimeError

    def __del__(self):
        #res=destroy_intr_chan_1(None,self.clnt)
        #parm=longp()
        #parm.assign(self.lid)
        #res=destroy_link_1(parm, self.clnt)
        clnt_destroy (self.clnt)
        if self.abt:
            clnt_destroy (self.abt)
        if self.intr:
            clnt_destroy (self.intr)
        
    def remote(self,io_timeout=0):
        parm=Device_GenericParms()
        parm.lid=self.lid
        parm.io_timeout=io_timeout
        res = device_remote_1(parm, self.clnt)
        if res and res.error == 0:
            return "remote"
        else:
            return "local %d"%res.error

    def local(self, io_timeout=0):
        parm=Device_GenericParms()
        parm.lid=self.lid
        parm.io_timeout=io_timeout
        res = device_local_1(parm, self.clnt)
        if res and (res.error == 0):
            return "local"
        else:
            return "remote %d"%res.error

    def write(self,cmd="*IDN?;\n"):
        parm=Device_WriteParms()
        parm.lid=self.lid;
        parm.flags = device_flags_end;
        parm.data.data_val = cmd
        parm.data.data_len=len(cmd)
        res = device_write_1(parm, self.clnt);
        if (not res) or (res.error != 0):
            raise RuntimeError,res.error
        size=res.size
        release_Device_WriteResp(res)
        return size

    def read_one(self,requestSize=255,io_timeout=3000,lock_timeout=0,
             flags=device_flags_termchrset, termChar="\n"):
        # read response, timeout in msec.
        parm=Device_ReadParms()
        parm.lid=self.lid
        parm.requestSize=requestSize
        parm.io_timeout=io_timeout
        parm.lock_timeout=lock_timeout
        parm.flags = flags
        parm.termChar=termChar
        res= device_read_1(parm, self.clnt);
        if (not res) or (res.error != 0):
            raise IOError,res
        self.lastRes=res.get_binary_data()
        self.lastRes_reason=res.reason
        release_Device_ReadResp(res)
        return self.lastRes

    def read(self,requestSize=255,io_timeout=3000,lock_timeout=0,
             flags=device_flags_termchrset, termChar="\n"):
        resp=""
        r=self.read_one(requestSize=requestSize,
                     io_timeout=io_timeout,
                     lock_timeout=lock_timeout,
                     flags=flags,
                     termChar=termChar)
        if r:
            resp += r
            #print len(r),
        #print "reason:",self.lastRes_reason,"resp:",len(r),r
        while ((self.lastRes_reason
                & (Device_ReadResp_END|Device_ReadResp_CHR) == 0)):
            r=None
            try:
                r=self.read_one(requestSize=requestSize,
                             io_timeout=io_timeout,
                             lock_timeout=lock_timeout,
                             flags=flags,
                             termChar=termChar)
                #print "lastRes:",self.lastRes_reason,r,
                if r:
                    resp +=r
                    #print len(r)
            except IOError,m:
                print m
                break
            except TypeError,m:
                print m
                break
        return resp

    def readResponce(self,requestSize=4096,io_timeout=30):
        return self.read(requestSize=requestSize,io_timeout=io_timeout)
    
    def read_raw(self,requestSize=4096,io_timeout=30):
        return self.read(requestSize=requestSize,io_timeout=io_timeout)

    def ask(self,message,io_timeout=3000,termChar="\n",requestSize=255):
        """ A name borrowed from PyVISA module """
        self.write(message)
        return self.read(io_timeout=io_timeout,termChar=termChar,requestSize=255)

    def ask_block(self,message,io_timeout=3000):
        self.write(message)
        return self.readResponce(io_timeout=io_timeout)
        
    def readstb(self, flags=0,lock_timeout=0,io_timeout=5):
        parm=Device_GenericParms()
        parm.lid=self.lid
        parm.flags=flags
        parm.lock_timeout=lock_timeout
        parm.io_timeout=io_timeout
        res=device_readstb_1(parm, self.clnt)
        if (not res) or (res.error != 0):
            raise RuntimeError
        stb=res.stb
        release_Device_ReadStbResponce(res)
        return 

    def trigger(self,flags=0,lock_timeout=0,io_timeout=5):
        parm=Device_GenericParms()
        parm.lid=self.lid
        parm.flags=flags
        parm.lock_timeout=lock_timeout
        parm.io_timeout=io_timeout
        res=device_trigger_1(parm, self.clnt)
        if (not res) or (res.error != 0):
            raise RuntimeError
        
    def clear(self,flags=0,lock_timeout=0,io_timeout=5):
        parm=Device_GenericParms()
        parm.lid=self.lid
        parm.flags=flags
        parm.lock_timeout=lock_timeout
        parm.io_timeout=io_timeout
        res=device_clear_1(parm,self.clnt)
        if (not res) or (res.error != 0):
            raise RuntimeError,res

    def lock(self,flags=0,lock_timeout=0):
        parm=Device_LockParms()
        parm.lid=self.lid
        parm.flags=flags
        parm.lock_timeout=lock_timeout
        res=device_lock_1(parm,self.clnt)
        if (not res) or (res.error != 0):
            raise RuntimeError,res

    def unlock(self):
        parm=longp()
        parm.assign(self.lid)
        res=device_unlock_1(parm, self.clnt)
        if (not res) or (res.error != 0):
            raise RuntimeError,res
    
    def enable_srq(self,enable=True):
        parm=Device_EnableSrqParms()
        parm.lid=self.lid
        if enable:
            parm.enable=1
        else:
            parm.enable=0
        res=device_enablesrq(parm,self.clnt)
        if (not res) or (res.error != 0):
            raise RuntimeError,res

    def docmd(self,cmd, flags=0, io_timeout=5,
              lock_timeout=0, network_order=1, data_in_val=""):
        parm=Device_DocmdParms()
        parm.flags=flags
        parm.io_timeout=5
        parm.lock_timeout=lock_timeout
        parm.network_order=1
        parm.lid=self.lid
        parm.cmd=cmd
        parm.datasize=len(cmd)
        parm.data_in.data_in_val=data_in_val
        parm.data_in.data_in_len=len(data_in_val)
        res=device_docmd_1(parm,self.clnt)
        if (not res) or (res.error != 0):
            raise RuntimeError, res
        
        rval=res.data_out.data_out_val[:res.data_out.data_out_len]+"" # create copy of char * data
        release_Device_DcomdResp(res)
        return rval

    # Common * commsnds
    def CLS(self):
        return self.write("*CLS")

    def qESR(self):
        return self.ask("*ESR?")

    def ESE(self):
        return self.write("*ESE")

    def qESE(self):
        return self.ask("*ESE?")

    def qESR(self):
        return self.ask("*ESR?")
    
    def qIDN(self):
        return self.ask("*IDN?")

    def qLRN(self):
        self.write("*LRN?")
        return self.readResponce()

    def OPC(self):
        return self.write("*OPC")

    def qOPC(self):
        return self.ask("*OPC?")
    
    def qOPT(self):
        return self.ask("*OPT?")
    
    def RCL(self,value=0):
        "<value> ::= {0 | 1 | 2 | 3 | 4 |5 | 6 | 7 | 8 | 9}"
        return self.write("*RCL %d"%value)

    def SAV(self,value=0):
        "<value> ::= {0 | 1 | 2 | 3 | 4 |5 | 6 | 7 | 8 | 9}"
        return self.write("*SAV %d"%value)

    def RST(self):
        return self.write("*RST")

    def SRE(self,mask=255):
        """
        <mask> ::= sum of all bits thatare set, 0 to 255; an integer inNR1 format.
        <mask> ::= followingvalues:
        Bit Weight Name Enables
        --- ------ ---- ----------
        7 128 OPER Operation Status Reg
        6 64 ---- (Not used.)
        5 32 ESB Event Status Bit
        4 16 MAV Message Available
        3 8 ---- (Not used.)
        2 4 MSG Message
        1 2 USR User
        0 1 TRG Trigger
        quoted from "600_series_prog_refernce.pdf" by Agilent Tecnology.
        """
        return self.write("*SRE %d"%value)

    def qSRE(self,mask=255):
        return self.ask("*SRE?")

    def qSTB(self):
        """
        <value> ::= 0 to 255; an integer in NR1 format, as shown in the following:
        Bit Weight Name  "1" Indicates
        --- ------ ----  ---------------
        7   128   OPER  Operation status condition occurred. 
        6   64 RQS/ MSS Instrument is requesting service.
        5   32 ESB  Enabled event status condition occurred. 
        4   16 MAV  Message available. (Not used.)
        3   8 ---- 
        2   4 MSG   Message displayed. 
        1   2 USR   User event condition occurred. 
        0   1 TRG   A trigger occurred.
        quoted from "600_series_prog_refernce.pdf" by Agilent Tecnology.
        """
        return self.ask("*STB?")

    def TRG(self):
        return self.write("*TRG")

    def qTST(self):
        return self.ask("*TST?")

    def WAI(self):
        return self.write("*WAI")
    
def test(hostip="10.9.16.20"):
    import Gnuplot,time
    dev=Vxi11Device(host=hostip,device="inst0,0")
    print "remote Status:",dev.remote()
    dev.abort()

    print "remote Status:",dev.remote()
    dev.write("*IDN?;")
    print dev.read()

    wv1=""
    wv2=""
    gp=Gnuplot.Gnuplot(persist=1)
    dev.write("DAT:SOU CH1;:WAVFRM?")
    while 1:
        try:
            wv1 +=dev.read(io_timeout=1, requestSize=4096)
        except:
            break
    dev.write("DAT:SOU CH2;:WAVFRM?")
    time.sleep(0.05)
    while 1:
        try:
            wv2 +=dev.read(io_timeout=1,requestSize=4096)
        except:
            break

    dev.abort()
    dev.clear()

    h1=(wv1.split(";"))[:-1]
    h2=(wv2.split(";"))[:-1]

    try:
        d1=map(float, (wv1.split(";"))[-1].split(","))
        d2=map(float, (wv2.split(";"))[-1].split(","))
        gp.plot(d1,d2)
    except:
        d1=wv1
        d2=wv2
        pass
    return (gp,h1,h2,d1,d2)

if __name__ == "__main__":
    test()
