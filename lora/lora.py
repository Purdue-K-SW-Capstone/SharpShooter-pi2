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
        
    # get first image with width and height from pi1
    def getImage(self):
        
        imageBytes, width, height = self.node.receiveImage()
        
        return [imageBytes, width, height]
    
    # send packet to inform that user clicks start button and sound is detected to pi1
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

    # get packet from pi1
    def getPacket(self):
        
        processed = self.node.receivePacket()
        
        if processed != None:
            result = json.loads(processed)
            
            return result
        
        return {}
        