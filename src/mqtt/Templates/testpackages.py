from enum import Enum
import os   
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json


class packetGenerator:
    def __init__(self):
        pass
    
    def _blankPacket(self) -> dict:
        return {
            "identifier": f"python_mqtt_{self.formattedTime()}",
        }

    def formattedTime(self) -> str:
        return t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())
    
    def newPacket(self, message: str) -> str:
        packet = self._blankPacket()
        packet.update({
            "message": message})
        
        return json.dumps(packet)

    def newTestPacket(self) -> str:
        packet = self._blankPacket()
        packet.update({
            "identifier":f"test_python_{self.formattedTime()}",
            "message": "Test"})
        
        return json.dumps(packet)

