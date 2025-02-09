from datetime import datetime

import json
import sys
from threading import Thread
import time

from Util.logUtil import concatenateSensorLogs, getSensorLogsDate
from mqtt.Templates.testpackages import _blankPacket, newResponsePacket, newStatePacket
from pi_interface import DHTSensor, DummyThermostat
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
# def _onMessageReceived(str1, str2):
#     print(f"Message received: {str1} - {str2}")
#     logger.info(f"Message received: ")
    

"""
A class to represent the main program.
Attributes
----------
mqttMode : str
    The mode of MQTT connection, either "mqtt" or "awt".
Methods
-------
__new__(cls, *args, **kwargs):
    Creates a singleton instance of the Program class.
__init__(self, mqttMode="mqtt"):
    Initializes the Program with the specified MQTT mode.
onMessageReceived(self, topic: str, payload: dict):
    Handles incoming MQTT messages and executes commands based on the payload.
run(self):
    The main program loop that updates sensor data and publishes it to the MQTT broker.
getRuntime(self) -> float:
    Returns the runtime of the program.
getAppData(self):
    Retrieves application data such as host, certificate, private key, and root CA.
"""
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
        self.loggerWindow = LoggerWindow(blacklist=["SENSOR_DATA", "MQTT_CONNECTION"], exit=self.exit)
        self.tempReadingWindow = SensorLoggerWindow( exit=self.exit)
        self.mqttWindow = MQTTLoggerWindow( exit=self.exit)
        self.isRunning = True
        logger.info(f"Program started")
        #setup program / data
        SetupProgram(mqttMode=mqttMode)
        #get app data
        #includes connection data, etc
        self.getAppData()
        
        #create connection object containing the data
        self.broker = None
        if self.mqttMode == "mqtt":
            logger.info(f"Using MQTT local broker")
            self.broker = mqttBroker(self.host, autoStart=False, onMessageReceived=self.onMessageReceived)
        elif self.mqttMode == "awt":
            logger.info(f"Using AWS IoT broker")
            self.awtConnection = awtConnection(
                self.host,
                self.cert,
                self.privateKey,
                self.rootCA
            )
            
            self.broker = awtBroker(self.awtConnection, autoStart=False)
        
        self.publishInterval = 10
        self.sensor = DHTSensor(useDummy=True)
        self.thermostat = DummyThermostat()
        
        self.sensorThread = Thread(target=self.sensor.run, args=([self.isRunning]))
        self.programThread = Thread(target=self.run)

        #start program thread
        self.sensorThread.start()
        self.programThread.start()
        self.loggerWindow.mainloop()
    
    def onMessageReceived(self, topic: str, payload: dict):
        # message format:
        # {
        #   "command": "set_temperature_medium_bound",
        #   "value": 0.0
        # }
        # get messages from topic command
        if topic.lower().find("command") != -1:
            command = payload.get("command", "")
            if command == "" or command == None:
                logger.error(f"Command not found in payload: {payload}")
                return
            logger.info(f"Command received: {command}")
            
            
            if command.lower().find("stop") != -1:
                self.stop()
            elif command.lower().find("start") != -1:
                self.start()
            # send state
            if command.lower().find("state") != -1:
                logger.info(f"Sending state: {self.thermostat.getState()}")
                packet = newStatePacket(self.sensor.getState(), self.thermostat.getState())
                self.broker.publish(packet, "test/response")

            # set desired temperature
            if command.lower().find("set_desired_temperature") != -1:
                logger.info(f"Setting desired temperature to {payload.get('value',self.thermostat.desiredTemperature)}")
                self.thermostat.setDesiredTemperature(
                    desired=payload.get("value", self.thermostat.desiredTemperature),
                )
                # respond with new state
                packet = newStatePacket(self.sensor.getState(), self.thermostat.getState())
                self.broker.publish(packet, "test/sensor_data")
            
            # set temperature mode
            if command.lower().find("set_temperature_mode") != -1:
                logger.info(f"Setting temperature mode to {payload.get('value', self.thermostat.temperatureMode)}")
                self.thermostat.setMode(
                    mode=payload.get("value", self.thermostat.temperatureMode)
                )
                # respond with new state
                packet = newStatePacket(self.sensor.getState(), self.thermostat.getState())
                self.broker.publish(packet, "test/sensor_data")
            
            if command.lower().find("get_history") != -1:
                day = payload.get('value', datetime.now().strftime('%Y%m%d'))
                logger.info(f"Getting history for {day}")
                
                files = getSensorLogsDate(day)
                if not files:
                    return
                
                #data = concatenateSensorLogs([os.path.join(DIRECTORIES.SENSOR_DATA_PATH, "input.json")], "hour")
                #print(data)
                data = concatenateSensorLogs(files, "hour")
                logger.debug(f"Data: {data}")
                # with open(os.path.join(DIRECTORIES.SENSOR_DATA_PATH, 'text.json'), 'w') as f:
                #     for entry in data:
                #         f.write(json.dumps(entry) + '\n')
                
                packet = newResponsePacket(json.dumps(data), "get_history", day)
                self.broker.publish(packet, "test/response")
                #DIRECTORIES.SENSOR_DATA_PATH
   
   
    #program thread
    def run(self):
        self.broker.connect()
        self.broker.subscribe("test/topic")
        self.broker.subscribe("test/command")
        self.broker.subscribe("test/response")
        self.broker.subscribe("test/testing")
        while self.isRunning:
            temperature = self.sensor.temperature
            humidity = self.sensor.humidity
            self.thermostat.update(temperature, humidity)

            if (self.sensor.useDummy):
                self.sensor.setThermostatState(self.thermostat.state)
            #if int(time.time()) % self.publishInterval == 0:
            packet = newStatePacket(self.sensor.getState(), self.thermostat.getState())
            self.broker.publish(packet, "test/sensor_data")
    
            time.sleep(self.publishInterval)
        
        self.broker.disconnect()
            
    def getRuntime(self) -> float:
        """Get the runtime of the program"""
        return time.time() - self.startTime
        
    def getAppData(self):
        files = FILES()
        self.host, self.cert, self.privateKey, self.rootCA = None, None, None, None
        
        with open(files.HOST, 'r') as f:
            self.host = f.read()
        if self.mqttMode == "aws":
            self.cert = files.CERTIFICATE
            self.privateKey = files.PRIVATE_KEY
            self.rootCA = files.ROOT_CA
    
    def exit(self):
        self.isRunning = False
        self.loggerWindow.quit()
        self.tempReadingWindow.quit()
        self.mqttWindow.quit()
        print("Program stopped")
        os._exit(1)
        


if __name__ == "__main__":
    Program()