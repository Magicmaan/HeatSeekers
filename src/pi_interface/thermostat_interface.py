from datetime import datetime
from program.Logger import getLogger, getSensorLogger


logger = getLogger()
sensorDataLogger = getSensorLogger()

class TemperatureMode:
    HEAT = "HEAT"
    COOL = "COOL"
    OFF = "OFF"
    AUTO = "AUTO"

class State:
    HEATING = "HEATING"
    COOLING = "COOLING"
    OFF = "OFF"

class DummyThermostat:
    def __init__(self):
        self.previousTemperatures = []
        self.previousTimes: list[float] = []
        self.temperature = 20.0
        self.humidity = 50.0
        self.temperatureGradient = 0.0
        
        self.temperatureLowerBound = 18.0
        self.temperatureUpperBound = 20.0
        self.desiredTemperature = 19.0
        
        self.temperatureMode = TemperatureMode.OFF
        self.state = State.OFF
    
    def updateTemperatureGradient(self):
        # return the average rate of change of the last 5 temperatures
        if (len (self.previousTemperatures) < 2): return
        if (len (self.previousTemperatures) > 5): self.previousTemperatures.pop(0)
        if (len (self.previousTimes) > 5): self.previousTimes.pop(0)
        
        #x axis is time, y axis is temperature
        p1 = [self.previousTimes[0], self.previousTemperatures[0]]
        p2 = [self.previousTimes[1], self.previousTemperatures[1]]
        
        # check for division by zero
        try:
            # calculate gradient from first and second points
            gradient = (p2[1] - p1[1]) / (p2[0] - p1[0])
        except ZeroDivisionError:
            gradient = 0.0
        
        self.temperatureGradient = gradient
    
    def update(self, temperature: float, humidity: float):
        # store the last 5 temperatures
        self.previousTemperatures.append(temperature)
        self.previousTimes.append(datetime.now().timestamp())
        
        self.temperature = temperature
        self.humidity = humidity
        self.updateTemperatureGradient()
        
        roundedTemperature = round(temperature, 1)
        # the following logic is a placeholder for the actual thermostat logic
        # if auto, aim for median bound ( with a 10% tolerance )
        # if cool, aim for between lower bound and median bound
        # if heat, aim for between median bound and upper bound
        if self.temperatureMode == TemperatureMode.AUTO:
            if roundedTemperature < self.desiredTemperature - (self.desiredTemperature * 0.05):
                self.dispatchHeat()
            elif roundedTemperature > self.desiredTemperature + (self.desiredTemperature * 0.05):
               self.dispatchCool()
            else:
                self.dispatchOff()
        
        elif self.temperatureMode == TemperatureMode.COOL:
            if roundedTemperature < self.desiredTemperature:
                self.dispatchOff()
            else:
                self.dispatchCool()

        elif self.temperatureMode == TemperatureMode.HEAT:
            if roundedTemperature > self.desiredTemperature:
                self.dispatchOff()
            else:
                self.dispatchHeat()


    def dispatchOff(self):
        if self.state == State.OFF:
            return
        self.state = State.OFF
        logger.info("Dispatching off")
        
    def dispatchHeat(self):
        self.state = State.HEATING
        logger.info("Dispatching heat")
        # placeholder to simulate heating
    
    def dispatchCool(self):
        self.state = State.COOLING
        logger.info("Dispatching cool")
        # placeholder to simulate cooling
    
    def setMode(self, mode: str):
        if mode not in [TemperatureMode.HEAT, TemperatureMode.COOL, TemperatureMode.OFF, TemperatureMode.AUTO]:
            logger.error(f"Invalid mode: {mode}")
            return
        
        self.temperatureMode = mode
    
    def setDesiredTemperature(self, desired: float):
        self.desiredTemperature = round(desired, 1)
    
    def getState(self) -> dict:
        """
        Retrieves the current state of the thermostat.

        Returns:
            dict: A dictionary containing the following keys:
                - temperature_lower_bound (float): The lower bound for temperature.
                - temperature_upper_bound (float): The upper bound for temperature.
                - temperature_medium_bound (float): The medium bound for temperature.
                - temperature_gradient (float): The temperature gradient.
                - temperatureMode (str): The current temperature mode.
                - state (str): The current state of the thermostat.
        """
        return {
            "desired_temperature": self.desiredTemperature,
            "temperature_gradient": self.temperatureGradient,
            "temperature_mode": self.temperatureMode,
            "state": self.state
        }