import paho.mqtt.client as mqtt
from mqtt.Templates.testpackages import _blankPacket
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
from .brokerBase import BrokerBase
from paho.mqtt.client import MQTT_ERR_SUCCESS 

logger = getLogger("LOCAL_BROKER")
connection_logger = getLogger("MQTT_CONNECTION")
#https://repost.aws/knowledge-center/iot-core-publish-mqtt-messages-python


class connectionState:
    DISCONNECTED = 0
    CONNECTED = 1
    CONNECTING = 2



    
class mqttBroker(BrokerBase):   
    """Class for Local Broker connection
    
        If connection settings are provided, will connect on creation\n
        Otherwise, will need to call connect() to connect
    """
    def __init__(self, 
                 autoStart: bool = False, 
                 onMessageReceived: callable = None, 
                 onConnect: callable = None, 
                 onDisconnect: callable = None, 
                 onPublish: callable = None
                ):
        super().__init__()
        self.MESSAGE = "Hello World"
        self.TOPIC = "test/testing"
        self.messageCount = 0
        
        self._message_callback = onMessageReceived

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
    

    def publish(self, payload: str, topic: str, messageRepeat: int=1):
        """Publish message to desired topic"""
        assert self.isConnected(), "Not connected"
        assert messageRepeat > 0
        assert topic != ""
        
        for i in range(messageRepeat):
            result = self.connection.publish(topic, payload, 1)
            connection_logger.info(f"Publishing message to {topic}")
            connection_logger.debug(f"Message contents: {payload}")
            
            # wait for the message to be published to give debug feedback
            result.wait_for_publish(0.25)
            if result.rc == MQTT_ERR_SUCCESS:
                self._on_publish_success(result)
            else:
                self._on_publish_failure(f"{result} {result.rc}")

   
    def subscribe(self, topic: str):
        assert self.isConnected()
        self.connection.subscribe(topic)
        logger.info(f"Subscribed to {topic}")
        connection_logger.info(f"Subscribed to {topic}")




