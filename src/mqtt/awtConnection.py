from dataclasses import dataclass
import random


@dataclass
class awtConnection:
    """
    Class for AWS connection settings
    
    Arguments:
        endpoint (str): AWS broker URL
        cert_filepath (str): Path to certificate for Device
        pri_key_filepath (str): Path to private key for Device
        ca_filepath (str): Path to Amazon root CA
        client_id (str): Client ID for connection
    """
    endpoint:str
    cert_filepath:str
    pri_key_filepath:str
    ca_filepath:str
    client_id:str = f"python_mqtt"