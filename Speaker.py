import pyttsx3
import tempfile
import soundfile as sf
import sounddevice as sd

def speak_text(text, samplerate=16000):
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)  # Speed in words per minute

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tf:
        temp_filename = tf.name
    engine.save_to_file(text, temp_filename)
    engine.runAndWait()

    # Load and play via sounddevice
    audio_data, fs = sf.read(temp_filename, dtype='float32')
    print("Speaking:", text)
    sd.play(audio_data, fs)
    sd.wait()