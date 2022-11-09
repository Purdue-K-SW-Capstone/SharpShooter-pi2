from lora.node_21_main import LoRa

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
            
            # Sound detect
            # bytearray type
            sound = audio.readAudio()

            if sound != None:
                soundModel.processing()
                result = soundModel.execute()
                print("{'sound': " + str(result) + "}")
                
                if result == 1:
                    lora.sendType({"sound": 1})
            
            # This code is for Image transmission test
            # imageBytes = lora.getImage()
            # print("imageBytes")
            # print(imageBytes)
            # if imageBytes != None:
            #     imageNp = np.fromstring(imageBytes, np.uint8)
            #     print(imageNp)
            #     imgArr = cv2.imdecode(imageNp, cv2.IMREAD_COLOR)
            #     print("imgArr")
            #     print(imgArr)
            #     cv2.imwrite('../../test.jpg', imgArr)
                # await websocket.send(imageBytes)
            
            # Receive Packet
            packet = lora.getPacket()
                
            if packet.get("start") == 1:
                print(packet)
                lora.sendType({"start": 1})

                imageBytes = bytearray()
            
                # while True:
                #     imageBytes += lora.getImage()
                
                #     if imageBytes is end:
                #         break;
                # await websocket.send(imageBytes)
                
            if packet.get("time") != None:
                print(packet)
                data = json.dumps(packet)
                await websocket.send(data)
            
            # isSoundDic = {"sound": 1}
            # isStartDic = {"start": 1}

            # time.sleep(2)
            # lora.sendType(isSoundDic)


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

    
        