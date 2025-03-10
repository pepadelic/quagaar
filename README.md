# QUAGAAR - QUick Audio to text with Gnome Automated Accessible Recording 🎤
<img src="quagaar.webp" alt="QUAGAAR" width="300">  

<table>  
  <tr>  
    <td>  
      <img src="quagaar.webp" alt="QUAGAAR" width="150">  
    </td>  
    <td>  
      <h1>QUAGAAR - QUick Audio to text with Gnome Automated Accessible Recording 🎤</h1>  
    </td>  
  </tr>  
</table>  

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://opensource.org/licenses/Apache-2.0)  
[![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey)](https://www.linux.org/)

A simple voice-to-text tool that lets you transcribe speech to text with a single keyboard shortcut. The transcribed text is automatically pasted wherever your cursor is located.

## Features

- 🎯 Single keyboard shortcut activation
- 🔒 Privacy-focused (no cloud services, works offline)
- ⚡ Fast transcription
- 📝 Paste transcribed text directly from clipboard with Ctrl+V
- 🧹 Automatic cleanup of temporary files

## Prerequisites

- Linux (Fedora/etc.)
- Python 3.6 or higher
- GNOME Desktop Environment (for easy shortcut setup)

## Installation

1. Install system dependencies:
```bash
sudo dnf install python3-pip sox xclip xdotool
```

2. Install Vosk through pip:
```bash
pip install vosk
```

3. Download and set up the Vosk model:
```bash
mkdir -p ~/.local/share/vosk
cd ~/.local/share/vosk
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 model-small-en
```

4. Create the script directory and save the transcription script:
```bash
mkdir -p ~/bin
```

Create `~/bin/quick-transcribe.py` with the following content:

```python
#!/usr/bin/env python3
import json
import wave
import subprocess
import os
import atexit
import signal
from vosk import Model, KaldiRecognizer

# Path for temporary audio file
temp_dir = "/tmp"
audio_file = os.path.join(temp_dir, "recording.wav")

# Ensure cleanup happens in all cases
def cleanup(file_path):
    try:
        if os.path.exists(file_path):
            # Overwrite with zeros before deletion for secure removal
            with open(file_path, 'wb') as f:
                f.write(b'\x00' * os.path.getsize(file_path))
            os.remove(file_path)
    except Exception:
        pass

# Register cleanup for normal exit and signals
atexit.register(lambda: cleanup(audio_file))
signal.signal(signal.SIGINT, lambda s, f: cleanup(audio_file))
signal.signal(signal.SIGTERM, lambda s, f: cleanup(audio_file))

try:
    model_path = os.path.expanduser("~/.local/share/vosk/model-small-en")

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
    wf.close()

    # Copy to clipboard and paste
    subprocess.run(["echo", text.strip()], stdout=subprocess.PIPE)
    subprocess.run(["xclip", "-selection", "clipboard"], input=text.strip().encode())
    subprocess.run(["xdotool", "key", "ctrl+v"])

finally:
    # Ensure cleanup happens even if an error occurs
    cleanup(audio_file)
```

5. Make the script executable:
```bash
chmod +x ~/bin/quick-transcribe.py
```

## Setting Up the Keyboard Shortcut

1. Open GNOME Settings
2. Navigate to Keyboard Shortcuts
3. Click the + at the bottom
4. Add a new custom shortcut:
   - Name: Quick Transcribe
   - Command: `/home/YOUR_USERNAME/bin/quick-transcribe.py`
   - Shortcut: Choose something like Ctrl+Alt+R

## Usage

1. Place your cursor where you want the transcribed text to appear
2. Press your configured keyboard shortcut (e.g., Ctrl+Alt+R)
3. Wait for the "Recording will start in 3 seconds..." notification
4. Speak clearly after the "Recording..." notification appears
5. Stop speaking for 2 seconds to automatically end recording
6. The transcribed text will automatically appear at your cursor location

## Privacy & Security

- All processing is done locally on your machine
- No audio data is sent to external servers
- Temporary audio files are:
  - Created in `/tmp/recording.wav`
  - Securely overwritten before deletion
  - Automatically cleaned up, even if the script crashes
  - Only exist during the recording and transcription process

## License

This project is licensed under the Apache 2 - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
