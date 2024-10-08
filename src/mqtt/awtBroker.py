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


#https://repost.aws/knowledge-center/iot-core-publish-mqtt-messages-python
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

class connectionState:
    DISCONNECTED = 0
    CONNECTED = 1
    CONNECTING = 2

class topics:
    TEST = "test/testing"


    
class awtBroker:   
    #TODO
    #will take in amazon aws broker and return a connection
    def __init__(self):
        #DO NOT CHANGE
        path = f"{DATA_PATH}/mqtt/certs"
        self.PATH_TO_HOST = f"{DATA_PATH}/mqtt/host.txt"
        self.PATH_TO_CERTIFICATE = f"{path}certificate.pem.crt"
        self.PATH_TO_PRIVATE_KEY = f"{path}private.pem.key"
        self.PATH_TO_AMAZON_ROOT_CA_1 = path+"ROOTCA1.pem"
        
        self.MESSAGE = "Hello World"
        self.TOPIC = "test/testing"
        
        self.messageCount = 0
        self.receivedMessageEvent = threading.Event()
        
        self.connection = None
        self.connectionState = connectionState.DISCONNECTED
        
        #connection settings
        #contains the host name, and certificates for IOT connection
        self.connectArgs = awtConnection(self.PATH_TO_HOST, 
                                         self.PATH_TO_CERTIFICATE, 
                                         self.PATH_TO_PRIVATE_KEY, 
                                         self.PATH_TO_AMAZON_ROOT_CA_1, 
                                         )
        
        self.connect()
        
        self.subscribe(self.TOPIC)
    
    def connect(self, connectArgs:awtConnection=None):
        if not connectArgs:
            if not self.connectArgs:
                return
            connectArgs = self.connectArgs
        
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
        print(f'Connecting to {kwargs["endpoint"]} with client ID {kwargs["client_id"]}...')  
        
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
        self.connectArgs = connectArgs
    
    def publish(self, message: str, topic: str,messageRepeat: int=1):
        """Publish message to desired topic"""
        assert self.isConnected()
            
        topic = topics.TEST
        data = newTestPacket()
        for i in range (messageRepeat):
            #assemmble message into a json
            result = self.connection.publish(topic=      topic, 
                                            payload=     json.dumps(data), 
                                            qos=         mqtt.QoS.AT_LEAST_ONCE)
            print("Published: '" + json.dumps(message) + "' to the topic: " + "'test/testing'")
            t.sleep(0.1)
    
    def subscribe(self, topic: str):
        assert self.isConnected()
        
        self.connection.subscribe(topic=topic, 
                                  qos=mqtt.QoS.AT_LEAST_ONCE, 
                                  callback=self._on_message_received)
        pass
    
    def await_message(self,messageAmount:int=1):
        messageAmount += self.messageCount
        while self.messageCount != messageAmount and not self.receivedMessageEvent.is_set():
            print("Waiting for message")
            self.receivedMessageEvent.wait()
    #callbacks
    def _on_connect_success(self, connection, callback_data): print("*** Connected ***\n"); self.connectionState = connectionState.CONNECTED
    def _on_connect_close(self, connection, callback_data): print("*** Connection Closed ***\n"); self.connectionState = connectionState.DISCONNECTED
    def _on_connect_interrupted(self, connection, error): print("*** Connection interrupted ***\n"); print(f"Error: {error}\n")
    def _on_connect_resumed(self, connection, return_code, session_present): print("*** Connection Resumed ***\n")
    def _on_connect_failure(self, connection, callback_data): print("*** Connection Failed ***\n")
    def _on_publish_success(self, connection, callback_data): 
        print("*** Publish Succeeded ***\n")
    def _on_publish_failure(self, connection, callback_data): 
        print("*** Publish Failed ***\n")
    
    def _on_message_received(self, topic, payload, dup, qos, retain, **kwargs): 
        self.messageCount += 1
        print(f"Message received: {payload.decode()}")
        print(f"Topic: {topic}")
        #self.receivedMessageEvent.set()
    
if __name__ == "__main__":
    broker = awtBroker()
    broker.publish("Hello World", "test/testing")
    
    broker.await_message(10)
    print("done")
    
