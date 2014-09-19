#/usr/bin/env python3

from tkinter import *
from tkinter.ttk import *
import time
import os
import glob
import sys
import socket
import threading
import json
import signal

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.__master = master
        self.pack()
        self.createWidgets()
        self.__running = True
        self.__time = '00:00:00'
        self.__temp = (0.0, 0.0)

    def isRunning(self):
        return self.__running

    def read_temp_raw(self):
        base_dir = '/sys/bus/w1/devices/'
        try:
            device_folder = glob.glob(base_dir + '28*')[0]
        except:
            self.set_status("No temperature device found")
            return ''
        device_file = device_folder + '/w1_slave'
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        lines = self.read_temp_raw()
        if not lines:
            # it no workie --- no temperature found
            return 0.0,0.0

        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                temp_f = temp_c * 9.0 / 5.0 + 32.0
                return temp_c, temp_f

    def createWidgets(self):
        style = Style()
        style.configure("TIME.TLabel", foreground="black", background="white", padding=10, relief="flat")
        style.configure("TEMP.TLabel", foreground="red", background="white", padding=10, relief="flat")
        style.configure("STAT.TLabel", foreground="blue", background="white", padding=5, relief="flat")

        self.status = Label(self, style="STAT.TLabel")
        self.status['font'] = 'Helvetica 14'
        self.set_status('all is well')

        self.time = Label(self, style="TIME.TLabel")
        self.time['font'] = 'courier 36 bold'
        self.update_time()
        self.time.pack(side="top")

        self.temp = Label(self, style="TEMP.TLabel")
        self.temp['font'] = 'courier 36 bold'
        self.update_temp()
        self.temp.pack(side="top")

        self.status.pack(side='top')

        self.QUIT = Button(self, text="exit", command=self.stop)
        self.QUIT.pack(side="bottom")

    def stop(self):
        self.__master.destroy()
        self.__running = False

    def update_time(self):
        currtime = time.localtime()
        self.__time = '{:02d}:{:02d}:{:02d}'.format(currtime.tm_hour, currtime.tm_min, currtime.tm_sec)
        self.time['text'] = self.__time

    def update_temp(self):
        self.__temp = self.read_temp()
        self.temp['text'] = '{:2.02f}\u00B0C / {:2.02f}\u00B0F'.format(self.__temp[0], self.__temp[1])

    def set_status(self, text):
        self.status['text'] = text

    def update_all(self):
        if not self.__running:
            return
        self.update_time()
        self.update_temp()
        if self.__running:
            self.after(1000, self.update_all)

    def get_data(self):
        return json.dumps({
            'time':self.__time,
            'celcius':self.__temp[0],
            'fahrenheit':self.__temp[1],
        })

def nethandler(theapp):
    sock = socket.socket() # defaults to TCP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 7890))
    sock.listen(1)
    sock.settimeout(0.5)
    while theapp.isRunning():
        try:
            (newsock, remote_addr) = sock.accept()
        except socket.timeout:
            continue  

        if newsock:
            # print ("Got connection from {}:{}".format(*remote_addr))
            xdata = theapp.get_data()
            # print ("Sending <{}>".format(str(xdata)))
            newsock.sendall(xdata.encode('utf-8'))
            newsock.close()
            newsock = None


root = Tk()
app = Application(master=root)
app.master.title("pi temperature monitor")
app.master.maxsize(400, 400)
root.after(1000, app.update_all)

def halt(*args):
    global app
    app.stop()
signal.signal(signal.SIGINT, halt)

netthread = threading.Thread(target=nethandler, args=(app,))
netthread.start()
app.mainloop()
netthread.join()

