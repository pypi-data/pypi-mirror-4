#!/usr/bin/env pythonmake -k 
"""
Author:Noboru Yamamoto,KEK

Version 1.11.3. 

contact info: http://gofer.kek.jp/
or https://plus.google.com/i/xW1BWwWsj3s:2rbmfOGOM4c
Thanks:
   Dr. Shuei Yamada for improved vxi11scan.py
"""
import os,platform,re

from distutils.core import setup,Extension
rev="$Revision: 1.11.3.5 $"


sysname=platform.system()
if re.match("Darwin.*",sysname):
    RPCLIB=["rpcsvc"]
elif re.match("CYGWIN.*",sysname):
    RPCLIB=["rpc"]
else:
    RPCLIB=None

try:
    os.stat("./VXI11.h")
except OSError:
    os.system("rpcgen -C VXI11.rpcl")

setup(name="PyVXI11",
      version=rev[11:-2],
      description='Python modules to control devices over VXI11 protocol',
      author="Noboru Yamamoto, KEK, JAPAN",
      author_email = "Noboru.YAMAMOTO_at_kek.jp",
      url="http://www-acc.kek.jp/EPICS_Gr/products.html",
      py_modules=["VXI11","vxi11Device","TekOSC","vxi11Exceptions","vxi11scan"],
      ext_modules=[Extension("_VXI11",["VXI11.i","VXI11_clnt.c","VXI11_xdr.c"]
                             ,swig_opts=["-O","-nortti"]
                             ,libraries=RPCLIB
                             ),
                   # You may need to remove "-c++" option in some environment.
                   ]
      )
