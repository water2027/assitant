from pathlib import Path
import time
import pygame
import azure.cognitiveservices.speech as speechsdk
from tools import *

with open('config.json','r',encoding="utf-8") as f:
    config = json.load(f)
with open('tools.json','r',encoding="utf-8") as f:
    tools = json.load(f)
openai.api_key = config["api_key"]
openai.base_url = config["base_url"]
edge_key=config["edge_key"]

class Tool:
    def __init__(self):
        self.message=[{
            "role": "system",
            "content": config["system"]
        }]

    def get_response(self,text:str):
        self.message.append({"role": "user", "content": text})
        wow=self.sendtoAI().choices[0].message
        
        if(wow.content):
            self.message.append({"role": wow.role, "content": wow.content})
            return wow.content
        else:
            self.message.append({"role": wow.role, "content": str(wow.tool_calls[0].function)})
            faq=self.tool_call(wow)
            return faq
    
    def addmessage(self,msg,text):
        self.message.append({
            "role": "function",
            "tool_call_id":msg.tool_calls[0].id,
            "name":msg.tool_calls[0].function.name,
            "content": text
        })

    def sendtoAI(self):
        response = openai.chat.completions.create(
            model=config["model"],
            messages=self.message,
            tools=tools,
            tool_choice="auto",
            max_tokens=config["max_tokens"],
            temperature=config["temperature"],
        )
        return response

    def stt(self):
        audio_file_path = Path(__file__).parent/ "uohw" / "speech.wav"
        with open(audio_file_path, "rb") as audio_file:
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcription.text
    
    def tts(self,text):
        pygame.init()
        pygame.mixer.init()
        speech_file_path = Path(__file__).parent/"hvfu" / "speech.wav"
        response = openai.audio.speech.create(
            model="tts-1-hd-1106",
            voice="alloy",
            input=text
        )
        response.stream_to_file(speech_file_path)
        time.sleep(1)
        print("File exists:", speech_file_path.exists())  # 检查文件存在
        if speech_file_path.exists():
            print(str(speech_file_path))
        music=pygame.mixer.Sound(str(speech_file_path))
        music.play()
        play_time = music.get_length()  
        time.sleep(play_time)  

    def edge_stt(self):
        speech_config = speechsdk.SpeechConfig(subscription=edge_key, region="southeastasia")
        speech_config.speech_recognition_language="zh-CN"

        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        print("Speak into your microphone.")
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(speech_recognition_result.text))
            return speech_recognition_result.text
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
            return ""
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
            return ""
        
    def edge_tts(self,text):
        speech_config = speechsdk.SpeechConfig(subscription=edge_key, region="southeastasia")
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

        speech_config.speech_synthesis_voice_name='en-US-JennyMultilingualNeural'
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")

    def tool_call(self,msg):
        if msg.tool_calls[0].function.name == "get_current_weather":
            arguments_str = msg.tool_calls[0].function.arguments  # 这是一个字符串
            arguments_dict = json.loads(arguments_str)  # 将字符串转换为字典
            text = str(get_current_weather(arguments_dict['location']))  # 现在可以这样访问
        
        elif msg.tool_calls[0].function.name == "code_interpreter":
            arguments_str = msg.tool_calls[0].function.arguments
            arguments_dict = json.loads(arguments_str)  # 将字符串转换为字典
            text = code_interpreter((arguments_dict['code']))  # 现在可以这样访问
        
        elif msg.tool_calls[0].function.name == "get_image":
            arguments_str = msg.tool_calls[0].function.arguments
            arguments_dict = json.loads(arguments_str)
            url = arguments_dict['image_url']
            wahaha = arguments_dict['msg']
            text = get_image(url,wahaha)
        
        elif msg.tool_calls[0].function.name == "get_file":
            arguments_str = msg.tool_calls[0].function.arguments
            arguments_dict = json.loads(arguments_str)
            file_url = arguments_dict['file_url']
            text = get_file(file_url)
        
        self.addmessage(msg,text)
        wow=self.sendtoAI().choices[0].message
        self.message.append({"role": wow.role, "content": wow.content})
        print(self.message)
        return wow