import RPi.GPIO as GPIO
import time

GREEN = 18
RED = 23
BLUE = 25

GPIO.setmode(GPIO.BCM)

GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)

redstate = False
greenstate = True
bluestate = greenstate
for i in range(100):
    greenstate = not greenstate
    redstate = not redstate
    bluestate = not bluestate
    GPIO.output(GREEN, greenstate)
    GPIO.output(RED, redstate)
    GPIO.output(BLUE, bluestate)
    time.sleep(0.1)

GPIO.output(GREEN, False)
GPIO.output(RED, False)
GPIO.output(BLUE, False)
   
GPIO.cleanup()
