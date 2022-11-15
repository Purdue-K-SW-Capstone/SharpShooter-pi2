import struct
import pyaudio as pa
import wave
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from os import listdir, rename
# import librosa
# import librosa.display


class Audio:
    
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pa.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = 2
        self.WAVE_FILE_PATH = "/home/shooter/input.wav"
        
        self.audio = pa.PyAudio()
        
        self.total_data = bytearray()

    def openStream(self):
        
        # open the audio data stream
        self.stream = self.audio.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        output=True,
                        frames_per_buffer=self.CHUNK)
        
    # while statement that read audio in real time
    def readAudio(self):
        # read a CHUNK from stream
        data = self.stream.read(self.CHUNK, exception_on_overflow = False)

        # to get the pre-receive sound
        self.total_data += data
        if len(self.total_data) > 122880:
            self.total_data = bytearray()
        
        # convert to list
        dataInt = struct.unpack(str(self.CHUNK) + 'h', data)
        npData = np.abs(dataInt)
        list_data = list(npData)

        # When there's a loud noise, start recording
        if list_data[-1] > 10000:
            print("Start to record the audio")
        
            largest = []
        
            frames = self.total_data
            print(len(frames))
            for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                data = self.stream.read(self.CHUNK)
                frames += data
                
                tempData = struct.unpack(str(self.CHUNK) + 'h', data)
                tempNpData = np.abs(tempData)
                tempListData = list(tempNpData)
                largest = largest + tempListData

            largest.sort(reverse=True)
            print("max amplitude : " + str(largest[0]))
            
            print("Recording is finished.")
            # self.stream.stop_stream()
            # self.stream.close()
            
            # save code
            wf = wave.open(self.WAVE_FILE_PATH, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(frames)
            wf.close()
            
            return frames