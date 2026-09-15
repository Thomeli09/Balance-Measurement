# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 11:58:52 2026

@author: Thommes Eliott
"""

import serial
import time

PORT = "COM3"      # change this
BAUDRATE = 9600    # check your scale manual

ser = serial.Serial(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

time.sleep(2)

# Send a command to the scale
command = b"Z\r\n"   # example only; depends on your scale
ser.write(command)

# Send a command to the scale
command = b"SI\r\n"   # example only; depends on your scale
ser.write(command)

# Read one response line
response = ser.readline()
print(response)
print(response.decode(errors="ignore"))

# ser.close()