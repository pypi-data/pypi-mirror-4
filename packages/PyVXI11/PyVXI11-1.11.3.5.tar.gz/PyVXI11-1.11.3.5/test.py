#!/bin/env python
import vxi11Device

def test():
    osc=vxi11Device.Vxi11Device("10.33.41.74","inst0,0")
    w=osc.ask_block("C1:WAVEFORM? DESC")
    print len(w),w


if __name__ == "__main__":
    test()
    
