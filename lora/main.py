from node_21_main import LoRa
from dotenv import load_dotenv

import os
import json

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
    
        while True:
            
            package = lora.transmitBytes()
            
            if package != None:
                imageBytes = imageBytes + package
                
                print(imageBytes)
                await websocket.send(package)
                print(i)
                i+=1
                


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
    # main()
    mainImage()
    # mainTest()