from os import getenv
from os import path
import platform
from dataclasses import dataclass, asdict
import time
START_TIME:float = time.time()

from System import Environment, DIRECTORIES, FILES, INSTANCE_FILES
from .setup_program import SetupProgram
SetupProgram()


#TODO: distinguish between platforms for directories
DATA_PATH = DIRECTORIES.DATA_PATH
CONNECTION_DATA_PATH = DIRECTORIES.CONNECTION_DATA_PATH

from .GUI.LoggerWindow import LoggerWindow, SensorLoggerWindow, MQTTLoggerWindow

from .program import Program

__all__ = [
    'Program',
    'DIRECTORIES',
    'FILES',
    'INSTANCE_FILES',
    'DATA_PATH',
    'CONNECTION_DATA_PATH',
    'START_TIME',
    
    'LoggerWindow',
    'SensorLoggerWindow',
    'MQTTLoggerWindow',
]
