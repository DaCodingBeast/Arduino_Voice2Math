import requests
import time
from transcript import Transcriptor
from MathLibary import MathProcessor
import re
from Speaker import speak_text
import time
ARDUINO_URL = "http://172.20.10.5"
oldText = ""
import math

def truncate_to_hundredths(n):
    return math.trunc(n * 100) / 100

def readMessages():
     global oldText
     text =  response.text.strip()
     if text != oldText:
            print("Arduino responds:", text)
            oldText = text
            time.sleep(7)
            speak_text("The Arduino says it got the number " + str(truncate_to_hundredths(float(text))))
     oldText = text

     print("text")
     
     



def sendMessage(text):
    
    send_url = f"{ARDUINO_URL}/send?msg={text}"
    send_response = requests.get(send_url, timeout=3)
    if send_response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Message send failed with status {send_response.status_code}")

transcriber = Transcriptor()
processor = MathProcessor()
RequestTranscription = False



while True:
    try:
        response = requests.get(ARDUINO_URL, timeout=3)

        try: 
            float(response.text.strip())
            readMessages()
        except: 
            pass
        
        if response.status_code == 200 and transcriber.Completion == True and RequestTranscription == True:
            RequestTranscription = False
            math_problem = transcriber.transcribe_audio_array(audio)
            ans = processor.process_and_check(math_problem)

            finalMessage = "Solved the problem: " + math_problem + "     Answer Was:  " + ans

            sendMessage(re.findall(r'\S+',finalMessage))
            
            while True:
                try:
                    float(response.text.strip())  # Try to parse to float
                    break  # Exit the loop if successful
                except:
                    response = requests.get(ARDUINO_URL, timeout=3)
                    readMessages()  # Keep reading messages even on error
                    time.sleep(.2)   # Optional: wait before retrying


        elif RequestTranscription == False and input("Start Recording: ") == "Yes":
            RequestTranscription = True
            audio = transcriber.record_audio()
        else:
            print(f"Connected but got status code: {response.status_code}")

        
        
    except requests.exceptions.RequestException as e:
        print(f"Connection failed: {e}")

    time.sleep(.1)  # wait before next request