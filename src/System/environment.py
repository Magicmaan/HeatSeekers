from dataclasses import dataclass
from os import getenv, path
import os
import platform
from platform import node
from enum import Enum
from program import START_TIME

class Environment:
    """Class to identify the platform the program is running on.
        OS (PLATFORM): The platform the program is running on.
        VERSION (str): The version of the operating system.
        ARCHITECTURE (str): The architecture of the operating system.
        PYTHON_VERSION (str): The version of Python being used.
    Methods:
        hasdht() -> bool:
            Check if the Raspberry Pi has a DHT sensor.
        getOS() -> PLATFORM:
            Get the platform the program is running on.
        isRaspberryPi() -> bool:
            Check if the program is running on a Raspberry Pi.
        isWindows() -> bool:
            Check if the program is running on Windows.
        isLinux() -> bool:
            Check if the program is running on Linux."""

    class PLATFORM(Enum):
        """
        Enum representing different platform types.\n
        Attributes:
            WINDOWS (int):          0
            LINUX (int):            1
            RASPBERRY_PI (int):     2
            UNKNOWN_UNIX (int):     3
            UNKNOWN (int):          4
            
        Methods:
            Get the enum member from its string value.
            Args:
                value (str): The string representation of the enum member.
            Returns:
                PLATFORM: The corresponding enum member.
            Raises:
                ValueError: If the string does not match any enum member.
            """
        WINDOWS: int = 0
        LINUX: int = 1
        RASPBERRY_PI: int = 2
        UNKNOWN_UNIX: int = 3
        UNKNOWN: int = 4
        
        @classmethod
        def from_string(cls, value: str):
            """Get the enum member from its string value"""
            value_upper = value.upper()
            for member in cls:
                if member.name == value_upper:
                    return member
            raise ValueError(f"{value} is not a valid {cls.__name__}")

    OS: PLATFORM = PLATFORM.from_string(platform.system())
    VERSION:str = platform.version()
    ARCHITECTURE:str = platform.architecture()[0]
    PYTHON_VERSION:str = platform.python_version()
    
    DEVICE_NAME:str = node()
    IDENTIFIER:str = f"{DEVICE_NAME}_python_mqtt"
    
    @classmethod
    def hasdht(cls) -> bool:
        """Check if the raspberrry pi has a DHT sensor"""
        if not cls.isRaspberryPi():
            return False
        
        
        return False
        #TODO: Implement
    
    @classmethod
    def getDeviceName(cls) -> str:
        """Get the name of the device"""
        return cls.DEVICE_NAME
    @classmethod
    def getIdentifier(cls) -> str:
        """Get the identifier of the device"""
        return cls.IDENTIFIER
    @classmethod
    def getOS(cls) -> PLATFORM:
        """Get the platform the program is running on"""
        return cls.OS
    
    @classmethod
    def isRaspberryPi(cls) -> bool:
        """Check if the program is running on a Raspberry Pi"""
        if cls.getOS() == cls.PLATFORM.RASPBERRY_PI:
            return True
        return False
    
    @classmethod
    def isWindows(cls) -> bool:
        """Check if the program is running on Windows"""
        if cls.getOS() == cls.PLATFORM.WINDOWS:
            return True
        return False
    
    @classmethod
    def isLinux(self) -> bool:
        """Check if the program is running on Linux"""
        #TODO: Implement
        return False

class WindowsDirectories:
    """Internal Class for Windows directories\n
    Arguments:
        DATA_PATH: str - Path to the main data directory
        CONNECTION_DATA_PATH: str - Path to the connection data directory
        MQTT_PATH: str - Path to the MQTT data directory
        CERTS_PATH: str - Path to the certificates directory
        CLIENT_DATA_PATH: str - Path to the client data directory
        LOGS_PATH: str - Path to the logs directory"""
        
    DATA_PATH: str = path.join(getenv('APPDATA'), 'HeatSeekers')
    CONNECTION_DATA_PATH: str = path.join(DATA_PATH, 'mqtt')
    MQTT_PATH: str = path.join(DATA_PATH, 'mqtt')
    CERTS_PATH: str = path.join(MQTT_PATH, 'certs')
    CLIENT_DATA_PATH: str = path.join(DATA_PATH, 'data')
    LOGS_PATH: str = path.join(CLIENT_DATA_PATH, 'logs')
    
    SENSOR_DATA_PATH: str = path.join(CLIENT_DATA_PATH, 'sensor_data')
    
