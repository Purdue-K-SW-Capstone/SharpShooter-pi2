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

# async def accept(lora):
#     async with websockets.connect(WS_URL) as websocket:
        
#         while True:
            
#             package = lora.transmit()
            
#             if package != None:
#                 # package = json.dumps(package)
#                 await websocket.send(package)

# def main():
    
#     print("open the LoRa")
#     lora = LoRa()
    
#     asyncio.run(accept(lora))

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
    

async def accept(lora):
    async with websockets.connect(WS_URL) as websocket:
        
        while True:
            
            package = lora.receiveCoordinate()
            
            if package != None:
                package = json.dumps(package)
                await websocket.send(package)

async def main():
    async with websockets.connect(WS_URL) as websocket:
        
        lora = LoRa()
        
        while True:
            coordinate = lora.getPacket()
            
            isSoundDic = {"sound": 1}
            isStartDic = {"start": 1}

            time.sleep(5)
            lora.sendType(isSoundDic)


if __name__ == "__main__":
    
    # lora = LoRa()
    asyncio.run(main())
    # while True:
        # at ordinary times, They always ready to get the coordinate
        # asyncio.run(accept(lora))
        # asyncio.run(main(lora))
        
        # 1. sound value send ({sound: True})
        # 2. start button value send ({start: True})
        
        # if sound sensor detect the gun shot
        # sendSoundValue()
        
        # if tablet click the start button.
        # capture the target image and send that to tablet.
        # but get only odd number of packet.
        # asyncio.run(acceptImage(lora))

    
        