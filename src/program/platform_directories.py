from os import getenv
from os import path
from dataclasses import dataclass
from .identify_platform import PLATFORM, getPlatform

@dataclass
class BaseDirectories:
    """Internal Base class for directories (empty)\n
    Arguments:
        DATA_PATH: str - Path to the main data directory
        CONNECTION_DATA_PATH: str - Path to the connection data directory
        MQTT_PATH: str - Path to the MQTT data directory
        CERTS_PATH: str - Path to the certificates directory
        CLIENT_DATA_PATH: str - Path to the client data directory
        LOGS_PATH: str - Path to the logs directory"""
    DATA_PATH: str
    CONNECTION_DATA_PATH: str
    MQTT_PATH: str
    CERTS_PATH: str
    CLIENT_DATA_PATH: str
    LOGS_PATH: str

@dataclass
class WindowsDirectories(BaseDirectories):
    """Internal Class for Windows directories\n
    Arguments:
        DATA_PATH: str - Path to the main data directory
        CONNECTION_DATA_PATH: str - Path to the connection data directory
        MQTT_PATH: str - Path to the MQTT data directory
        CERTS_PATH: str - Path to the certificates directory
        CLIENT_DATA_PATH: str - Path to the client data directory
        LOGS_PATH: str - Path to the logs directory"""
    DATA_PATH: str = f"{getenv('APPDATA', '')}\\HeatSeekers"
    CONNECTION_DATA_PATH: str = f"{DATA_PATH}\\mqtt"
    MQTT_PATH: str = f"{DATA_PATH}\\mqtt"
    CERTS_PATH: str = f"{MQTT_PATH}\\certs"
    CLIENT_DATA_PATH: str = f"{DATA_PATH}\\data"
    LOGS_PATH: str = f"{CLIENT_DATA_PATH}\\logs"

@dataclass
class UnixDirectories(BaseDirectories):
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


@dataclass
class DIRECTORIES(BaseDirectories):
    """Class for directories\n

    Arguments:
        DATA_PATH: str - Path to the main data directory
        CONNECTION_DATA_PATH: str - Path to the connection data directory
        MQTT_PATH: str - Path to the MQTT data directory
        CERTS_PATH: str - Path to the certificates directory
        CLIENT_DATA_PATH: str - Path to the client data directory
        LOGS_PATH: str - Path to the logs directory
        
    ***Arguments are platform dependent***\n
    Use  os.path.join()  to join paths\n
    Example:
    ```python
    from os import path
    from program import DIRECTORIES
    print(path.join(DIRECTORIES.DATA_PATH, "data"))
    ```
    """
    #arguments are platform dependent
    #so are generated at runtime
    DATA_PATH: str = None
    CONNECTION_DATA_PATH: str = None
    MQTT_PATH: str = None
    CERTS_PATH: str = None
    CLIENT_DATA_PATH: str = None
    LOGS_PATH: str = None
    
    platform = getPlatform()
    match platform:
        case PLATFORM.WINDOWS:
            DATA_PATH: str = WindowsDirectories.DATA_PATH
            CONNECTION_DATA_PATH: str = WindowsDirectories.CONNECTION_DATA_PATH
            MQTT_PATH: str = WindowsDirectories.MQTT_PATH
            CERTS_PATH: str = WindowsDirectories.CERTS_PATH
            CLIENT_DATA_PATH: str = WindowsDirectories.CLIENT_DATA_PATH
            LOGS_PATH: str = WindowsDirectories.LOGS_PATH
        case PLATFORM.LINUX | PLATFORM.RASPBERRY_PI:
            DATA_PATH: str = UnixDirectories.DATA_PATH
            CONNECTION_DATA_PATH: str = UnixDirectories.CONNECTION_DATA_PATH
            MQTT_PATH: str = UnixDirectories.MQTT_PATH
            CERTS_PATH: str = UnixDirectories.CERTS_PATH
            CLIENT_DATA_PATH: str = UnixDirectories.CLIENT_DATA_PATH
            LOGS_PATH: str = UnixDirectories.LOGS_PATH