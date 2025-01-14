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
from mqtt import awtBroker, awtConnection, mqttBroker
from multiprocessing import Process
from program.Logger import getLogger

logger = getLogger("PROGRAM")

class Program:
    #singleton instance
    __instance = None
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__ins'):
            print("Instance creating...")
            cls.__ins = super().__new__(cls)
        return cls.__ins
    
    def __init__(self, mqttMode="mqtt"):
        self.startTime = START_TIME
        self.mqttMode = mqttMode
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
        
        if self.mqttMode == "mqtt":
            self.mqttBroker = mqttBroker(autoStart=False)
        else:
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
    
    def _runAWS(self):
        self.awtBroker.connect()
        self.awtBroker.subscribe("test/topic")
        self.awtBroker.subscribe("test/cmd")
        self.awtBroker.subscribe("test/testing")
        self.awtBroker.subscribe("test/sensor_data")
        
        while True:
            temperature = self.sensor.temperature
            humidity = self.sensor.humidity
            self.awtBroker.publishSensorData(temperature, humidity)
            time.sleep(1)
    
    def _runMQTT(self):
        self.mqttBroker.connect()
        self.mqttBroker.subscribe("test/topic")
        while True:
            temperature = self.sensor.temperature
            humidity = self.sensor.humidity
            self.mqttBroker.publishSensorData(temperature, humidity)
            time.sleep(1)
    
    #program thread
    def run(self):
        if self.mqttMode == "mqtt":
            self._runMQTT()
        else:
            self._runAWS()
            
        
    
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