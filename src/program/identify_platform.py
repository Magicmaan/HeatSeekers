import platform
class PLATFORM:
    """Class to identify the platform the program is running on\n
        Attributes:
            WINDOWS: int - Windows platform
            LINUX: int - Linux platform
            RASPBERRY_PI: int - Raspberry Pi platform
            UNKNOWN_UNIX: int - Unknown UNIX platform
            UNKNOWN: int - Unknown platform
        """
    WINDOWS = 0
    LINUX = 1
    RASPBERRY_PI = 2
    UNKNOWN = 3

def getPlatform() -> PLATFORM:
    """Get the platform the program is running on"""
    platform = PLATFORM.UNKNOWN
    if isWindows():
        platform = PLATFORM.WINDOWS
    elif isLinux():
        platform = PLATFORM.LINUX
    elif isRaspberryPi():
        platform = PLATFORM.RASPBERRY_PI
    
    return platform

def isRaspberryPi() -> bool:
    """Check if the program is running on a Raspberry Pi"""
    return False

def isWindows() -> bool:
    """Check if the program is running on Windows"""
    if platform.system() == "Windows":
        return True
    return False

def isLinux() -> bool:
    """Check if the program is running on Linux"""
    return False