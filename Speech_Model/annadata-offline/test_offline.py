import requests
import json
import io
import wave
import numpy as np

# 1. Generate a mock 2-second WAV audio file in memory
sample_rate = 16000
duration = 2.0
t = np.linspace(0, duration, int(sample_rate * duration), False)
# 440 Hz tone as audio dummy
audio_data = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)

wav_io = io.BytesIO()
with wave.open(wav_io, 'wb') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(audio_data.tobytes())

wav_io.seek(0)

# 2. Send the simulated query to the local offline endpoint
url = "http://127.0.0.1:8000/api/v1/voice/hybrid-consult?lang=od"
files = {
    'file': ('test_farmer_query.wav', wav_io, 'audio/wav')
}

print("🌾 Sending query to local AnnaDATA Offline Engine...")
response = requests.post(url, files=files)

print(f"\n[Status Code]: {response.status_code}")
print("[Response JSON]:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))