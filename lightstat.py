#!/usr/bin/env python3
 
# Example for RC timing reading for Raspberry Pi
# Must be used with GPIO 0.3.1a or later - earlier verions
# are not fast enough!
 
import math, time, os
import RPi.GPIO as GPIO
 
DEBUG = 1
GPIO.setmode(GPIO.BCM)
 
def RCtime (RCpin):
        reading = 0
        GPIO.setup(RCpin, GPIO.OUT)
        GPIO.output(RCpin, GPIO.LOW)
        time.sleep(0.1)
 
        GPIO.setup(RCpin, GPIO.IN)
        # This takes about 1 millisecond per loop cycle
        while (GPIO.input(RCpin) == GPIO.LOW):
                reading += 1
        return reading

 
lvals = [ RCtime(22) for _ in range(25) ]
GPIO.cleanup()

n = float(len(lvals))
lavg = sum(lvals) / n
var = (( sum([x**2 for x in lvals]) * n ) - ( sum(lvals) ** 2.0 )) / (n * (n - 1))

threshold = 3000

status = "off"
if lavg >= threshold:
    status = "on"

print ("Lights: likely {} (average reading {:.1f}, sdev {:.1f})".format(status, lavg, math.sqrt(var)))
