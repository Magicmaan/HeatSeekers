import paho.mqtt.client as mqtt
from program import DATA_PATH
from .Templates import *
from dataclasses import asdict, dataclass
import platform
import time as t
import json
import random
import threading
from logging import DEBUG
from program.Logger import getLogger
from System.environment import Environment


logger = getLogger("LOCAL_BROKER")
connection_logger = getLogger("MQTT_CONNECTION")
#https://repost.aws/knowledge-center/iot-core-publish-mqtt-messages-python


class connectionState:
    DISCONNECTED = 0
    CONNECTED = 1
    CONNECTING = 2



    
class mqttBroker:   
    """Class for Local Broker connection
    
        If connection settings are provided, will connect on creation\n
        Otherwise, will need to call connect() to connect
    """
    def __init__(self, autoStart:bool=False):
        self.MESSAGE = "Hello World"
        self.TOPIC = "test/testing"
        self.messageCount = 0
        self._message_callback = None
        self.connection = mqtt.Client()
        self.connectionState = connectionState.DISCONNECTED
        
        if autoStart:
            self.connect()

    def connect(self) -> None:
        """Connect to Local broker"""
        assert not self.isConnected(), "Already connected"
        
        self.connection.on_connect = self._on_connect_success
        self.connection.on_disconnect = self._on_connect_close
        self.connection.on_message = self._on_message_received
        
        logger.info('Connecting to localhost...')
        self.connection.connect("localhost", 1883, 60)
        self.connection.loop_start()
        self.connectionState = connectionState.CONNECTED
    
    def disconnect(self) -> None:
        self.connection.disconnect()
        self.connection.loop_stop()
        self.connectionState = connectionState.DISCONNECTED
    
    def isConnected(self) -> bool:
        return self.connectionState == connectionState.CONNECTED
    
    def publish(self, message: str, topic: str, messageRepeat: int=1):
        """Publish message to desired topic"""
        assert self.isConnected(), "Not connected"
        assert messageRepeat > 0
        assert topic != ""
        
        for i in range(messageRepeat):
            result = self.connection.publish(topic, message)
            connection_logger.info(f"Publishing message to {topic}")
            connection_logger.debug(f"Message contents: {message}")
            result.wait_for_publish()
            self._on_publish_success(result)

    def publishSensorData(self, temperature: float, humidity: float, units: list[str,str] = ["C","%"]):
        """Publish sensor data"""
        data = newSensorPacket(temperature, humidity, units=units, identifier="local_client")
        self.publish(data, "test/sensor_data")
    
    def subscribe(self, topic: str):
        assert self.isConnected()
        self.connection.subscribe(topic)
        logger.info(f"Subscribed to {topic}")
        connection_logger.info(f"Subscribed to {topic}")
    
    def setMessageCallback(self, callback: callable):
        """Set the callback function for when a message is received\n
        Callback must accept two arguments: topic: str and payload: dict\n
        """
        assert callable(callback), "Callback must be callable"
        assert callback.__code__.co_argcount == 2, "Callback must accept exactly two arguments"
        self._message_callback = callback
    
    #callbacks
    def _on_connect_success(self, client, userdata, flags, rc): connection_logger.info("*** Connected ***\n"); logger.info("*** Connected ***\n"); self.connectionState = connectionState.CONNECTED
    def _on_connect_close(self, client, userdata, rc): connection_logger.info("*** Connection Closed ***\n"); self.connectionState = connectionState.DISCONNECTED
    def _on_publish_success(self, result): connection_logger.debug("Publish successful")
    def _on_message_received(self, client, userdata, msg): 
        payloadDecoded = json.loads(msg.payload.decode())
        self.messageCount += 1
        connection_logger.info(f"Received message from {msg.topic}")
        connection_logger.debug(f"Message contents: {payloadDecoded}")
        if self._message_callback:
            self._message_callback(msg.topic, payloadDecoded)




