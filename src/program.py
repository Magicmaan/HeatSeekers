from paho.mqtt import client as mqtt
from paho.mqtt import enums as mqtt_enums
from math import random

def _connect_callback(client: mqtt.Client, userdata, flags: dict, rc: int):
    match rc:
        case mqtt_enums.ConnackCode.CONNACK_ACCEPTED.value:
            print("Connection accepted")
            
        case mqtt_enums.ConnackCode.CONNACK_REFUSED_BAD_USERNAME_PASSWORD.value:
            print("Connection refused: bad username or password")
        
        
        case mqtt_enums.ConnackCode.CONNACK_REFUSED_PROTOCOL_VERSION.value:
            print("Connection refused: unacceptable protocol version")
        case mqtt_enums.ConnackCode.CONNACK_REFUSED_IDENTIFIER_REJECTED.value:
            print("Connection refused: identifier rejected")
        case mqtt_enums.ConnackCode.CONNACK_REFUSED_SERVER_UNAVAILABLE.value:
            print("Connection refused: server unavailable")
        case mqtt_enums.ConnackCode.CONNACK_REFUSED_NOT_AUTHORIZED.value:
            print("Connection refused: not authorized")
            

class Program:
    def __init__(self):
        #TODO move to file
        broker = 'broker.emqx.io'
        port = 1883
        topic = 'test'
        #random client ID
        
        
        
        self.client = self.connectMQTT(broker, port)
        self.run()
    
    
        
    def run(self):
        self.client.loop_forever()
    
    def connectMQTT(self, hostname:str, port) -> mqtt.Client:
        #random client ID
        clientID = f'python-mqtt-{random.randint(0, 1000)}'
        
        client = mqtt.Client(clientID)
        client.on_connect = _connect_callback
        client.connect(hostname, port)

        return client
    
    def subscribe(self, client: mqtt.Client, topic: str):
        #TODO
        return
    
    