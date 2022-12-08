from lora.lora import LoRa

from sound.audio import Audio
from sound.model import SoundModel

from dotenv import load_dotenv

import os
import json
import time
import struct

import asyncio
import websockets

import cv2
import numpy as np
from PIL import Image
import io

load_dotenv('/home/shooter/PycharmProjects/receiver/lora/.env')
WS_URL = os.environ.get("WS_URL")

async def main():
    async with websockets.connect(WS_URL) as websocket:
        audio = Audio()
        audio.openStream()
        print("Audio is opened")
        
        lora = LoRa()
        print("LoRa is opened")
        
        soundModel = SoundModel()
        soundModel.setup()
        print("model setting is completed")
        
        while True:
            
            while True:
                data = await websocket.recv()
                
                if data != None:
                    value = json.loads(data)
                    
                    if value.get("start") == 1:
                        lora.sendType({"start": 1})
                                                
                        imageBytes, width, height = lora.getImage()
                        
                        print(f"width : {width}")
                        print(f"height : {height}")
                        
                        img = {"img": list(imageBytes)}
                        size = {"size": [width, height]}
                        
                        package = json.dumps(img)
                        package2 = json.dumps(size)
                        
                        await websocket.send(package)
                        await websocket.send(package2)

                        break

            while True:
                # Sound detect
                # bytearray type
                sound = audio.readAudio()
                # print(123)
                # data = await websocket.recv()
                # try:
                #     if data != None:
                #         print("data : " + str(data))
                #         value = json.loads(data)
                        
                #         if value.get("finish") == 1:
                #             break
                # except:
                #     pass

                if sound != None:
                    soundModel.processing()
                    result = soundModel.execute()
                    print("{'sound': " + str(result) + "}")

                    if result == 1:
                        lora.sendType({"sound": 1})
                
                # Receive Packet
                packet = lora.getPacket()
                
                # when get coordinate, send coordinate to tablet.
                if packet.get("coordinate") != None:
                    print(packet)
                    data = json.dumps(packet)
                    await websocket.send(data)
        
        
    # open the LoRa
    lora = LoRa()
    print("LoRa is opened")

    lora.getImage()

def test():
    lora = LoRa()
    print("LoRa is opened")
    lora.getImage()

if __name__ == "__main__":
    asyncio.run(main())
    # test()