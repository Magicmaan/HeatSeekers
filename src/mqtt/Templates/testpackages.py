from enum import Enum
import os
import platform   
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json

def _blankPacket(identifier: str = None) -> dict:
    if identifier:
        return {
            "identifier": identifier,
        }
    else:
        return {
            "identifier": f"{platform.node()}_python_mqtt",
        }

def newSensorPacket(temperature: float, humidity: float, units: list[str,str] = ["C","%"], identifier: str = None) -> str:
    packet = _blankPacket(identifier)
    packet.update({
        "temperature": temperature,
        "humidity": humidity,
        
        "units": {
            "temperature": units[0],
            "humidity": units[1]
        }
            
        })
    return json.dumps(packet)

def newPacket(message: str, identifier: str = None) -> str:
    packet = _blankPacket(identifier)
    packet.update({
        "message": message})
    
    return json.dumps(packet)

def newTestPacket(identifier: str = None) -> str:
    packet = _blankPacket(identifier)
    packet.update({
        "message": "Test"})
    
    return json.dumps(packet)


