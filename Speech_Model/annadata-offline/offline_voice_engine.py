import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import shutil
import tempfile
import traceback
import asyncio
import soundfile as sf
import numpy as np
import torch
import torchaudio
import ollama
from transformers import AutoModel, pipeline
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

app = FastAPI(title="AnnaDATA Indic Voice Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
asr_model = None
whisper_pipeline = None
device = "cuda" if torch.cuda.is_available() else "cpu"
OLLAMA_MODEL = "qwen2.5:3b"

LANG_CONFIG = {
    "od": {"name": "Odia (ଓଡ଼ିଆ)", "asr_code": "or", "tts_code": "or"},
    "hi": {"name": "Hindi (हिन्दी)", "asr_code": "hi", "tts_code": "hi"},
    "bn": {"name": "Bengali (বাংলা)", "asr_code": "bn", "tts_code": "bn"},
    "te": {"name": "Telugu (తెలుగు)", "asr_code": "te", "tts_code": "te"},
    "ta": {"name": "Tamil (தமிழ்)", "asr_code": "ta", "tts_code": "ta"},
    "en": {"name": "English", "asr_code": "en", "tts_code": "en"}
}

def get_whisper_pipeline():
    """Lazily load Whisper model for English."""
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
    """Offline local transcription using Whisper (No FFmpeg)."""
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
    """Lazily load the model on first call to prevent server startup hangs."""
    global asr_model
    if asr_model is None:
        print("\n⏳ Loading AI4Bharat IndicConformer from disk cache...")
        asr_model = AutoModel.from_pretrained(
            "ai4bharat/indic-conformer-600m-multilingual",
            trust_remote_code=True,
            local_files_only=True
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

def generate_natural_speech_sync(text: str, lang_code: str, output_path: str):
    """Generates natural regional Indian voice."""
    if not HAS_GTTS:
        raise RuntimeError("gTTS not installed")
    target_info = LANG_CONFIG.get(lang_code, LANG_CONFIG["od"])
    tts = gTTS(text=text, lang=target_info["tts_code"], tld="co.in", slow=False)
    tts.save(output_path)

# ----------------------------------------------------
# Routes
# ----------------------------------------------------
@app.post("/api/v1/voice/hybrid-consult")
async def hybrid_voice_consult(
    file: UploadFile = File(...),
    lang: str = Query("od", description="Language code: od, hi, bn, te, ta, en")
):
    temp_audio_path = None
    target_info = LANG_CONFIG.get(lang, LANG_CONFIG["od"])
    
    try:
        suffix = os.path.splitext(file.filename)[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_audio_path = tmp.name

        print(f"\n🎙️ [ASR] Transcribing offline in {target_info['name']}...")
        
        # Run ASR in a non-blocking thread
        if lang == "en":
            farmer_transcript = await asyncio.to_thread(
                transcribe_local_english, temp_audio_path
            )
        else:
            farmer_transcript = await asyncio.to_thread(
                transcribe_local_indic, temp_audio_path, target_info["asr_code"]
            )

        if not farmer_transcript:
            farmer_transcript = "ଧାନ ଫସଲରେ କେମିତି ଉପଜାଉ କରିବା"

        print(f"✅ Transcribed Query: \"{farmer_transcript}\"")

        lang_name = target_info["name"]
        print(f"🧠 [LLM Step 1] Reasoning agronomy advisory in English...")

        # Step 1: Expert Agronomy Reasoning (High-precision English generation)
        agronomy_prompt = f"""You are AnnaDATA's expert agricultural scientist.
The farmer is dealing with this problem: "{farmer_transcript}"

Provide a structured, practical 4-line advisory.
Format:
Line 1: Direct diagnosis of the crop issue, deficiency, or pest cause.
Line 2: Organic treatment with specific low-cost remedy and exact dosage.
Line 3: Chemical treatment with specific medicine/fertilizer and exact dosage (e.g. Urea 25kg/acre, Chlorpyrifos 2ml/L, or DAP).
Line 4: Irrigation, weeding, or soil management practice.

Rules:
- Write strictly in simple, clear English.
- Keep each line to 1 short, actionable sentence.
- Do not use markdown bolding (**) or bullet numbers."""

        def run_english_reasoning():
            return ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": agronomy_prompt}],
                options={
                    "temperature": 0.2,
                    "num_predict": 130,
                    "top_p": 0.9
                }
            )

        english_res = await asyncio.wait_for(asyncio.to_thread(run_english_reasoning), timeout=180.0)
        english_advisory = english_res["message"]["content"].strip()
        print(f"📋 English Advisory Generated:\n{english_advisory}\n")

        # Step 2: High-Quality Regional Translation (If language is not English)
        if lang != "en":
            print(f"🌐 [LLM Step 2] Translating advisory into natural {lang_name}...")
            
            translation_prompt = f"""You are a professional agricultural translator.
Translate this 4-line farming advisory directly into natural, fluent {lang_name} script for a rural farmer:

{english_advisory}

Rules:
- Translate strictly into {lang_name} script.
- Keep the technical dosages intact and accurately written.
- Output ONLY the translated 4 lines without explanations, markdown bolding, or introductions."""

            def run_regional_translation():
                return ollama.chat(
                    model=OLLAMA_MODEL,
                    messages=[{"role": "user", "content": translation_prompt}],
                    options={
                        "temperature": 0.1,
                        "num_predict": 160,
                        "top_p": 0.9
                    }
                )

            translation_res = await asyncio.wait_for(asyncio.to_thread(run_regional_translation), timeout=180.0)
            advisory_regional = translation_res["message"]["content"].strip()
        else:
            advisory_regional = english_advisory

        print(f"✅ Final Regional Advisory:\n{advisory_regional}\n")

        # Audio synthesis with fast fallback
        audio_filename = f"advisory_{lang}_{os.getpid()}.mp3"
        audio_save_path = os.path.join(tempfile.gettempdir(), audio_filename)
        has_audio = False

        try:
            print(f"🔊 Synthesizing speech in {lang_name}...")
            await asyncio.wait_for(
                asyncio.to_thread(generate_natural_speech_sync, advisory_regional, lang, audio_save_path),
                timeout=20.0
            )
            has_audio = os.path.exists(audio_save_path) and os.path.getsize(audio_save_path) > 0
        except Exception:
            has_audio = False

        return {
            "status": "success",
            "mode": "100% Local IndicConformer + Ollama",
            "farmer_query": farmer_transcript,
            "advisory_regional": advisory_regional,
            "language": lang_name,
            "audio_file": audio_filename if has_audio else None
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Engine Error: {str(e)}")
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except OSError:
                pass

@app.get("/api/v1/voice/audio-stream")
async def get_audio_stream(file: str = Query(...)):
    audio_path = os.path.join(tempfile.gettempdir(), file)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(audio_path, media_type="audio/mpeg")

# ----------------------------------------------------
# Responsive Web UI
# ----------------------------------------------------
HTML_UI = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AnnaDATA — IndicConformer Edge AI</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    .recording-pulse { animation: pulse 1.5s infinite; }
    @keyframes pulse {
      0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
      50% { transform: scale(1.05); box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); }
    }
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen flex flex-col items-center justify-center p-4 font-sans">

  <div class="w-full max-w-2xl bg-slate-800 border border-slate-700 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6">
    
    <div class="flex items-center justify-between border-b border-slate-700 pb-4">
      <div>
        <h1 class="text-2xl font-bold text-emerald-400 flex items-center gap-2">
          🌾 AnnaDATA Edge
        </h1>
        <p class="text-xs text-slate-400">Offline Bhashini IndicConformer + Ollama Qwen 2.5</p>
      </div>
      <div class="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1.5 rounded-full">
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
        <span class="text-xs font-semibold text-emerald-400">Indic Engine Ready</span>
      </div>
    </div>

    <div class="flex items-center justify-between bg-slate-900/60 p-3 rounded-2xl border border-slate-700">
      <label for="langSelect" class="text-sm font-medium text-slate-300">Farmer's Dialect / Language:</label>
      <select id="langSelect" class="bg-slate-800 text-slate-200 text-sm border border-slate-600 rounded-xl px-3 py-1.5 focus:outline-none focus:border-emerald-500">
        <option value="od" selected>Odia (ଓଡ଼ିଆ)</option>
        <option value="hi">Hindi (हिन्दी)</option>
        <option value="bn">Bengali (বাংলা)</option>
        <option value="te">Telugu (తెలుగు)</option>
        <option value="ta">Tamil (தமிழ்)</option>
        <option value="en">English</option>
      </select>
    </div>

    <div id="statusBox" class="text-center py-2 text-sm text-slate-400">
      Tap the mic button and speak in your selected dialect
    </div>

    <div class="flex flex-col items-center justify-center py-4">
      <button id="recordBtn" class="w-24 h-24 rounded-full bg-emerald-500 hover:bg-emerald-600 active:scale-95 transition flex items-center justify-center shadow-lg shadow-emerald-500/30 cursor-pointer">
        <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 003-3V5a3 3 0 10-6 0v6a3 3 0 003 3z" />
        </svg>
      </button>
      <span id="btnLabel" class="text-xs font-semibold text-slate-400 mt-3 uppercase tracking-wider">Tap to Speak</span>
    </div>

    <div class="space-y-4">
      <div class="bg-slate-900/80 rounded-2xl p-4 border border-slate-700/80">
        <div class="flex justify-between items-center mb-1">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Farmer Said (IndicConformer ASR):</span>
        </div>
        <p id="transcriptionText" class="text-slate-200 text-sm italic min-h-[1.5rem]">Awaiting audio...</p>
      </div>

      <div class="bg-emerald-950/30 border border-emerald-500/30 rounded-2xl p-5 shadow-inner">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-bold text-emerald-400 uppercase tracking-wide">AI Agronomy Advisory:</span>
          <button id="replayVoiceBtn" class="hidden text-xs bg-emerald-600 hover:bg-emerald-500 text-white px-2.5 py-1 rounded-lg transition flex items-center gap-1">
            🔊 Replay
          </button>
        </div>
        <p id="advisoryText" class="text-slate-100 text-base leading-relaxed">
          The regional agronomy advisory will appear here.
        </p>
      </div>
    </div>

  </div>

  <script>
    const recordBtn = document.getElementById('recordBtn');
    const btnLabel = document.getElementById('btnLabel');
    const statusBox = document.getElementById('statusBox');
    const transcriptionText = document.getElementById('transcriptionText');
    const advisoryText = document.getElementById('advisoryText');
    const langSelect = document.getElementById('langSelect');
    const replayVoiceBtn = document.getElementById('replayVoiceBtn');

    let audioContext, mediaStream, inputNode, processorNode;
    let audioData = [];
    let isRecording = false, latestAdvisory = "";
    let currentAudio = new Audio();

    recordBtn.addEventListener('click', async () => {
      if (!isRecording) startRecording();
      else stopRecording();
    });

    async function startRecording() {
      try {
        if (currentAudio) { currentAudio.pause(); currentAudio.currentTime = 0; }
        audioData = [];
        audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        inputNode = audioContext.createMediaStreamSource(mediaStream);

        processorNode = audioContext.createScriptProcessor(4096, 1, 1);
        processorNode.onaudioprocess = (e) => {
          if (!isRecording) return;
          const channelData = e.inputBuffer.getChannelData(0);
          audioData.push(new Float32Array(channelData));
        };

        inputNode.connect(processorNode);
        processorNode.connect(audioContext.destination);

        isRecording = true;
        recordBtn.classList.replace('bg-emerald-500', 'bg-red-500');
        recordBtn.classList.add('recording-pulse');
        btnLabel.innerText = "Recording... Tap to Stop";
        statusBox.innerText = "Listening to farmer...";
        statusBox.classList.add('text-red-400');
      } catch (err) {
        alert("Microphone access error: " + err);
      }
    }

    async function stopRecording() {
      isRecording = false;
      if (processorNode) processorNode.disconnect();
      if (inputNode) inputNode.disconnect();
      if (mediaStream) mediaStream.getTracks().forEach(t => t.stop());

      recordBtn.classList.replace('bg-red-500', 'bg-emerald-500');
      recordBtn.classList.remove('recording-pulse');
      btnLabel.innerText = "Tap to Speak";
      statusBox.innerText = "Processing ASR & Reasoning...";
      statusBox.classList.remove('text-red-400');

      const wavBlob = encodeWAV(audioData, 16000);
      await sendAudioToServer(wavBlob);
    }

    function encodeWAV(samplesArrays, sampleRate) {
      let totalLength = samplesArrays.reduce((acc, curr) => acc + curr.length, 0);
      let samples = new Float32Array(totalLength);
      let offset = 0;
      for (let arr of samplesArrays) {
        samples.set(arr, offset);
        offset += arr.length;
      }

      let buffer = new ArrayBuffer(44 + samples.length * 2);
      let view = new DataView(buffer);

      function writeString(view, offset, string) {
        for (let i = 0; i < string.length; i++) view.setUint8(offset + i, string.charCodeAt(i));
      }

      writeString(view, 0, 'RIFF');
      view.setUint32(4, 36 + samples.length * 2, true);
      writeString(view, 8, 'WAVE');
      writeString(view, 12, 'fmt ');
      view.setUint32(16, 16, true);
      view.setUint16(20, 1, true); 
      view.setUint16(22, 1, true); 
      view.setUint32(24, sampleRate, true);
      view.setUint32(28, sampleRate * 2, true);
      view.setUint16(32, 2, true);
      view.setUint16(34, 16, true);
      writeString(view, 36, 'data');
      view.setUint32(40, samples.length * 2, true);

      let index = 44;
      for (let i = 0; i < samples.length; i++) {
        let s = Math.max(-1, Math.min(1, samples[i]));
        view.setInt16(index, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        index += 2;
      }

      return new Blob([view], { type: 'audio/wav' });
    }

    async function sendAudioToServer(wavBlob) {
      const formData = new FormData();
      formData.append('file', wavBlob, 'farmer_voice.wav');
      const lang = langSelect.value;

      try {
        const res = await fetch(`/api/v1/voice/hybrid-consult?lang=${lang}`, { method: 'POST', body: formData });
        const data = await res.json();
        
        if (data.status === 'success') {
          transcriptionText.innerText = `"${data.farmer_query}"`;
          advisoryText.innerText = data.advisory_regional;
          latestAdvisory = data.advisory_regional;
          statusBox.innerText = "Advisory ready!";

          if (data.audio_file) {
            currentAudio.src = `/api/v1/voice/audio-stream?file=${encodeURIComponent(data.audio_file)}&t=${Date.now()}`;
            currentAudio.play().catch(() => speakFallback(data.advisory_regional, lang));
          } else {
            speakFallback(data.advisory_regional, lang);
          }

          replayVoiceBtn.classList.remove('hidden');
        } else {
          statusBox.innerText = "Failed: " + (data.detail || "Unknown error");
        }
      } catch (e) {
        statusBox.innerText = "Connection error: " + e.message;
      }
    }

    function speakFallback(text, lang) {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(text);
        const map = { "hi": "hi-IN", "od": "hi-IN", "bn": "bn-IN", "te": "te-IN", "ta": "ta-IN", "en": "en-IN" };
        utter.lang = map[lang] || "hi-IN";
        utter.rate = 0.95;
        window.speechSynthesis.speak(utter);
      }
    }

    replayVoiceBtn.addEventListener('click', () => {
      if (currentAudio && currentAudio.src && !currentAudio.paused) {
        currentAudio.currentTime = 0;
        currentAudio.play();
      } else if (latestAdvisory) {
        speakFallback(latestAdvisory, langSelect.value);
      }
    });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    return HTMLResponse(content=HTML_UI)

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "asr_engine": "AI4Bharat IndicConformer", "ollama_model": OLLAMA_MODEL}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)