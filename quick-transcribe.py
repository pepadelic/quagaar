#!/usr/bin/env python3  
import json  
import wave  
import subprocess  
import os  
from vosk import Model, KaldiRecognizer  

# Path to the model  
model_path = os.path.expanduser("~/.local/share/vosk/model-small-en")  

# Create temporary directories if they don't exist  
temp_dir = "/tmp"  
audio_file = os.path.join(temp_dir, "recording.wav")  

# Notify recording start  
subprocess.run(["notify-send", "Recording will start in 3 seconds..."])  
subprocess.run(["sleep", "3"])  
subprocess.run(["notify-send", "Recording... Speak now (Press Ctrl+C to stop)"])  

# Record audio  
subprocess.run([  
    "rec",  
    "-r", "16000",  
    "-c", "1",  
    audio_file,  
    "silence", "1", "0.1", "1%", "1", "2.0", "1%"  
])  

# Load model and process audio  
model = Model(model_path)  
wf = wave.open(audio_file, "rb")  
rec = KaldiRecognizer(model, 16000)  

text = ""  
while True:  
    data = wf.readframes(4000)  
    if len(data) == 0:  
        break  
    if rec.AcceptWaveform(data):  
        result = json.loads(rec.Result())  
        text += result.get("text", "") + " "  

final_result = json.loads(rec.FinalResult())  
text += final_result.get("text", "")  

# Copy to clipboard and paste  
subprocess.run(["echo", text.strip()], stdout=subprocess.PIPE)  
subprocess.run(["xclip", "-selection", "clipboard"], input=text.strip().encode())  
subprocess.run(["xdotool", "key", "ctrl+v"])  

# Cleanup  
os.remove(audio_file)  
