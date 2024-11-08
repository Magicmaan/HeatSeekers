from program import DATA_PATH
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
from .Templates import *
from dataclasses import asdict, dataclass
import os   
import time as t
import json
import random
import threading
from logging import DEBUG
from program.Logger import getLogger


logger = getLogger("AWT_BROKER")
#https://repost.aws/knowledge-center/iot-core-publish-mqtt-messages-python
@dataclass
class awtConnection:
    """
    Class for AWT connection settings
    
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

class connectionState:
    DISCONNECTED = 0
    CONNECTED = 1
    CONNECTING = 2



    
class awtBroker:   
    """Class for AWT Broker connection
    
        If connection settings are provided, will connect on creation\n
        Otherwise, will need to call setConnectionArgs() then connect() to connect
    """
    #TODO
    #will take in amazon aws broker and return a connection
    def __init__(self, connectArgs:awtConnection=None, autoStart:bool=False):
        self.connectArgs = None
        if connectArgs:
            self.connectArgs = connectArgs
        
        self.MESSAGE = "Hello World"
        self.TOPIC = "test/testing"
        
        
        self.messageCount = 0
        #setup threading event for when message is received
        self.receivedMessageEvent = threading.Event()
        self._message_callback = None
        self.connection = None
        self.connectionState = connectionState.DISCONNECTED
        
        if self.connectArgs and autoStart:
                self.connect()

    
    def connect(self) -> None:
        """Connect to AWS broker\n
        Uses the connection settings provided to object"""
        assert not self.isConnected(), "Already connected"
        assert self.connectArgs, "No connection args provided"
        
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
        
        #unpack connection settings
        kwargs = asdict(self.connectArgs)
        
        kwargs["client_bootstrap"] = client_bootstrap
        kwargs["clean_session"] = False
        kwargs["keep_alive_secs"] = 600
        
        #make connection
        self.connection = mqtt_connection_builder.mtls_from_path(**kwargs)
        logger.info(f'Connecting to {kwargs["endpoint"]} with client ID {kwargs["client_id"]}...')
        
        #callbacks
        self.connection._on_connection_success_cb = self._on_connect_success
        self.connection._on_connection_closed_cb = self._on_connect_close
        self.connection._on_connection_interrupted_cb = self._on_connect_interrupted
        self.connection._on_connection_resumed_cb = self._on_connect_resumed
        self.connection._on_connection_failure_cb = self._on_connect_failure
        
        # Make the connect() call
        connect_future = self.connection.connect()
        # needed to make the connection, idk why
        connect_future.result(float(20))
        
        self.connectionState = connectionState.CONNECTED
    
    def disconnect(self) -> None:
        disconnect_future = self.connection.disconnect()
        disconnect_future.result(float(1))
        
        self.connectionState = connectionState.DISCONNECTED
    
    def isConnected(self) -> bool:
        if self.connection and self.connectionState == connectionState.CONNECTED:
            return True
        return False
    
    def getConnection(self) -> mqtt.Connection:
        return self.connection
    
    def getConnectionArgs(self) -> awtConnection:
        return self.connectArgs
    
    def setConnectionArgs(self, connectArgs:awtConnection):
        assert not self.isConnected(), "Cannot change connection settings while connected"
        self.connectArgs = connectArgs
    
    def publish(self, message: str, topic: str, type:str="SENSOR_DATA",messageRepeat: int=1):
        """Publish message to desired topic"""
        assert self.isConnected(), "Not connected"
        assert messageRepeat > 0
        assert topic != ""
        data = None
        
        if type == "SENSOR_DATA":
            data = newSensorPacket(random.uniform(0,100), random.uniform(0,100))
        elif type == "MESSAGE":
            data = newPacket(message)
        else:
            data = newTestPacket()
        
        
        for i in range (messageRepeat):
            #assemmble message into a json
            result = self.connection.publish(topic=      topic, 
                                            payload=     json.dumps(data), 
                                            qos=         mqtt.QoS.AT_LEAST_ONCE,)
            logger.info(f"Publishing message to {topic}")
            logger.debug(f"Message contents: {data}")
            result[0].add_done_callback(self._on_publish_success)
    
    def subscribe(self, topic: str):
        assert self.isConnected()
        self.connection.subscribe(topic=topic, 
                                  qos=mqtt.QoS.AT_LEAST_ONCE, 
                                  callback=self._on_message_received)
        logger.info(f"Subscribed to {topic}")
        pass
    
    def setMessageCallback(self, callback):
        self._message_callback = callback
    
    def await_message(self,messageAmount:int=1):
        assert self.isConnected(), "Not connected"
        messageAmount += self.messageCount
        while self.messageCount != messageAmount or not self.receivedMessageEvent.is_set():
            self.receivedMessageEvent.wait(1)
            self.receivedMessageEvent.clear()
    #callbacks
    def _on_connect_success(self, connection, callback_data): logger.info("*** Connected ***\n"); self.connectionState = connectionState.CONNECTED
    def _on_connect_close(self, connection, callback_data): logger.info("*** Connection Closed ***\n"); self.connectionState = connectionState.DISCONNECTED
    def _on_connect_interrupted(self, connection, error): logger.error("*** Connection interrupted ***\n"); print(f"Error: {error}\n")
    def _on_connect_resumed(self, connection, return_code, session_present): logger.info("*** Connection Resumed ***\n")
    def _on_connect_failure(self, connection:mqtt.Connection, callback_data): 
        logger.error("*** Connection Failed ***\n")
        logger.error(connection.host_name)
        
    def _on_publish_success(self, future):
        try:
            future.result()
            logger.debug("Publish successful")
            
        except Exception as e:
            pass
    
    def _on_publish_failure(self, connection, callback_data): 
        logger.error(f"Publish failed: {connection.host_name}")
    
    def _on_message_received(self, topic, payload, dup, qos, retain, **kwargs): 
        self.messageCount += 1
        logger.info(f"Received message from {topic}")
        logger.debug(f"Message contents: {payload.decode()}")
        if self._message_callback:
            self._message_callback(topic, payload)
        
        self.receivedMessageEvent.set()
        
    
    
