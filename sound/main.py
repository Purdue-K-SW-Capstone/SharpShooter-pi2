import pyaudio
import wave

# CHUNK는 음성 데이터를 불러올 때, 한 번에 몇 개의 정수를
# 한 번 불러올 때다 1024개의 정수를 불러온다
# 
# RATE는 음성 데이터의 샘플링 레이트이다.
# 높을수록 음질이 좋아진다.
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

# 음성 데이터 스트림을 여는 코드
# format : 비트 깊이 설정
# rate : 샘플링 레이트
# input : 입력 스트림인지 아닌지 설정하는 매개 변수
# frame_per_buffer : chunk크기
# input_device_index : 원하는 입력 장치의 번호. 입력 하지 않으면 자동으로 세팅해준다.
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Start to record the audio.")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    # 음성 데이터를 문자열로 반환
    # data is bytes type
    # frames is list type
    data = stream.read(CHUNK)
    print(type(data))
    # print("data : " +str(data))
    
    frames.append(data)
    print(type(frames))
    # print("frames : " +str(frames))

print("Recording is finished.")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()