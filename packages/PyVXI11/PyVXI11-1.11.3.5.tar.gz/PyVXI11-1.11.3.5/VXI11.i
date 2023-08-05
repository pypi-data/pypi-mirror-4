//VXI11.i
%module VXI11
%include typemaps.i
%include cstring.i
%include cpointer.i
%{
#include <rpc/rpc.h>
#include "VXI11.h"
void release_Device_ReadResp(Device_ReadResp *pResp){
        xdr_free((const xdrproc_t) xdr_Device_ReadResp, (char *) pResp);
}

void release_Device_ReadStbResp(Device_ReadStbResp *pResp){
        xdr_free((const xdrproc_t) xdr_Device_ReadStbResp, (char *) pResp);
}

void release_Device_WriteResp(Device_WriteResp *pResp){
        xdr_free((const xdrproc_t) xdr_Device_WriteResp, (char *) pResp);
}

void release_Device_DocmdResp( Device_DocmdResp *pResp){
        xdr_free((const xdrproc_t) xdr_Device_DocmdResp, (char *) pResp);
}
%}

//#include <rpc/rpc.h>
//%include "VXI11.h"

%pointer_class(long, longp)

#define RPCGEN_VERSION	199506
#define DEVICE_CORE ((unsigned long) 0x0607AF)
#define DEVICE_CORE_VERSION ((unsigned long) 1)

//#define DEVICE_CORE 395183
//#define DEVICE_CORE_VERSION 1

%constant unsigned long const device_core_prog = DEVICE_CORE;
%constant unsigned long const device_core_version = DEVICE_CORE_VERSION;

#define DEVICE_ASYNC ((u_long)0x0607B0)
#define DEVICE_ASYNC_VERSION ((u_long)1)

%constant unsigned long const device_async_prog = DEVICE_ASYNC;
%constant unsigned long const device_async_version = DEVICE_ASYNC_VERSION;

%typedef unsigned long u_long;
%typedef unsigned int u_int;
%typedef unsigned short  u_short;
%typedef unsigned char  u_char;
%typedef struct CLIENT CLIENT;
%typedef int bool_t;

%typedef long Device_Flags;
%constant long device_flags_termchrset = 0x80;
%constant long device_flags_end = 0x8;
%constant long device_flags_waitlock = 0x1;

//from rpc/clnt.h
CLIENT *clnt_create(char *host,
     	u_long prog,
	u_long vers,
	char *prot);

void clnt_destroy(CLIENT *);
void clnt_perror(CLIENT *,char *);
char *clnt_sperror(CLIENT *,char *);

%typedef long Device_Link;
%typedef Device_Link *Device_Linkptr;
typedef long Device_Link;
typedef Device_Link *Device_Linkptr;

%typedef struct XDR XDR;
typedef struct XDR XDR;

extern  bool_t xdr_Device_Link(XDR *, Device_Link*);

typedef enum Device_AddrFamily {
	DEVICE_TCP = 0,
	DEVICE_UDP = 1,
} Device_AddrFamily;
//%apply Device_AddrFamily *OUTPUT{Device_AddrFamily*}

//extern  bool_t xdr_Device_AddrFamily(XDR *, Device_AddrFamily*);

typedef long Device_ErrorCode;
struct Device_Error {
	Device_ErrorCode error;
};
%constant long Device_ErrorCode_No_Error = 0;
%constant long Device_ErrorCode_Syntax_Error = 1;
%constant long Device_ErrorCode_not_Accessible = 3;
%constant long Device_ErrorCode_invalid_Link_Id = 4;
%constant long Device_ErrorCode_Parm_Error = 5;
%constant long Device_ErrorCode_Chan_not_Established = 6;
%constant long Device_ErrorCode_Op_not_Supported = 8;
%constant long Device_ErrorCode_Out_of_Resoruces = 9;
%constant long Device_ErrorCode_Dev_Locked_by_Another = 11;
%constant long Device_ErrorCode_No_Lock_by_this_Link = 12;
%constant long Device_ErrorCode_IO_Timeout = 15;
%constant long Device_ErrorCode_IO_Error = 17;
%constant long Device_ErrorCode_Ivalid_Addr = 21;
%constant long Device_ErrorCode_Abort = 23;
%constant long Device_ErrorCode_Already_Established = 29;

//%apply Device_ErrorCode *OUTPUT{Device_ErrorCode*}
//%apply Device_Error *OUTPUT{Device_Error*}

