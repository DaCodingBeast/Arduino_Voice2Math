from openai import completions
import whisper
import os
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

class Transcriptor:

    Completion = False
    def __init__(self):
        
        self.model = whisper.load_model("small")

    def record_audio(self, filename = "r.wav", samplerate=16000):
        self.audiopath = filename

        print("Recording... Press Enter to stop.")
        recording = []
        is_recording = True

        def callback(indata, frames, time, status):
            if status:
                print(status)
            recording.append(indata.copy())

        # recording
        stream = sd.InputStream(channels=1, samplerate=samplerate, callback=callback)
        stream.start()

        input()
        stream.stop()
        stream.close()

        audio_np = np.concatenate(recording, axis=0)

        write(filename, samplerate, (audio_np * 32767).astype(np.int16))

        Transcriptor.Completion = True

        print(f"Recording saved to {filename}")
        
    def transcribe(self):
        Transcriptor.Completion = False
        return self.model.transcribe(self.audiopath)["text"]
    

