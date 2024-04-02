from tool import *
import tkinter as tk
from recorder import *
import threading

class Main:
    def __init__(self):
        self.recorder = Recorder()
        self.tool = Tool()

    def start_recording_and_processing(self):
        self.recorder.toggle_recording()  # 开始或结束录音
        if not self.recorder.is_recording:  # 如果结束录音
            text = self.tool.get_response(self.tool.edge_stt())  # 进行语音识别
            self.tool.edge_tts(text)  # 文本转语音

    def start(self):
        threading.Thread(target=self.start_recording_and_processing).start()

    # def dazi(self):
    #     text = entry.get()
    #     entry.delete(0, tk.END)
    #     wow = self.tool.get_response(text)
    #     # self.tool.tts(wow)
    #     print(wow.content)

    def get_recording(self):
        while(True):
            text = self.tool.edge_stt()
            if "你好" in text:
                print("检测到你好")
                self.active(text)
                return

    def active(self,msg):
        while True:
            text=self.tool.get_response(msg)
            print(text)
            self.tool.tts(text)
            msg=self.tool.edge_stt()
            if "再见" in msg:
                print("再见")
                return
            

main = Main()
main.get_recording()#顺便把这行注释掉
#如果要启用界面UI和打字功能，取消下面的注释和上面函数dazi的注释
# root = tk.Tk()
# root.title("简单的Tkinter应用")
# label = tk.Label(root, text="欢迎来到Tkinter!")
# label.pack()
# entry = tk.Entry(root)
# entry.pack()
# button = tk.Button(root, text="打字", command=main.dazi)
# button.pack()
# button = tk.Button(root, text="录音", command=main.get_recording)
# button.pack()
# root.geometry("600x800")
# root.mainloop()


