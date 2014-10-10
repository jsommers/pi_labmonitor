#/usr/bin/env python3

import os
import glob
import sys
import atexit
import signal
import re

def read_temp_raw():
    base_dir = '/sys/bus/w1/devices/'
    try:
        device_folder = glob.glob(base_dir + '28*')[0]
    except:
        return ''
    # print (device_folder)
    device_file = os.path.join(device_folder, 'w1_slave')
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return [ s.strip() for s in lines ]

def read_temp():
    lines = read_temp_raw()
    if not lines:
        # it no workie --- no temperature found
        return 0.0,0.0

    if not lines[0].endswith('YES'):
        print ("Device not ready (first line not 'YES')")
        return 0.0,0.0

    mobj = re.search('t=(\d+)$', lines[1])
    if not mobj:
        print ("Can't find end of line stuff")
        return 0.0,0.0

    temp_c = float(mobj.groups()[0]) / 1000.0
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_c, temp_f

print (read_temp())
