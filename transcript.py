import whisper
import sounddevice as sd
import numpy as np

class Transcriptor:
    Completion = False

    def __init__(self, model_size="small"):
        print("Loading Whisper model...")
        self.model = whisper.load_model(model_size)

    def record_audio(self, duration=None, samplerate=16000):
        Transcriptor.Completion = False
        print("Recording... Press Enter to stop manually or wait for duration.")

        recording = []

        def callback(indata, frames, time, status):
            if status:
                print(status)
            recording.append(indata.copy())

        stream = sd.InputStream(channels=1, samplerate=samplerate, callback=callback)
        stream.start()

        if duration:
            sd.sleep(int(duration * 1000))
        else:
            input("Press Enter to stop recording...\n")

        stream.stop()
        stream.close()

        audio_np = np.concatenate(recording, axis=0).flatten()
        Transcriptor.Completion = True
        return audio_np

    def transcribe_audio_array(self, audio_array, samplerate=16000):
        print("Transcribing")
        result = self.model.transcribe(audio_array, fp16=False, language="en", task="transcribe")
        return result["text"]
