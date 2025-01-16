from program import DATA_PATH
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
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


logger = getLogger("AWT_BROKER")
connection_logger = getLogger("MQTT_CONNECTION")
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
    client_id:str = Environment.getIdentifier()

class connectionState:
    DISCONNECTED = 0
    CONNECTED = 1
    CONNECTING = 2



    
class awtBroker(BrokerBase):   
    """Class for AWT Broker connection
    
        If connection settings are provided, will connect on creation\n
        Otherwise, will need to call setConnectionArgs() then connect() to connect
    """
    def __init__(self, connectArgs: awtConnection = None, autoStart: bool = False):
        super().__init__()
        self.connectArgs = connectArgs
        self.MESSAGE = "Hello World"
        self.TOPIC = "test/testing"
        self.connection = None
        
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
    
    def publish(self, payload: str, topic: str, messageRepeat: int=1):
        """Publish message to desired topic"""
        assert self.isConnected(), "Not connected"
        assert messageRepeat > 0
        assert topic != ""
        
        for i in range (messageRepeat):
            #assemmble message into a json
            result = self.connection.publish(topic=      topic, 
                                            payload=     payload, 
                                            qos=         0)
            connection_logger.info(f"Publishing message to {topic}")
            connection_logger.debug(f"Message contents: {payload}")
            result[0].add_done_callback(self._on_publish_success)


    
    def subscribe(self, topic: str):
        assert self.isConnected()
        self.connection.subscribe(topic=topic, 
                                  qos=mqtt.QoS.AT_LEAST_ONCE, 
                                  callback=self._on_message_received)
        logger.info(f"Subscribed to {topic}")
        connection_logger.info(f"Subscribed to {topic}")
        pass
    
    def setMessageCallback(self, callback: callable):
        """Set the callback function for when a message is received\n
        Callback must accept two arguments: topic: str and payload: dict\n
        """
        assert callable(callback), "Callback must be callable"
        assert callback.__code__.co_argcount == 2, "Callback must accept exactly two arguments"
        self._message_callback = callback
    
    #callbacks
    def _on_connect_success(self, connection, callback_data): connection_logger.info("*** Connected ***\n"); logger.info("*** Connected ***\n"); self.connectionState = connectionState.CONNECTED
    def _on_connect_close(self, connection, callback_data): connection_logger.info("*** Connection Closed ***\n"); self.connectionState = connectionState.DISCONNECTED
    def _on_connect_interrupted(self, connection, error): connection_logger.error("*** Connection interrupted ***\n"); print(f"Error: {error}\n")
    def _on_connect_resumed(self, connection, return_code, session_present): connection_logger.info("*** Connection Resumed ***\n")
    def _on_connect_failure(self, connection:mqtt.Connection, callback_data): 
        logger.error("*** Connection Failed ***\n")
        logger.error(connection.host_name)
    def _on_publish_success(self, future):
        try:
            future.result()
            connection_logger.debug("Publish successful")
        except Exception as e:
            pass
    def _on_publish_failure(self, connection, callback_data): 
        logger.error(f"Publish failed: {connection.host_name}")
        connection_logger.error(f"Publish failed: {connection.host_name}")
    
    
    def _on_message_received(self, topic, payload:str, dup, qos, retain, **kwargs): 
        #I'm not sure why it has to be done twice, but it does trust me..
        payloadDecoded = json.loads(payload)
        #check if message is from self
        
        self.messageCount += 1
        connection_logger.info(f"Received message from {topic}")
        connection_logger.debug(f"Message contents: {payloadDecoded}")
        if self._message_callback:
            self._message_callback(topic, payloadDecoded)




