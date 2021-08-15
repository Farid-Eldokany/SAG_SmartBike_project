from btle import *
from binascii import hexlify
import time
import MQTT

class MyDelegate(DefaultDelegate):
    
    def __init__(self):
        
        DefaultDelegate.__init__(self)
        
        self.power=None
        self.oldRevValue=None
        self.oldRevTime=None
        self.newRevValue=None
        self.newRevTime=None
        self.revPerSec=None
        self.revAchieved=None
        
    def parse_rev(self,data):
        data=str(hexlify(data))
        data=data[2:len(data)-1]
        val=data[8:16]
        little_hex = bytearray.fromhex(val)
        little_hex.reverse()
        data=str(hexlify(little_hex))
        data=data[2:len(data)-1]
        return int(data,16)
    def parse_power(self,data):
        data=str(hexlify(data))
        data=data[2:len(data)-1]
        val=data[4:8]
        little_hex = bytearray.fromhex(val)
        little_hex.reverse()
        data=str(hexlify(little_hex))
        data=data[2:len(data)-1]
        return int(data,16)
    def stopwatch(self,mode):
        
        if mode=="start":
            self.oldRevTime=int(time.perf_counter())
            return 0
        
        elif mode=="end":
            self.newRevTime=int(time.perf_counter())
            return self.newRevTime-self.oldRevTime
        
    def send_stats(self):
        
        MQTT.send_BikeRevolutions(self.revAchieved)
        MQTT.send_BikeSpeedMeasurement(self.revPerSec)
        MQTT.send_BikePower(self.power)
    def stats(self,revAchieved,time):
        if time==0:
            time=1
        self.revPerSec=revAchieved/time
        self.revAchieved=revAchieved
        
        print("                       ---BikeStats---")
        print("Revolutions per second: {s} \nRevolutions achived: {r}".format(s=self.revPerSec,r=self.revAchieved))
        print("-------------------------------------------------------------------")
    
    def handleNotification(self, cHandle, data):
        self.power=self.parse_power(data)
        data=self.parse_rev(data)
        if self.oldRevTime==None:
            self.stopwatch("start")
            self.oldRevValue=data
            return
        
        self.newRevValue=data
        time=self.stopwatch("end")
        self.stats(self.newRevValue-self.oldRevValue,time)
        self.send_stats()
        self.stopwatch("start")
        self.oldRevValue=data
        
class Bluetooth:
    
    def __init__(self, addr, chr):
        
        self.addr=addr
        self.chr=chr
        self.per=None
        
    def connect(self,mode):
        
        self.per = Peripheral(self.addr, mode)
        
    def subscribe(self):
        
        self.per.setDelegate(MyDelegate())
        setup_data = b"\x01\x00"
        notify = self.per.getCharacteristics(uuid=self.chr)[0]
        notify_handle = notify.getHandle() + 1
        self.per.writeCharacteristic(notify_handle, setup_data, withResponse=True)
        
    def disconnect(self):
        
        if self.per==None:
            return
        
        self.per.disconnect()
        
    def wait(self):
        
        while True:
            if self.per.waitForNotifications(1.0):
                continue