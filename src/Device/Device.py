from mqtt import awtBroker

class Device:
    def __init__(self):
        
        self.identifier:str = None
        self.data:dict = {
            "temperature": [],
            "humidity": [],
        }
        
        
        
        self.connection:awtBroker = None
    

    def getTemperature(self) -> list:
        return self.data["temperature"]
    
    def getHumidity(self) -> list:
        return self.data["humidity"]
    
    
    