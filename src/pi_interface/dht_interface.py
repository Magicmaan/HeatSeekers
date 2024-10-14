import logging
import time
import board
from logging import FileHandler, getLogger
from time import sleep, time
from System import Environment
from random import random
from math import floor, sin, cos, sqrt, atan2, radians
from collections import deque

from System import INSTANCE_FILES
from Util.data import predictFutureValue, getAverageData

logger = logging.getLogger("DHTSensor")
logger.setLevel(logging.DEBUG)

sensorDataLogger = getLogger("SENSOR_DATA")
# Remove any existing handlers
sensorDataLogger.setLevel(logging.DEBUG)

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
        if not useDummy:
            if not Environment.isRaspberryPi():
                logger.error("Not running on Raspberry Pi, cannot use DHT sensor")
                return
            if not Environment.hasdht():
                logger.error("Raspberry Pi does not have a DHT sensor")
                return
            
            self.sensor = adafruit_dht.DHT22(board.D4)
        else:
            self.sensor = DummySensor()
            logger.info("Using dummy sensor")
        
        formatter = logging.Formatter(datefmt='%H:%M:%S', fmt='%(asctime)s: %(message)s')
        sensorDataFile = FileHandler(INSTANCE_FILES.SENSOR_DATA_FILE)
        sensorDataFile.setFormatter(formatter)
        sensorDataLogger.addHandler(sensorDataFile)
        
        sensorDataLogger.info("Sensor data logger started")


        #how often to query the sensor in seconds
        self.queryInterval:int = 1
        self.lastQueryTime:float = time()
        
        #data cache to store the last n data points
        #DataCache = {
        # [time:int, temperature:float, humidity:float],   
        # [time:int, temperature:float, humidity:float],
        # [time:int, temperature:float, humidity:float],
        # ...
        # }
        self.dataCacheSize:int = 50
        self.dataCache = deque(maxlen=self.dataCacheSize)
        
        self.lastTemperature:float = 0
        self.lastHumidity:float = 0
        
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
                self.lastTemperature = temperatureData
                self.lastHumidity = humidityData
                
                #append the data to the data cache
                #also adds to lastTemp and lastHumidity
                self.dataCache.append([self.lastQueryTime, self.lastTemperature, self.lastHumidity])
                #log the data to the sensor data file
                msg = f"Temperature: {round(self.lastTemperature,2)} Humidity: {round(self.lastHumidity,2)}"
                sensorDataLogger.log(logging.DEBUG, msg)
                
                predictedTemperature = predictFutureValue(self.dataCache, 10)
                msg = f"Predicted temperature in 10 seconds: {round(predictedTemperature, 2)}"
                sensorDataLogger.log(logging.DEBUG, msg)
            else:
                sleep(1)

            sleep(self.queryInterval)
        
        print("Sensor thread ended")