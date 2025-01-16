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
            "timestamp": t.time() * 1000 #milliseconds to match js
        }

def newStatePacket(sensorState: dict, thermostatState: dict, identifier: str = None) -> str:
    packet = _blankPacket(identifier)
    packet.update(sensorState)
    packet.update(thermostatState)
    
    return json.dumps(packet)

def newResponsePacket(response: str, command:str, value:str = "", identifier: str = None) -> str:
    packet = _blankPacket(identifier)
    packet.update({
        "response": response,
        "command": command,
        "command_args": value
    })
    
    return json.dumps(packet)

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


