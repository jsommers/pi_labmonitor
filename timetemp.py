#/usr/bin/env python3

import time
import os
import glob
import sys
import socket
import threading
import json
import atexit
import signal

class FakeGPIO(object):
    BCM = LOW = HIGH = IN = OUT = 0

    def __init__(self):
        pass

    def output(*args):
        pass

    def input(*args):
        pass 

    def setmode(*args):
        pass

    def setup(*args):
        pass

    def cleanup(*args):
        pass


try:
    import RPi.GPIO as GPIO
except:
    GPIO = FakeGPIO()
    print ("Warning: Can't import RPi.GPIO.  I hope you're just testing...")


GREEN = 18
RED = 23
BLUE = 25
LIGHT = 22

def clear_led():
    GPIO.output(GREEN, False)
    GPIO.output(RED, False)
    GPIO.output(BLUE, False)

def led_stripe():
    colors = [ GREEN, RED, BLUE ]
    setting = [ True, False, False ]
    for i in range(15):
        for i,c in enumerate(colors):
            GPIO.output(c, setting[i])
        setting.append(setting.pop(0))
        time.sleep(0.01)

def led_flash():
    colors = [ GREEN, RED, BLUE ]
    setting = True
    for i in range(13):
        for c in colors:
            GPIO.output(c, setting)
        setting = not setting
        time.sleep(0.01)

def update_led(ledstate, counter):
    # print ("Update LED {} {}".format(ledstate,counter))
    if counter % 13 == 0:
        led_stripe()
    elif counter % 101 == 0:
        led_flash()

    GPIO.output(GREEN, ledstate[GREEN])
    GPIO.output(RED, ledstate[RED])
    GPIO.output(BLUE, ledstate[BLUE])

    ledstate[GREEN] = ledstate[RED] = ledstate[BLUE] = False

    if counter % 3 == 0:
        ledstate[GREEN] = True
    elif counter % 3 == 1:
        ledstate[RED] = True
    else:
        ledstate[BLUE] = True

def light_reading():
    reading = 0
    GPIO.setup(LIGHT, GPIO.OUT)
    GPIO.output(LIGHT, GPIO.LOW)
    time.sleep(0.1)

    GPIO.setup(LIGHT, GPIO.IN)
    # This takes about 1 millisecond per loop cycle
    while (GPIO.input(LIGHT) == GPIO.LOW):
            reading += 1
    return reading

def read_temp_raw():
    base_dir = '/sys/bus/w1/devices/'
    try:
        device_folder = glob.glob(base_dir + '28*')[0]
    except:
        return ''
    device_file = device_folder + '/w1_slave'
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    if not lines:
        # it no workie --- no temperature found
        return 0.0,0.0

    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c, temp_f

def read_data(debug=False):
    light = 100
    temp = (10.0, 50.0)
    if not debug:
        light = light_reading()
        temp = read_temp()
    return json.dumps({'light':light, 'temperature':temp})

def nethandler():
    sock = socket.socket() # defaults to TCP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 7890))
    sock.listen(1)
    sock.settimeout(0.5)

    ledstate = { RED: False, GREEN: False, BLUE: False }
    counter = 0

    while True:
        counter += 1
        timeout = False
        newsock = None

        try:
            (newsock, remote_addr) = sock.accept()
        except socket.timeout:
            timeout = True
        except KeyboardInterrupt:
            break

        if timeout:
            update_led(ledstate, counter)

        if newsock:
            print ("Got connection from {}:{}".format(*remote_addr))
            xdata = read_data(debug=False)
            # print ("Sending <{}>".format(str(xdata)))
            newsock.sendall(xdata.encode('utf-8'))
            newsock.close()
            newsock = None

    sock.close()

def shutdown(*args):
    print ("Cleaning up.")
    clear_led()
    GPIO.cleanup()

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.setup(RED, GPIO.OUT)
    GPIO.setup(BLUE, GPIO.OUT)

    atexit.register(shutdown)
    nethandler()
