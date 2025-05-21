import requests
import time
from transcript import Transcriptor

ARDUINO_URL = "http://172.20.10.5"
oldText = ""


def readMessages(text):
     global oldText
     if text.strip() != oldText:
            print("Arduino says:", response.text.strip())
            oldText = response.text.strip()
            return oldText


def sendMessage(text):
    # Limit to 16 chars
    if(len(text) > 16):
        print("Too long of a Message")
        return
    
    send_url = f"{ARDUINO_URL}/send?msg={text}"
    send_response = requests.get(send_url, timeout=3)
    if send_response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Message send failed with status {send_response.status_code}")

transcriber = Transcriptor()
RequestInput = False
while True:
    try:
        response = requests.get(ARDUINO_URL, timeout=3)
        
        if response.status_code == 200 and transcriber.Completion == True:
            sendMessage(transcriber.transcribe())
            RequestInput = False
        elif RequestInput == False and input("Start Recording: ") == "Yes":
            RequestInput = True
            transcriber.record_audio()
        else:
            print(f"Connected but got status code: {response.status_code}")
        
    except requests.exceptions.RequestException as e:
        print(f"Connection failed: {e}")

    time.sleep(.1)  # wait before next request