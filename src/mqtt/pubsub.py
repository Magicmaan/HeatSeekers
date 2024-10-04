from paho.mqtt import client as mqtt
from paho.mqtt import enums as mqtt_enums
from enum import Enum
import Templates.testpackages as pkgs
import os   
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json

#https://repost.aws/knowledge-center/iot-core-publish-mqtt-messages-python


class connectionState:
    DISCONNECTED = 0
    CONNECTED = 1
    CONNECTING = 2

class topics:
    
    
    test = "test/testing"

    
class awtBroker:    
    #TODO
    #will take in amazon aws broker and return a connection
    def __init__(self):
        
        self.ENDPOINT = "a1mcw1hchqljw1-ats.iot.eu-north-1.amazonaws.com"
        self.CLIENT_ID = "testDevice"
        
        path = "E:/theob/Documents/PythonProjects/HeatSeekers/aws/env/"
        self.PATH_TO_CERTIFICATE = path+"certificates/certificate.pem.crt"
        self.PATH_TO_PRIVATE_KEY = path+"certificates/private.pem.key"
        self.PATH_TO_AMAZON_ROOT_CA_1 = path+"AmazonRootCA1.pem"
        
        self.MESSAGE = "Hello World"
        self.TOPIC = "test/testing"
        self.RANGE = 20
        self.packetGenerator = pkgs.packetGenerator()
        
        self.connection = None
        self.connectionState = connectionState.DISCONNECTED
        
        self.connect()
    
    def connect(self):
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
        
        #make connection
        self.connection = mqtt_connection_builder.mtls_from_path(
            endpoint=           self.ENDPOINT,
            cert_filepath=      self.PATH_TO_CERTIFICATE,
            pri_key_filepath=   self.PATH_TO_PRIVATE_KEY,
            client_bootstrap=   client_bootstrap,
            ca_filepath=        self.PATH_TO_AMAZON_ROOT_CA_1,
            client_id=          self.CLIENT_ID,
            clean_session=      False,
            keep_alive_secs=    6
        )
        
        #callbacks
        self.connection._on_connection_success_cb = self._on_connect_success
        self.connection._on_connection_closed_cb = self._on_connect_close
        self.connection._on_connection_interrupted_cb = self._on_connect_interrupted
        self.connection._on_connection_resumed_cb = self._on_connect_resumed
        self.connection._on_connection_failure_cb = self._on_connect_failure
        
        
        print(f'Connecting to {self.ENDPOINT} with client ID {self.CLIENT_ID}...')  
        # Make the connect() call
        connect_future = self.connection.connect()
        # needed to make the connection, idk why
        connect_future.result(float(20))
        
        self.connectionState = connectionState.CONNECTED
        return
    
    def disconnect(self) -> None:
        disconnect_future = self.connection.disconnect()
        disconnect_future.result(float(1))
    
    def isConnected(self) -> bool:
        if self.connection and self.connectionState == connectionState.CONNECTED:
            return True
        return False
    
    def publish(self, message: str, topic: str,messageRepeat: int=1):
        """Takes in message and posts with json format to topic"""
        if not self.isConnected():
            return
        
        #self.logger.info(f"Publishing message: {message} to topic: {topic}")
        
        message = "TEST"        
        topic = "test/testing"
        for i in range (messageRepeat):
            #assemmble message into a json
            data = self.packetGenerator.newTestPacket()
            result = self.connection.publish(topic=      topic, 
                                            payload=     json.dumps(data), 
                                            qos=         mqtt.QoS.AT_LEAST_ONCE)
        
            print("Published: '" + json.dumps(message) + "' to the topic: " + "'test/testing'")
            t.sleep(0.1)
    
    def _on_connect_success(self, connection, callback_data): print("*** Connected ***\n")
    def _on_connect_close(self, connection, callback_data): print("*** Connection Closed ***\n")
    def _on_connect_interrupted(self, connection, callback_data): print("*** Connection interrupted ***\n")
    def _on_connect_resumed(self, connection, callback_data): print("*** Connection Resumed ***\n")
    def _on_connect_failure(self, connection, callback_data): print("*** Connection Failed ***\n")
if __name__ == "__main__":
    broker = awtBroker()
    broker.publish("Hello World", "test/testing")
    broker.disconnect()
    print("done")
    
    