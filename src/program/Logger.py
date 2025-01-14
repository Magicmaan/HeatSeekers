from logging import FileHandler, Handler, getLogger, Formatter, Logger
import logging
import string
from pythonjsonlogger import jsonlogger
from System.environment import INSTANCE_FILES

loggerFileHandler: Handler = FileHandler(INSTANCE_FILES.LOG_FILE)
loggerFileHandler.addFilter(lambda record: record.name != "SENSOR_DATA")
sensorFileHandler: Handler = FileHandler(INSTANCE_FILES.SENSOR_DATA_FILE)

# create log formatter
logFormatter: Formatter = Formatter(datefmt='%H:%M:%S', fmt='%(asctime)s %(name)s - %(levelname)s - %(message)s')
# create sensor log formatter (outputs json)
sensorLogFormatter: jsonlogger.JsonFormatter = jsonlogger.JsonFormatter('%(timestamp)s %(temperature)s %(humidity)s %(units)s')

loggerFileHandler.setFormatter(logFormatter)
sensorFileHandler.setFormatter(sensorLogFormatter)


print("Sensor logger created")
sensorDataLogger: Logger = getLogger("SENSOR_DATA")
sensorDataLogger.setLevel("DEBUG")
print(f"sensor handlers: {sensorDataLogger.handlers}")
sensorDataLogger.addHandler(sensorFileHandler)


rootLogger: Logger = getLogger()
rootLogger.setLevel("DEBUG")
rootLogger.addFilter(lambda record: record.name != "SENSOR_DATA")
rootLogger.addHandler(loggerFileHandler)


def getSensorLogger() -> Logger:
    return sensorDataLogger


def getLogger(name:string="ROOT") -> Logger:
    if name == "SENSOR_DATA":
        return sensorDataLogger
    if name == "ROOT":
        return rootLogger
    
    logger: Logger = logging.getLogger(name)
    logger.setLevel("DEBUG")
    logger.addHandler(loggerFileHandler)
    return logger