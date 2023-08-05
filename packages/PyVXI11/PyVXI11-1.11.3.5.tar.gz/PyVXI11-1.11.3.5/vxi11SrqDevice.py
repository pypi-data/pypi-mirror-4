
class vxi11SrqServer:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def enable(self):
        pass

    def disable(self):
        pass

# struct Device_RemoteFunc {
# 	u_long hostAddr;
# 	u_short hostPort;
# 	u_long progNum;
# 	u_long progVers;
vxiCreateIrqChannel
# 	Device_AddrFamily progFamily;
# };

#     /* create the interrupt channel */
#     devRemF.hostAddr = ntohl(srqBindAddr.ia.sin_addr.s_addr);
#     devRemF.hostPort = ntohs(srqBindAddr.ia.sin_port);
#     devRemF.progNum = DEVICE_INTR;
#     devRemF.progVers = DEVICE_INTR_VERSION;
#     devRemF.progFamily = DEVICE_TCP;
#     memset((char *) &devErr, 0, sizeof(Device_Error));
#     clntStat = clientCall(pvxiPort,  create_intr_chan,
#         (const xdrproc_t) xdr_Device_RemoteFunc, (void *) &devRemF,
#         (const xdrproc_t) xdr_Device_Error, (void *) &devErr);