extern  bool_t xdr_Device_ErrorCode(XDR *, Device_ErrorCode*);
extern  bool_t xdr_Device_Error(XDR *, Device_Error*);

struct Create_LinkParms {
	long clientId;
	bool_t lockDevice;
	u_long lock_timeout;
	char *device;
};


typedef struct Create_LinkParms Create_LinkParms;

extern  bool_t xdr_Create_LinkParms(XDR *, Create_LinkParms*);

struct Create_LinkResp {
	Device_ErrorCode error;
	Device_Link lid;
	u_short abortPort;
	u_long maxRecvSize;
};
typedef struct Create_LinkResp Create_LinkResp;

extern  bool_t xdr_Create_LinkResp(XDR *, Create_LinkResp*);

struct Device_WriteParms {
	Device_Link lid;
	u_long io_timeout;
	u_long lock_timeout;
	Device_Flags flags;
	struct {
		u_int data_len;
		char *data_val;
	} data;
};
typedef struct Device_WriteParms Device_WriteParms;

extern  bool_t xdr_Device_WriteParms(XDR *, Device_WriteParms*);

struct Device_WriteResp {
	Device_ErrorCode error;
	u_long size;
};
typedef struct Device_WriteResp Device_WriteResp;

extern  bool_t xdr_Device_WriteResp(XDR *, Device_WriteResp*);

struct Device_ReadParms {
	Device_Link lid;
	u_long requestSize;
	u_long io_timeout;
	u_long lock_timeout;
	Device_Flags flags;
	char termChar;
};
typedef struct Device_ReadParms Device_ReadParms;

extern  bool_t xdr_Device_ReadParms(XDR *, Device_ReadParms*);

struct Device_ReadResp {
	Device_ErrorCode error;
	long reason;
	struct Device_ReadResp_data {
		u_int data_len;
		char *data_val;
	} data;
};
typedef struct Device_ReadResp Device_ReadResp;
%constant long Device_ReadResp_REQCNT=1;
%constant long Device_ReadResp_CHR=2;
%constant long Device_ReadResp_END=4;

extern  bool_t xdr_Device_ReadResp(XDR *, Device_ReadResp*);

%extend Device_ReadResp{
	PyObject *get_binary_data(void){
                PyObject *pyobj;
                pyobj=SWIG_FromCharPtrAndSize(self->data.data_val,self->data.data_len);
		return pyobj;
	};
};

struct Device_ReadStbResp {
	Device_ErrorCode error;
	u_char stb;
};
typedef struct Device_ReadStbResp Device_ReadStbResp;

extern  bool_t xdr_Device_ReadStbResp(XDR *, Device_ReadStbResp*);

struct Device_GenericParms {
	Device_Link lid;
	Device_Flags flags;
	u_long lock_timeout;
	u_long io_timeout;
};
typedef struct Device_GenericParms Device_GenericParms;

extern  bool_t xdr_Device_GenericParms(XDR *, Device_GenericParms*);

struct Device_RemoteFunc {
	u_long hostAddr;
	u_long hostPort;
	u_long progNum;
	u_long progVers;
	Device_AddrFamily progFamily;
};
typedef struct Device_RemoteFunc Device_RemoteFunc;

extern  bool_t xdr_Device_RemoteFunc(XDR *, Device_RemoteFunc*);

struct Device_EnableSrqParms {
	Device_Link lid;
	bool_t enable;
	struct {
		u_int handle_len;
		char *handle_val;
	} handle;
};
typedef struct Device_EnableSrqParms Device_EnableSrqParms;

extern  bool_t xdr_Device_EnableSrqParms(XDR *, Device_EnableSrqParms*);

struct Device_LockParms {
	Device_Link lid;
	Device_Flags flags;
	u_long lock_timeout;
};
typedef struct Device_LockParms Device_LockParms;

extern  bool_t xdr_Device_LockParms(XDR *, Device_LockParms*);

struct Device_DocmdParms {
	Device_Link lid;
	Device_Flags flags;
	u_long io_timeout;
	u_long lock_timeout;
	long cmd;
	bool_t network_order;
	long datasize;
	struct {
		u_int data_in_len;
		char *data_in_val;
	} data_in;
};

typedef struct Device_DocmdParms Device_DocmdParms;

extern  bool_t xdr_Device_DocmdParms(XDR *, Device_DocmdParms*);

