from node_21_main import LoRa
from dotenv import load_dotenv

import os
import json
import time
import struct

import asyncio
import websockets

load_dotenv('/home/shooter/PycharmProjects/receiver/lora/.env')
WS_URL = os.environ.get("WS_URL")

async def accept(lora):
    async with websockets.connect(WS_URL) as websocket:
        
        while True:
            
            package = lora.transmit()
            
            if package != None:
                # package = json.dumps(package)
                await websocket.send(package)

def main():
    
    print("open the LoRa")
    lora = LoRa()
    
    asyncio.run(accept(lora))

async def acceptImage(lora):
    async with websockets.connect(WS_URL) as websocket:
    
        i = 0
        imageBytes = bytearray()
    
        noneCount = 0
    
        while noneCount <= 40:
            
            packet = lora.transmitBytes()
            
            if packet != None:
                
                noneCount = 0
                            
                preTime = (struct.unpack('>f', packet[:4]))[0]
                
                print(preTime)
                                
                curTime = round(time.time(), 3) - 1640000000
                                        
                span = curTime - preTime
                print("span : " + str(span))
                
                span = struct.pack('>f', span)
                
                imageBytes = imageBytes + packet[4:]
                
                print(packet[4:])
                await websocket.send(span)
                await websocket.send(packet)
                print(i)
                i+=1
            
            # test code
            
            if packet == None:
                time.sleep(0.5)
                # print(noneCount)
                noneCount+=1



def mainImage():
    
    print("open the LoRa")
    lora = LoRa()
    
    asyncio.run(acceptImage(lora))
    

async def acceptTest(lora):
    async with websockets.connect(WS_URL) as websocket:
        
        while True:
            
            package = lora.transmitTest()
            
            if package != None:
                package = json.dumps(package)
                await websocket.send(package)

def mainTest():
    
    lora = LoRa()    
    
    asyncio.run(acceptTest(lora))
    # while True:
        
        # package is dictionary(json)
        # package = lora.transmit()
            
                
        # if package != None:
        #     package = json.dumps(package)
        #     asyncio.run(accept(package))

        



if __name__ == "__main__":
    
    # while True:
    # 계속 receive_coordinate 상태이다가.
    
    # 만약 tablet에서 start버튼을 누른다면
    # receive_imageByte함수를 실행시킨다.
    
    
    # main()
    # mainImage()
    # mainTest()