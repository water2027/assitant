import requests
import subprocess
import openai
import json
import base64
from docx import Document

with open('config.json','r',encoding="utf-8") as f:
    config = json.load(f)
openai.api_key = config["api_key"]
openai.base_url = config["base_url"]
url="https://api.vvhan.com/api/weather"

def get_current_weather(location:str):
    x = requests.get(url + "?city=" + location)
    data = x.json()
    return str(data)

def code_interpreter(code:str):
    code = code
    filename = "example.py"
    with open(filename, 'w') as file:
        file.write(code)
    result = subprocess.run(['python', filename], capture_output=True, text=True)
    if result.stderr:
        return result.stderr
    return result.stdout

def get_image(url:str,msg:str):
    base64_image=encode_image(url)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
        {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": msg
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
                }
            ]
            }
        ],
        "max_tokens": 300
    }
    response = requests.post("https://api1.zhtec.xyz/v1/chat/completions", headers=headers, json=payload)
    wow=response.json()['choices'][0]['message']['content']
    return str(wow)

def encode_image(image_path:str):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_file(file_path:str):
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    elif file_path.endswith('.docx'):
        document = Document(file_path)
        return str("\n".join([paragraph.text for paragraph in document.paragraphs]))
    else:
        return "Unsupported file format"