struct Device_DocmdResp {
	Device_ErrorCode error;
	struct {
		u_int data_out_len;
		char *data_out_val;
	} data_out;
};
typedef struct Device_DocmdResp Device_DocmdResp;

extern  bool_t xdr_Device_DocmdResp(XDR *, Device_DocmdResp*);
extern void release_Device_DocmdResp( Device_DocmdResp *);


#define device_abort ((u_long)1)
%constant unsigned long const _device_abort=device_abort;
extern  Device_Error * device_abort_1(Device_Link *, CLIENT *);

#define create_link ((u_long)10)
%constant unsigned long const _create_link=create_link;
extern  Create_LinkResp * create_link_1(Create_LinkParms *, CLIENT *OClient);

#define device_write ((u_long)11)
%constant unsigned long const _device_write=device_write;
extern  Device_WriteResp * device_write_1(Device_WriteParms *, CLIENT *);


#define device_read ((u_long)12)
%constant unsigned long const _device_read = device_read;
extern  Device_ReadResp * device_read_1(Device_ReadParms *, CLIENT *);

#define device_readstb ((u_long)13)
%constant unsigned long const _device_readstb = device_readstb;
extern  Device_ReadStbResp * device_readstb_1(Device_GenericParms *, CLIENT *);

#define device_trigger ((u_long)14)
%constant unsigned long const _device_trigger = device_trigger;
extern  Device_Error * device_trigger_1(Device_GenericParms *, CLIENT *);

#define device_clear ((u_long)15)
%constant unsigned long const _device_clear = device_clear;
extern  Device_Error * device_clear_1(Device_GenericParms *, CLIENT *);

#define device_remote ((u_long)16)
%constant unsigned long const _device_remote = device_remote;
extern  Device_Error * device_remote_1(Device_GenericParms *, CLIENT *);

#define device_local ((u_long)17)
%constant unsigned long const _device_local = device_local;
extern  Device_Error * device_local_1(Device_GenericParms *, CLIENT *);

#define device_lock ((u_long)18)
%constant unsigned long const _device_lock = device_lock;
extern  Device_Error * device_lock_1(Device_LockParms *, CLIENT *);

#define device_unlock ((u_long)19)
%constant unsigned long const _device_unlock = device_unlock;
extern  Device_Error * device_unlock_1(Device_Link *, CLIENT *);

#define device_enable_srq ((u_long)20)
%constant unsigned long const _device_enable_srq = device_enable_srq;
extern  Device_Error * device_enable_srq_1(Device_EnableSrqParms *, CLIENT *);

#define device_docmd ((u_long)22)
%constant unsigned long const _device_docmd = device_docmd;
extern  Device_DocmdResp * device_docmd_1(Device_DocmdParms *, CLIENT *);

#define destroy_link ((u_long)23)
%constant unsigned long const _destroy_link = destroy_link;
extern  Device_Error * destroy_link_1(Device_Link *, CLIENT *);

#define create_intr_chan ((u_long)25)
%constant unsigned long const _create_intr_chan = create_intr_chan;
extern  Device_Error * create_intr_chan_1(Device_RemoteFunc *, CLIENT *);

#define destroy_intr_chan ((u_long)26)
%constant unsigned long const _destroy_intr_chan = destroy_intr_chan;
extern  Device_Error * destroy_intr_chan_1(void *, CLIENT *);

//*C.2. Interrupt Protocol*/

struct Device_SrqParms {
	struct {
		u_int handle_len;
		char *handle_val;
	} handle;
};
typedef struct Device_SrqParms Device_SrqParms;

extern  bool_t xdr_Device_SrqParms(XDR *, Device_SrqParms*);

#define DEVICE_INTR ((u_long)0x0607B1)
#define DEVICE_INTR_VERSION ((u_long)1)
#define DEVICE_INTR_SRQ ((u_long)30)

%constant unsigned long const device_intr_prog = DEVICE_INTR;
%constant unsigned long const device_intr_version =DEVICE_INTR_VERSION;
%constant unsigned long const device_intr_srq = DEVICE_INTR_SRQ;


extern  void * device_intr_srq_1(Device_SrqParms *, CLIENT *);
//extern  void * device_intr_srq_1_svc(Device_SrqParms *, struct svc_req *);

extern void release_Device_ReadResp(Device_ReadResp *);
extern void release_Device_ReadStbResp(Device_ReadStbResp *);
extern void release_Device_WriteResp(Device_WriteResp *);
extern void release_Device_DocmdResp(Device_DocmdResp *);


