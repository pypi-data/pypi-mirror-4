#!/bin/env python
#-* coding:utf-8 -*-
from VXI11 import *
from socket import *
import time,sys

def device_scan(host="10.9.16.20",device="inst0,0",command="*IDN?"):
    clnt=clnt_create(host,device_core_prog, device_core_version, "tcp")
    if not clnt:
        raise IOError

    create_link_1_arg=Create_LinkParms()
    device_write_1_arg=Device_WriteParms()
    device_read_1_arg=Device_ReadParms()
    device_clear_1_arg=Device_GenericParms()
    device_remote_1_arg=Device_GenericParms()

    
    create_link_1_arg.lockDevice=0
    create_link_1_arg.lock_timeout=0
    create_link_1_arg.device=device
    result_1 = create_link_1(create_link_1_arg, clnt)
    print "link created to %s \n"%create_link_1_arg.device
    print "\t Error code:%d\n\t LinkID:%d\n\t port %hd\n\t MaxRecvSize:%ld\n"%(
        	       result_1.error, result_1.lid ,
                       result_1.abortPort, result_1.maxRecvSize)
    # 
    #     create_intr_chan_arg=Device_RemoteFunc()
    #     create_intr_chan_arg.progFamily=VXI11.DEVICE_TCP
    #     create_intr_chan_arg.progNum=VXI11.device_intr_prog
    #     create_intr_chan_arg.progVers=VXI11.device_intr_version
    #     create_intr_chan_arg.hostAddr=socket.gethostbyname(socket.gethostname())
    #     create_intr_chan_arg.hostPort=myPort
    #     intr_link=create_intr_chan_1(create_intr_chan_arg,clnt)

    # check remote or not
    device_remote_1_arg.lid=result_1.lid;
    device_remote_1_arg.io_timeout=0;
    result_7 = device_remote_1(device_remote_1_arg, clnt);

    print "Device is remote. RC:%d\n"%result_7.error

    # send a command
    device_write_1_arg.lid=result_1.lid;
    device_write_1_arg.data.data_val = command
    device_write_1_arg.flags = device_flags_end;
    device_write_1_arg.data.data_len= len(device_write_1_arg.data.data_val)
    result_2 = device_write_1(device_write_1_arg, clnt);
    print "wrote %s\n"%device_write_1_arg.data.data_val

    # read response
    device_read_1_arg.lid=result_1.lid;
    device_read_1_arg.requestSize=255;
    device_read_1_arg.io_timeout=5;
    device_read_1_arg.lock_timeout=0;
    device_read_1_arg.flags = device_flags_termchrset
    device_read_1_arg.termChar='\n';

    result_3 = device_read_1(device_read_1_arg, clnt);
    print "%d bytes data read:%s\n"%(result_3.data.data_len,
                                      result_3.data.data_val)
    clnt_destroy (clnt);

def rpcinfo(host):
    import os
    os.system("/usr/sbin/rpcinfo -p %s"%host)

def read_wf(host="10.9.16.20",device="inst0,0"):

    clnt=clnt_create(host,device_core_prog, device_core_version, "tcp")
    if not clnt:
        raise IOError

    create_link_1_arg=Create_LinkParms()
    device_write_1_arg=Device_WriteParms()
    device_read_1_arg=Device_ReadParms()
    device_clear_1_arg=Device_GenericParms()
    device_remote_1_arg=Device_GenericParms()

    create_link_1_arg.lockDevice=0
    create_link_1_arg.lock_timeout=0
    create_link_1_arg.device=device
    result_1 = create_link_1(create_link_1_arg, clnt)
    print "link created to %s \n"%create_link_1_arg.device
    print "\t Error code:%d\n\t LinkID:%d\n\t port %hd\n\t MaxRecvSize:%ld\n"%(
                       result_1.error, result_1.lid ,
                       result_1.abortPort, result_1.maxRecvSize)
    #
    time.sleep(1.0)
    # read waveform

    # send command :set wf mode
    #device_write_1_arg.data.data_val = ":WFMP:ENC ASC; BN_F RI; BYT_N 2; BYT_O MSB;:HOR:RECORD 10000;:HEAD OFF;:VERBOSE ON;:DATA:START 1;:DATA:STOP 10000"
    device_write_1_arg.data.data_val = ":WFMP:ENC BIN; BN_F RI; BYT_N 2; BYT_O MSB;:HOR:RECORD 10000;:HEAD OFF;:VERBOSE ON;:DATA:START 1;:DATA:STOP 10000"
    device_write_1_arg.data.data_len= len(device_write_1_arg.data.data_val)
    result_2 = device_write_1(device_write_1_arg, clnt);
    print "wrote %s\n"%device_write_1_arg.data.data_val
    time.sleep(1.0/30)

    # send command
    device_write_1_arg.lid=result_1.lid;
    device_write_1_arg.flags = device_flags_end;
    device_write_1_arg.data.data_val = "DAT:SOU CH1;:WAVFRM?"
    #device_write_1_arg.data.data_val = "DAT:SOU CH2;:WAVFRM?"
    device_write_1_arg.data.data_len= len(device_write_1_arg.data.data_val)
    # read response
    device_read_1_arg.lid=result_1.lid;
    device_read_1_arg.requestSize=4096
    device_read_1_arg.io_timeout=5;
    device_read_1_arg.lock_timeout=0;
    device_read_1_arg.flags = device_flags_end
    device_read_1_arg.termChar='\n';

    result_2 = device_write_1(device_write_1_arg, clnt);
    print "wrote %s\n"%device_write_1_arg.data.data_val

    data=""

    while(1):
        result_3 = device_read_1(device_read_1_arg, clnt);
        if (result_3.error == 0):
#             print "%d bytes data read:%s (erc:%d)\n"%(
#                 result_3.data.data_len,
#                 result_3.data.data_val[:result_3.data.data_len],
#                 result_3.error)
            data=data+result_3.data.data_val[:result_3.data.data_len]
        else:
            break

    clnt_destroy (clnt)

    s=data.split(";")

    return (s[:-2],map(float,s[-1].split(",")))

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    if (argc==1):
        device_scan()
    elif (argc==2):
        device_scan(argv[1])
    elif (argc==3):
        device_scan(argv[1], argv[2])
    else:
        device_scan(argv[1], argv[2], argv[3])

