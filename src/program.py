from paho.mqtt import client as mqtt
from paho.mqtt import enums as mqtt_enums
import os
from mqtt.awtBroker import awtBroker
from setupProgram import setupProgram

            

class Program:
    DATA_PATH:str = f"{os.getenv('APPDATA', '')}/HeatSeekers"
    
    def __init__(self):
        if not os.path.exists(self.DATA_PATH):
            print("Setting up app")
            self.setupApp()
        else:
            self.verifyAppData()
        self.getAppData()
        
        self.awtBroker = awtBroker()
        
        self.run()
    
    
        
    def run(self):
        self.client.loop_forever()
    
    def setupApp(self):
        #HeatSeekers
        # /mqtt
        #  host.txt
        #  /certs
        #    certificate.pem.crt
        #    private.pem.key
        #    ROOTCA1.pem
        #
        # /data
        #  /logs
        #  /device_name
        #    /temperature_data
        #    /humidity_data
        os.mkdir(self.DATA_PATH)
        
        os.mkdir(f'{self.DATA_PATH}/mqtt')
        os.mkdir(f'{self.DATA_PATH}/mqtt/certs')
        
        os.mkdir(f'{self.DATA_PATH}/data')
        os.mkdir(f'{self.DATA_PATH}/data/logs')
        
        setup_program = setupProgram()
        
    def verifyAppData(self):
        #TODO
        #verify that the app data is correct
        #verify hardware can be accessed
        #verify that the mqtt connection can be made
        return

if __name__ == "__main__":
    Program()