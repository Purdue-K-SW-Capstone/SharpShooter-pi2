from node_21_main import LoRa

import asyncio
import websockets
import json

async def accept(lora):
    async with websockets.connect("ws://127.0.0.1:5000") as websocket:
        
        while True:
            
            package = lora.transmit()
            
            if package != None:
                # package = json.dumps(package)
                await websocket.send(package)

def main():
    
    print("open the LoRa")
    lora = LoRa()
    
    asyncio.run(accept(lora))
    
    

async def acceptTest(lora):
    async with websockets.connect("ws://127.0.0.1:5000") as websocket:
        
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
    main()
    # mainTest()