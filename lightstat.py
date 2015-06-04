#!/usr/bin/env python3

import math, time, os
import RPi.GPIO as GPIO

GREEN = 18
RED = 23
BLUE = 25
lightpins = ( GREEN, RED, BLUE )
DEBUG = 1

GPIO.setmode(GPIO.BCM)

for pin in lightpins:
    GPIO.setup(pin, GPIO.OUT)

for pin in lightpins:
    GPIO.output(pin, False)

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

 
for pin in lightpins:
    GPIO.output(pin, True)

lvals = [ RCtime(22) for _ in range(3) ]

time.sleep(1.0)

for pin in lightpins:
    GPIO.output(pin, False)

GPIO.cleanup()

n = float(len(lvals))
lavg = sum(lvals) / n
var = (( sum([x**2 for x in lvals]) * n ) - ( sum(lvals) ** 2.0 )) / (n * (n - 1))

threshold = 500

status = "off"
if lavg <= threshold:
    status = "on"

print ("Lights: likely {} (average reading {:.1f}, sdev {:.1f})".format(status, lavg, math.sqrt(var)))
