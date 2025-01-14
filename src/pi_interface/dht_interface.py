import logging
import time
import board
from time import sleep, time
from System import Environment
from random import random
from math import floor, sin, cos, sqrt, atan2, radians
from collections import deque

from datetime import datetime
from System import INSTANCE_FILES
from Util.data import predictFutureValue, getAverageData
from program.Logger import getSensorLogger, getLogger


logger = getLogger("DHTSensor")
sensorDataLogger = getSensorLogger()

try:
    import adafruit_dht
except ImportError:
    print("Error importing adafruit_dht")

class DummySensor:
    """Dummy sensor class to simulate"""
    def __init__(self):
        self._temperature = 20
        self._humidity = 50
    
    def generateTemperature(self):
        self._temperature = 20 + 5 * sin(time() / 100)
    
    def generateHumidity(self):
        self._humidity = 50 + 10 * cos(time() / 100)
        
    @property
    def temperature(self):
        self.generateTemperature()
        return self._temperature
    @temperature.setter
    def temperature(self, value):
        self._temperature = value
    
    @property
    def humidity(self):
        self.generateHumidity()
        return self._humidity
    @humidity.setter
    def humidity(self, value):
        self._humidity = value
    
    def exit(self):
        print("Exiting dummy sensor")
        
class DHTSensor:
    """Class to interface with the DHT sensor
    Arguments:
        useDummy:bool - Whether to use a dummy sensor or not
    
    Methods:
        getData() -> tuple[float, float]:
            Returns the last temperature and humidity data
        querySensor() -> tuple[float, float]:
            Queries the sensor for temperature and humidity data
        run():
            Main sensor loop to constantly query the sensor
    """
    #TODO
    def __init__(self, useDummy:bool=False):
        logger.info("-"*10 + "\nInitializing DHT Sensor")
        if not useDummy:
            logger.debug("Attempting to initialize sensor")
            hasSensor = True
            if not Environment.isRaspberryPi(): logger.error("Not running on a Raspberry Pi"); hasSensor = False
            if not Environment.hasdht(): logger.error("Raspberry Pi does not have a DHT sensor"); hasSensor = False
            
            if hasSensor:
                self.sensor = adafruit_dht.DHT22(board.D4)
                logger.info("Sensor initialized")
            else:
                logger.error("Failed to initialize sensor. Using fallback Dummy Sensor") 
                self.sensor = DummySensor()
        else:
            self.sensor = DummySensor()
            logger.info("Using dummy sensor")

        #how often to query the sensor in seconds
        self.queryInterval:int = 1
        self.lastQueryTime:float = time()
        

        self.dataCacheSize:int = 50
        self.dataCache = deque(maxlen=self.dataCacheSize)
        
        self.temperature:float = 0
        self.humidity:float = 0
    

    
    def getData(self) -> tuple[float, float]:
        """Get the last temperature and humidity readings"""
        return list(self.dataCache)

    def getAverageData(self) -> float:
        return getAverageData(self.dataCache)
    
    def getPredictedTemperature(self, timestep:int) -> float:
        return predictFutureValue(self.dataCache, timestep)
    
    def querySensor(self) -> tuple[float, float]:
        """Query the sensor for temperature and humidity data

        Returns:
            tuple[float, float]: Temperature and humidity data
            
        Can also return None, None if there is an error
        """
        try:
            temperature = self.sensor.temperature
            humidity = self.sensor.humidity
            
            return temperature, humidity
        except Exception as e:
            #happens often
            logger.error(f"Error querying sensor: {e}")
        
        return None, None
    
    def run(self):
        #main sensor loop to constantly query the sensor
        while True:
            #query the sensor for data
            temperatureData, humidityData = self.querySensor()
            #if data is returned
            if temperatureData and humidityData: 
                self.lastQueryTime = time()
                self.temperature = temperatureData
                self.humidity = humidityData
                
                #append the data to the data cache
                #also adds to lastTemp and lastHumidity
                self.dataCache.append([self.lastQueryTime, self.temperature, self.humidity])
                #log the data to the sensor data file
                msg = {
                    "timestamp": datetime.now().time().__str__(),  
                    "temperature": round(self.temperature, 2), 
                    "humidity": round(self.humidity, 2),
                    "predicted_temperature": round(predictFutureValue(self.dataCache, 10), 2),
                    "units": {
                        "temperature": "C",
                        "humidity": "%"
                    }
                }
                sensorDataLogger.log(logging.DEBUG,msg)
            else:
                sleep(1)

            sleep(self.queryInterval)
        
        print("Sensor thread ended")