from threading import Thread
import time
from . import DIRECTORIES,DATA_PATH, FILES
from . import SetupProgram
from .Logger import Logger
import os
from mqtt import awtBroker, awtConnection, pingIP


            

class Program:
    #singleton instance
    __instance = None
    def __new__(cls):
        if not hasattr(cls, '__ins'):
            print("Instance creating...")
            cls.__ins = super().__new__(cls)
        return cls.__ins
    
    def __init__(self):
        SetupProgram()
        self.startTime:float = time.time()
        self.logger = Logger(DIRECTORIES.LOGS_PATH)
        print("Logger created")
        
        
        

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
        
        self.awtBroker = awtBroker(self.awtConnection, autoStart=True)
        self.awtBroker.publish("Hello World", "test/testing")

        
        self.loggerThread = Thread(target=self.logger.start)
        self.mainThread = Thread(target=self.start)
        
        
        self.logger.start()
        self.mainThread.start()
        
        
        
    def start(self):
        """Start the program"""
        print("Program started")
        self.awtBroker.await_message(-1)
        pass

    
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