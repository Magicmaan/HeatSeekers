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
from pi_interface.thermostat_interface import State as thermostatState
from program.Logger import getSensorLogger, getLogger


logger = getLogger()
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
        #testing interface to respond to heating / cooling
        self._temperature = 20 + 5 * sin(time() / 10)
    
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
        logger.info("Initializing DHT Sensor")
        # initialize the sensor
        # if useDummy is True, use a dummy sensor
        # if not on raspberry pi, use a dummy sensor
        # if no dht sensor, use a dummy sensor
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

        self.useDummy = useDummy
        self.thermostatState = thermostatState.OFF
        #how often to query the sensor in seconds
        self.queryInterval:int = 10
        self.lastQueryTime:float = time()
        

        self.dataCacheSize:int = 50
        self.dataCache = deque(maxlen=self.dataCacheSize)
        
        self.temperature:float = 0
        self.humidity:float = 0
    

    def setThermostatState(self, state:thermostatState):
        self.thermostatState = state

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

    
    def getState(self) -> dict:
        """Get the state of the sensor"""
        return {
            "temperature": round(self.temperature,1),
            "humidity": round(self.humidity,0),
            "units": {
                "temperature": "C",
                "humidity": "%"
            }
        }
    
    def run(self):
        #main sensor loop to constantly query the sensor
        while True:
            #if use dummy, simulate heating / cooling
            if self.useDummy:
                if self.thermostatState == thermostatState.HEATING:
                    logger.debug("Heating artificially")
                    temperatureData = self.temperature + 0.5
                elif self.thermostatState == thermostatState.COOLING:
                    logger.debug("Cooling artificially")
                    temperatureData = self.temperature - 0.5
                else:
                    temperatureData, humidityData = self.querySensor()
            else:
                temperatureData, humidityData = self.querySensor()
            #query the sensor for data
            
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
                    "timestamp": datetime.now().strftime("%H:%M:%S"),  
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