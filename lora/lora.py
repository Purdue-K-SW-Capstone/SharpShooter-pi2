from lora.hslr import HSLR
import json
import time

class LoRa:
    
    def __init__(self):
        
        self.SERIAL_NUMBER = "/dev/ttyS0"
        self.FREQUENCY = 915
        self.ADDRESS = 21
        self.POWER = 22
        self.RSSI = True
        
        self.SEND_TO_WHO = 100
        
        self.node = HSLR(serial_num=self.SERIAL_NUMBER, freq=self.FREQUENCY, addr=self.ADDRESS, power=self.POWER, rssi=self.RSSI)
        
    def sendImage(self):
        imageBytes = bytearray()
        imageBytes += b'\x01\x02\x03\x04\x05'
        
        print(imageBytes)
        
        # node setting
        self.node.addr_temp = self.node.ADDRESS
        self.node.set(self.node.FREQUENCY, self.SEND_TO_WHO, self.node.POWER, self.node.RSSI)
                
        # send the imageBytes
        self.node.transmitImage(imageBytes)
        
        self.node.set(self.node.FREQUENCY, self.node.addr_temp, self.node.POWER, self.node.RSSI)
        
        time.sleep(0.5)
        
    def getImage(self):
        
        imageBytes, width, height = self.node.receiveImage()
        
        return [imageBytes, width, height]
    
    def sendType(self, typeDic):
        # node setting 
        self.node.addr_temp = self.node.ADDRESS
        self.node.set(self.node.FREQUENCY, self.SEND_TO_WHO, self.node.POWER, self.node.RSSI)
        
        # change dictionary to json
        payload = json.dumps(typeDic)
        print("payload : " + str(payload))
        
        # send the payload
        self.node.transmitType(payload)
        
        self.node.set(self.node.FREQUENCY, self.node.addr_temp, self.node.POWER, self.node.RSSI)
        
        time.sleep(0.5)

    def getPacket(self):
        
        processed = self.node.receivePacket()
        
        if processed != None:
            result = json.loads(processed)
            
            return result
        
        return {}
        