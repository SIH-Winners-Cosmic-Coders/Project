import os
import tempfile
import torch
import torchaudio
import soundfile as sf
import numpy as np
from transformers import AutoModel, pipeline

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

device = "cuda" if torch.cuda.is_available() else "cpu"

asr_model = None
whisper_pipeline = None

# If you have the model folder downloaded to a specific path, you can put the absolute path here,
# or leave it as "ai4bharat/indic-conformer-600m-multilingual" with local_files_only=True
INDIC_MODEL_PATH = "ai4bharat/indic-conformer-600m-multilingual"

def get_whisper_pipeline():
    """Lazily loads Whisper model for English speech recognition."""
    global whisper_pipeline
    if whisper_pipeline is None:
        print("\n⏳ Loading Whisper Tiny (English)...")
        whisper_pipeline = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny.en",
            device=device
        )
        print("✅ Whisper Ready!\n")
    return whisper_pipeline

def transcribe_local_english(audio_path: str) -> str:
    """Offline local transcription using Whisper."""
    data, sr = sf.read(audio_path)
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
    
    if sr != 16000:
        wav = torch.tensor(data, dtype=torch.float32).unsqueeze(0)
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
        data = resampler(wav).squeeze(0).numpy()
        
    pipe = get_whisper_pipeline()
    result = pipe({"array": data, "sampling_rate": 16000})
    return result["text"].strip()

def get_asr_model():
    """Lazily load the IndicConformer model from local cache on disk."""
    global asr_model
    if asr_model is None:
        print("\n⏳ Loading local AI4Bharat IndicConformer from disk...")
        try:
            asr_model = AutoModel.from_pretrained(
                INDIC_MODEL_PATH,
                trust_remote_code=True,
                local_files_only=True
            )
        except Exception:
            print("⚠️ Local cache check failed. Loading with local_files_only=False fallback...")
            asr_model = AutoModel.from_pretrained(
                INDIC_MODEL_PATH,
                trust_remote_code=True,
                local_files_only=False
            )
        print("✅ IndicConformer Ready!\n")
    return asr_model

def transcribe_local_indic(audio_path: str, lang_code: str = "or") -> str:
    """Offline local transcription using AI4Bharat IndicConformer."""
    model = get_asr_model()
    
    data, sr = sf.read(audio_path)
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
        
    wav = torch.tensor(data, dtype=torch.float32).unsqueeze(0)
    
    TARGET_SR = 16000
    if sr != TARGET_SR:
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=TARGET_SR)
        wav = resampler(wav)

    with torch.no_grad():
        transcript = model(wav, lang_code, "ctc")
    
    if isinstance(transcript, list) and len(transcript) > 0:
        return transcript[0].strip()
    return str(transcript).strip()

def generate_natural_speech_sync(text: str, tts_code: str, output_path: str):
    """Generates localized TTS audio file."""
    if not HAS_GTTS:
        raise RuntimeError("gTTS is not installed. Install with `pip install gTTS`.")
    tts = gTTS(text=text, lang=tts_code, tld="co.in", slow=False)
    tts.save(output_path)