from enum import Enum
import os   
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json

def _blankPacket() -> dict:
    return {
        "identifier": f"python_mqtt_{formattedTime()}",
    }

def formattedTime() -> str:
    return t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())

def newPacket(message: str) -> str:
    packet = _blankPacket()
    packet.update({
        "message": message})
    
    return json.dumps(packet)

def newTestPacket() -> str:
    packet = _blankPacket()
    packet.update({
        "identifier":f"test_python_{formattedTime()}",
        "message": "Test"})
    
    return json.dumps(packet)


