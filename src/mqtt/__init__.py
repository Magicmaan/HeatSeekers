#import modules from the mqtt package as relative imports
from .awtBroker import awtBroker, awtConnection
from .mqttBroker import mqttBroker
import subprocess
import os

#add to __all__ so that the modules can be imported using the * operator and shorthand.
#i.e. 
# from mqtt import *
# from mqtt import awtBroker

#instead of 
# from mqtt.awtBroker import awtBroker 
# or 
# from mqtt.awtBroker import awtConnection

def pingIP(ip_address: str) -> bool:
    """
    Ping an IP address and return True if the ping is successful, False otherwise.
    
    Args:
        ip_address (str): The IP address to ping.
    
    Returns:
        bool: True if the ping is successful, False otherwise.
    """
    # Determine the command based on the operating system
    command = ['ping', '-n', '1', ip_address] if os.name == 'nt' else ['ping', '-c', '1', ip_address]
    try:
        # Execute the ping command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Check the return code to determine if the ping was successful
        return result.returncode == 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


__all__ = ['awtBroker', 'awtConnection', 'pingIP', 'mqttBroker'
           ]