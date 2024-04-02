import sounddevice as sd
from scipy.io.wavfile import write
from pathlib import Path
import time
from tool import *
# 全局变量用于跟踪录音状态
# 录音参数
# 考虑每三秒录音一次，如果监测到关键词，则进入激活状态
fs = 44100  
speech_file_path = Path(__file__).parent/"uohw" / "speech.wav"
is_recording = False
recording = []
tool = Tool()
class Recorder:
    def __init__(self, fs=44100, channels=2, dtype='int16'):
        self.fs = fs
        self.channels = channels
        self.dtype = dtype
        self.is_recording = False
        self.recording = None
        self.start_time = None

    def toggle_recording(self):
        if not self.is_recording:
            # 开始录音
            self.is_recording = True
            self.start_time = time.time()
            print("开始录音")
        else:
            # 结束录音，并保存
            self.is_recording = False
            duration = time.time() - self.start_time
            print("结束录音")
            self.recording = sd.rec(int(duration * self.fs), samplerate=self.fs, channels=self.channels, dtype=self.dtype)
            sd.wait()  # 等待录音完成
            write(str(speech_file_path), self.fs, self.recording)
            print("录音已保存")
            self.recording = None


                