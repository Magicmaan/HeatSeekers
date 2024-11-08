from threading import Thread
import time

from pi_interface import DHTSensor
from .Logger import getSensorLogger
from . import DIRECTORIES,DATA_PATH, FILES
from . import SetupProgram
from . import LoggerWindow
from . import SensorLoggerWindow
from . import MQTTLoggerWindow
from . import START_TIME
import os
from mqtt import awtBroker, awtConnection, pingIP
from multiprocessing import Process
from program.Logger import getLogger

logger = getLogger("PROGRAM")

class Program:
    #singleton instance
    __instance = None
    def __new__(cls):
        if not hasattr(cls, '__ins'):
            print("Instance creating...")
            cls.__ins = super().__new__(cls)
        return cls.__ins
    
    def __init__(self):
        self.startTime = START_TIME
        
        self.loggerWindow = LoggerWindow(blacklist=["SENSOR_DATA", "MQTT_CONNECTION"])
        self.tempReadingWindow = SensorLoggerWindow()
        self.mqttWindow = MQTTLoggerWindow()
        
        logger.info(f"Program started")
        #setup program / data
        SetupProgram()
        #get app data
        #includes connection data, etc
        self.getAppData()
        
        #create connection object containing the data
        self.awtConnection = awtConnection(
            self.host,
            self.cert,
            self.privateKey,
            self.rootCA
        )
        self.awtBroker = awtBroker(self.awtConnection, autoStart=False)
        self.sensor = DHTSensor()
        
        self.sensorThread = Thread(target=self.sensor.run)
        self.programThread = Thread(target=self.run)

        #start program thread
        self.sensorThread.start()
        self.programThread.start()
        self.loggerWindow.mainloop()
    

    #program thread
    def run(self):
        self.awtBroker.connect()
        self.awtBroker.subscribe("test/testing")
        self.awtBroker.subscribe("test/sensor_data")
        
        self.awtBroker.publish("Hello World", "test/testing")
        
        while True:
            temperature = self.sensor.temperature
            humidity = self.sensor.humidity
            
            print(f"Temperature: {temperature}")
            
            self.awtBroker.publish(f"Temperature: {temperature}", "test/sensor_data")
            
            time.sleep(1)
            
        
    
    def getRuntime(self) -> float:
        """Get the runtime of the program"""
        return time.time() - self.startTime
        
    def getAppData(self):
        files = FILES()
        self.host, self.cert, self.privateKey, self.rootCA = None, None, None, None
        
        with open(files.HOST, 'r') as f:
            self.host = f.read()
        self.cert = files.CERTIFICATE
        self.privateKey = files.PRIVATE_KEY
        self.rootCA = files.ROOT_CA
        


if __name__ == "__main__":
    Program()