class UnixDirectories:
    #TODO: Add UNIX directories
    """Internal Class for UNIX directories\n
    Arguments:
        DATA_PATH: str - Path to the main data directory
        CONNECTION_DATA_PATH: str - Path to the connection data directory
        MQTT_PATH: str - Path to the MQTT data directory
        CERTS_PATH: str - Path to the certificates directory
        CLIENT_DATA_PATH: str - Path to the client data directory
        LOGS_PATH: str - Path to the logs directory"""
    # TODO: Add UNIX directories
    DATA_PATH: str = None
    CONNECTION_DATA_PATH: str = None
    MQTT_PATH: str = None
    CERTS_PATH: str = None
    CLIENT_DATA_PATH: str = None
    LOGS_PATH: str = None
    
    SENSOR_DATA_PATH: str = None

@dataclass
class DIRECTORIES:
    """Class for directories\n
    Arguments:
        DATA_PATH: str - Path to the main data directory
        CONNECTION_DATA_PATH: str - Path to the connection data directory
        MQTT_PATH: str - Path to the MQTT data directory
        CERTS_PATH: str - Path to the certificates directory
        CLIENT_DATA_PATH: str - Path to the client data directory
        LOGS_PATH: str - Path to the logs directory
        
    ***Arguments are platform dependent***\n
    """

    platform = Environment.getOS()
    if platform == Environment.PLATFORM.WINDOWS:
        DATA_PATH: str =                WindowsDirectories.DATA_PATH
        CONNECTION_DATA_PATH: str =     WindowsDirectories.CONNECTION_DATA_PATH
        MQTT_PATH: str =                WindowsDirectories.MQTT_PATH
        CERTS_PATH: str =               WindowsDirectories.CERTS_PATH
        CLIENT_DATA_PATH: str =         WindowsDirectories.CLIENT_DATA_PATH
        
        LOGS_PATH: str =                WindowsDirectories.LOGS_PATH
        SENSOR_DATA_PATH: str =         WindowsDirectories.SENSOR_DATA_PATH
    elif platform == Environment.PLATFORM.LINUX | Environment.PLATFORM.RASPBERRY_PI:
        DATA_PATH: str =                UnixDirectories.DATA_PATH
        CONNECTION_DATA_PATH: str =     UnixDirectories.CONNECTION_DATA_PATH
        MQTT_PATH: str =                UnixDirectories.MQTT_PATH
        CERTS_PATH: str =               UnixDirectories.CERTS_PATH
        CLIENT_DATA_PATH: str =         UnixDirectories.CLIENT_DATA_PATH
        
        LOGS_PATH: str =                UnixDirectories.LOGS_PATH
        SENSOR_DATA_PATH: str =         UnixDirectories.SENSOR_DATA_PATH

@dataclass
class FILES:
    HOST: str = path.join(DIRECTORIES.CONNECTION_DATA_PATH, "host.txt")
    CERTIFICATE: str = path.join(DIRECTORIES.CONNECTION_DATA_PATH, "certs", "certificate.pem.crt")
    PRIVATE_KEY: str = path.join(DIRECTORIES.CONNECTION_DATA_PATH, "certs", "private.pem.key")
    ROOT_CA: str = path.join(DIRECTORIES.CONNECTION_DATA_PATH, "certs", "ROOTCA1.pem")
    TOPICS: str = path.join(DIRECTORIES.CLIENT_DATA_PATH, "topics.txt")

@dataclass
class INSTANCE_FILES:
    LOG_FILE: str = path.join(DIRECTORIES.LOGS_PATH, f"{START_TIME}_log.log")
    SENSOR_DATA_FILE: str = path.join(DIRECTORIES.SENSOR_DATA_PATH, f"{START_TIME}_sensor_data.json")
