import time
from . import DATA_PATH
from . import setupProgram
import os
from mqtt import awtBroker, pingIP


            

class Program:
    #singleton instance
    __instance = None
    def __new__(cls):
        if not hasattr(cls, '__ins'):
            print("Instance creating...")
            cls.__ins = super().__new__(cls)
        return cls.__ins
    
    def __init__(self):
        if not os.path.exists(DATA_PATH):
            print("Setting up app")
            self.setupApp()
        else:
            self.verifyAppData()
        self.getAppData()
        
        self.awtBroker = awtBroker()
        
        self.startTime:float = time.time()
        
        self.run()
    
    def getRuntime(self) -> float:
        """Get the runtime of the program"""
        return time.time() - self.startTime
        
        
    def setupApp(self):
        setup_program = setupProgram()
        
    def verifyAppData(self) -> bool:
        isVerified = False
        #TODO
        if os.path.exists(f"{DATA_PATH}/mqtt/host.txt"):
            with open(f"{DATA_PATH}/mqtt/host.txt", 'r') as f:
                pingIP
        else:
            print("No host.txt")
            isVerified = True

        if os.path.exists(f"{DATA_PATH}/mqtt/certs/certificate.pem.crt"):
            with open(f"{DATA_PATH}/mqtt/certs/certificate.pem.crt", 'r') as f:
                content = f.read()
                print(content)
        
        #verify that the app data is correct
        #verify hardware can be accessed
        #verify that the mqtt connection can be made
        
        
        
        #else:
        #    print("Setting up app")
        #    self.setupApp()
        
        return False

if __name__ == "__main__":
    Program()