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

import numpy as np
from PIL import Image
import io

# put pi2's ip address and port at here
# ex) "ws://ipaddress:port" -> "ws://127.0.0.1:3000"
WS_URL = "ws://10.42.0.1:3030"

async def main():
    # connect with web(tablet) using websocket
    async with websockets.connect(WS_URL) as websocket:
        
        audio = Audio()
        # Audio open
        audio.openStream()
        print("Audio is opened")
        
        # LoRa open
        lora = LoRa()
        print("LoRa is opened")
        
        # Model setup
        soundModel = SoundModel()
        soundModel.setup()
        print("model setting is completed")
        
        while True:
            
            while True:
                # wait for receiving data using websocket
                data = await websocket.recv()
                
                # if data exists
                if data != None:
                    # change json to dictionary
                    value = json.loads(data)
                    
                    # if user clicks start button on web
                    if value.get("start") == 1:
                        # send {start : 1} to pi1
                        lora.sendType({"start": 1})
                        
                        # get first image from pi1
                        imageBytes, width, height = lora.getImage()
                        
                        print(f"width : {width}")
                        print(f"height : {height}")
                        
                        img = {"img": list(imageBytes)}
                        size = {"size": [width, height]}
                        
                        # change dictionary to json
                        package = json.dumps(img)
                        package2 = json.dumps(size)
                        
                        await websocket.send(package)
                        await websocket.send(package2)

                        break

            while True:
                # Sound detect
                # bytearray type
                sound = audio.readAudio()
                
                # if sound is detected
                if sound != None:
                    # process the sound
                    soundModel.processing()
                    result = soundModel.execute()
                    print("{'sound': " + str(result) + "}")
                    
                    # if sound is gun sound
                    if result == 1:
                        # send {sound: 1} to pi1
                        lora.sendType({"sound": 1})
                
                # Receive Packet
                packet = lora.getPacket()
                
                # when get coordinate, send coordinate to tablet.
                if packet.get("coordinate") != None:
                    print(packet)
                    data = json.dumps(packet)
                    await websocket.send(data)

if __name__ == "__main__":
    # use asyncio function for asynchronization
    asyncio.run(main())