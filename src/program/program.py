from threading import Thread
import time

from pi_interface import DHTSensor
from . import DIRECTORIES,DATA_PATH, FILES
from . import SetupProgram
from . import LoggerWindow
from . import START_TIME
import os
from mqtt import awtBroker, awtConnection, pingIP
from multiprocessing import Process
from logging import getLogger



            

class Program:
    #singleton instance
    __instance = None
    def __new__(cls):
        if not hasattr(cls, '__ins'):
            print("Instance creating...")
            cls.__ins = super().__new__(cls)
        return cls.__ins
    
    def __init__(self):
        logger = getLogger("Program")
        self.startTime = START_TIME
        self.loggerWindow = LoggerWindow()
        logger.info(f"Program started")
        
        self.programThread = Thread(target=self.run)
        
        
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
        
        self.sensor = DHTSensor(useDummy=True)
        self.sensorThread = Thread(target=self.sensor.run)

        #start program thread
        self.sensorThread.start()
        self.programThread.start()
        self.loggerWindow.mainloop()
        
    #program thread
    def run(self):
        self.awtBroker.connect()
        self.awtBroker.subscribe("test/testing")
        
        self.awtBroker.publish("Hello World", "test/testing")
        
    
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