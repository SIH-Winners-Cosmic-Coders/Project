import torch
import torchaudio
from transformers import AutoModel

# Paste your copied HF Token here
HF_TOKEN = "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"

print("⏳ Downloading & loading AI4Bharat IndicConformer (~1.2 GB)...")
model = AutoModel.from_pretrained(
    "ai4bharat/indic-conformer-600m-multilingual", 
    trust_remote_code=True,
    token=HF_TOKEN
)
print("✅ Local Bhashini IndicConformer loaded successfully!")

def transcribe_indic(audio_file_path: str, lang_code: str = "hi"):
    """
    Transcribes audio offline with Bhashini Indic accuracy.
    lang_code options: 'or' (Odia), 'hi' (Hindi), 'bn' (Bengali), 'te' (Telugu), 'ta' (Tamil)
    """
    # 1. Load and resample audio to 16kHz
    wav, sr = torchaudio.load(audio_file_path)
    if wav.shape[0] > 1:
        wav = torch.mean(wav, dim=0, keepdim=True)
    if sr != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
        wav = resampler(wav)

    # 2. Run local transcription
    with torch.no_grad():
        transcription = model(wav, lang_code=lang_code)
    
    return transcription

if __name__ == "__main__":
    # Test with dummy/sample audio
    print("ASR model is ready for local inferencing.")