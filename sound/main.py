import pyaudio
import wave

# CHUNK는 음성 데이터를 불러올 때, 한 번에 몇 개의 정수를
# 한 번 불러올 때다 1024개의 정수를 불러온다
# 
# RATE는 음성 데이터의 샘플링 레이트이다.
# 높을수록 음질이 좋아진다.

# format 매개변수에는 비트 깊이를 설정한다. 
# 여기서는 pyaudio.paInt16이므로 비트 깊이가 16비트가 된다.

# RECORD_SECONDS
# 레코드의 시간

# WAVE_OUTPUT_FILENAME
# 결과 파일의 파일명과 확장자.




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

# 초당 44100 비트의 속도로 5.0 초 동안 녹음 할 것으로 보이지만 
# 1024 비트 청크로 할 것이다. 
# 따라서 for 루프는 0에서 int(44100 / 1024 * 5.0), 
# 즉 0에서 214까지 계산한다.(5초 바로 아래에 있는 range(215) 포함)
# 그런 다음 1024 크기의 청크로 사운드를 읽고 추가

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
# 스트림과 pyaudio 닫아줌

stream.stop_stream()
stream.close()
p.terminate()

#wave.open, wb -> 쓰기 전용 파일로 읽기
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
# setnchannels 채널수 설정하기
wf.setnchannels(CHANNELS)
# setsampwidth -> 샘플 너비를 n바이트로 설정
wf.setsampwidth(p.get_sample_size(FORMAT))
#프레임 수를 n으로 설정
wf.setframerate(RATE)
#오디오 프레임을 작성하고 올바른지 확인하는 작업
wf.writeframes(b''.join(frames))
#wave write 객체 닫음
wf.close()