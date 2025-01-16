from abc import ABC, abstractmethod
import json
from logging import getLogger

logger = getLogger("BROKER_BASE")
connection_logger = getLogger("MQTT_CONNECTION")

class connectionState:
    DISCONNECTED = 0
    CONNECTED = 1
    CONNECTING = 2

class BrokerBase(ABC):
    def __init__(self):
        self.connectionState = connectionState.DISCONNECTED
        self.messageCount = 0
        self._message_callback = None

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def publish(self, payload: str, topic: str, messageRepeat: int=1) -> None:
        pass
    
    def isConnected(self) -> bool:
        return self.connectionState == connectionState.CONNECTED

    def setMessageCallback(self, callback: callable):
        """Set the callback function for when a message is received\n
        Callback must accept two arguments: topic: str and payload: dict\n
        """
        assert callable(callback), "Callback must be callable"
        assert callback.__code__.co_argcount == 2, "Callback must accept exactly two arguments"
        self._message_callback = callback

    # callbacks
    def _on_connect_success(self, client, userdata, flags, rc): 
        connection_logger.info("*** Connected ***\n")
        self.connectionState = connectionState.CONNECTED

    def _on_connect_close(self, client, userdata, rc): 
        connection_logger.info("*** Connection Closed ***\n")
        self.connectionState = connectionState.DISCONNECTED

    def _on_publish_success(self, result): 
        connection_logger.debug("Publish successful")

    def _on_publish_failure(self, result): 
        connection_logger.error(f"Publish Failed, result: {result}")
    
    def _on_message_received(self, client, userdata, msg): 
        try:
            payloadDecoded = json.loads(msg.payload.decode())
        except Exception as e:
            connection_logger.error(f"Error decoding message: {e}")
            return
        self.messageCount += 1
        connection_logger.info(f"Received message from {msg.topic}")
        connection_logger.debug(f"Message contents: {payloadDecoded}")
        if self._message_callback:
            self._message_callback(msg.topic, payloadDecoded)
