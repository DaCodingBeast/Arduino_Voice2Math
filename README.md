# 📢 Voice to Math – AI Mathematical Solver  
**Created using Python and C++ | 2024–2025**

## 🎯 Project Goal  
Speak a math problem into your computer’s microphone and have the solution wirelessly displayed on an Arduino-powered LCD.

## 🛠️ How It Works  
1. **Voice Input**  
   - The computer listens for a spoken math problem using its microphone.

2. **Speech Recognition**  
   - Audio is transcribed to text using OpenAI’s [Whisper](https://github.com/openai/whisper) model.

3. **Math Solving**  
   - The text is parsed and solved using Python's symbolic math library, [SymPy](https://www.sympy.org/).

4. **Wireless Communication**  
   - The solution is sent via an HTTP POST request to an Arduino running a lightweight HTTP server over Wi-Fi.

5. **Result Display**  
   - The Arduino receives the solution and displays it on a connected **LCD screen** (Liquid Crystal Display).

## 🔌 Technologies Used  
- Python  
- C++ (Arduino IDE)  
- OpenAI Whisper (ASR)  
- SymPy  
- Arduino with Wi-Fi (ESP8266/ESP32 recommended)  
- LCD Module (16x2 or similar)

## 🔐 Networking Insights  
While building this system, special care was taken to navigate and understand the networking constraints imposed by school firewalls and network security protocols.

## 📚 What I Learned  
- End-to-end pipeline for audio-based AI applications  
- RESTful communication between Python and Arduino  
- Real-time audio transcription and symbolic math solving  
- Practical networking and firewall troubleshooting
