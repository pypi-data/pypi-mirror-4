class vxi11_Device_Error(IOError):
    Error_Code=0

class Device_Syntax_Error (vxi11_Device_Error):
    Error_Code=1

class Device_not_Accessible (vxi11_Device_Error): 
    Error_Code = 3 

class Device_invalid_Link_Id (vxi11_Device_Error): 
    Error_Code = 4 

class Device_Parm_Error (vxi11_Device_Error): 
    Error_Code = 5 

class Device_Chan_not_Established (vxi11_Device_Error): 
    Error_Code = 6 

class Device_Op_not_Supported (vxi11_Device_Error): 
    Error_Code = 8 

class Device_Out_of_Resoruces (vxi11_Device_Error): 
    Error_Code = 9 

class Device_Dev_Locked_by_Another (vxi11_Device_Error): 
    Error_Code = 11 

class Device_No_Lock_by_this_Link (vxi11_Device_Error): 
    Error_Code = 12 

class Device_IO_Timeout (vxi11_Device_Error): 
    Error_Code = 15 

class Device_IO_Error (vxi11_Device_Error): 
    Error_Code = 17 

class Device_Ivalid_Addr (vxi11_Device_Error): 
    Error_Code = 21 

class Device_Abort (vxi11_Device_Error): 
    Error_Code = 23 

class Device_Already_Established (vxi11_Device_Error): 
    Error_Code = 29 
