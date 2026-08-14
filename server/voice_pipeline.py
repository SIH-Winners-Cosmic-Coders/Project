import os
import base64
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

load_dotenv()
app = FastAPI()

# Configure Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in your .env file.")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

SUPPORTED_LANGUAGES = {
    # Odia variations
    "od": "od-IN", "or": "od-IN", "odia": "od-IN", "or-in": "od-IN", "od-in": "od-IN",
    # Hindi variations
    "hi": "hi-IN", "hindi": "hi-IN", "hi-in": "hi-IN",
    # Bengali variations
    "bn": "bn-IN", "bengali": "bn-IN", "bn-in": "bn-IN",
    # Telugu variations
    "te": "te-IN", "telugu": "te-IN", "te-in": "te-IN",
    # Tamil variations
    "ta": "ta-IN", "tamil": "ta-IN", "ta-in": "ta-IN",
    # Marathi variations
    "mr": "mr-IN", "marathi": "mr-IN", "mr-in": "mr-IN",
}

def resolve_language_code(target_lang: str, default_fallback: str = "od-IN") -> str:
    """Normalizes input language strings and applies fallback if unrecognized."""
    clean_code = target_lang.strip().lower()
    return SUPPORTED_LANGUAGES.get(clean_code, default_fallback)

# ==========================================
# New Audio Streaming Endpoint (Moved Outside)
# ==========================================
@app.get("/api/v1/voice/listen-advisory")
async def listen_advisory():
    """Directly streams the latest generated advisory WAV file."""
    audio_path = "digital_twin_response.wav"
    if os.path.exists(audio_path):
        return FileResponse(audio_path, media_type="audio/wav")
    raise HTTPException(status_code=404, detail="No advisory audio generated yet.")

@app.post("/api/v1/voice/master-consult")
async def master_farm_consult(file: UploadFile = File(...), target_lang: str = "od-IN"):
    """
    The Ultimate Farm Digital Twin Voice Pipeline.
    Hears the farmer -> Analyzes with AI -> Translates -> Speaks back.
    """
    sarvam_key = os.getenv("SARVAM_API_KEY")
    if not sarvam_key:
        raise HTTPException(status_code=500, detail="SARVAM_API_KEY missing in .env")
    
    # Base headers for all Sarvam API calls
    sarvam_headers = {"api-subscription-key": sarvam_key}

    # Normalize language with safe fallback
    active_lang = resolve_language_code(target_lang, default_fallback="od-IN")

    # ==========================================
    # STEP 1: Speech-to-Text (Hear the Farmer)
    # ==========================================
    audio_bytes = await file.read()
    stt_files = {'file': (file.filename, audio_bytes, file.content_type)}
    stt_data = {'language_code': active_lang}
    
    stt_res = requests.post(
        "https://api.sarvam.ai/speech-to-text", 
        headers=sarvam_headers, 
        files=stt_files, 
        data=stt_data
    )
    if stt_res.status_code != 200:
        raise HTTPException(status_code=502, detail=f"STT Error: {stt_res.text}")
    
    farmer_transcript = stt_res.json().get("transcript", "").strip()

    # Safety Guard: Check if the audio was silent or unclear
    if not farmer_transcript:
        raise HTTPException(
            status_code=400, 
            detail="Could not detect speech in the audio clip. Please try speaking clearly."
        )

    # ==========================================
    # STEP 2: Dual AI Agronomy Engine (Gemini -> Sarvam Fallback)
    # ==========================================
    prompt = f"""
    You are an expert Agronomy AI working in India. 
    A farmer just asked this question (transcribed from regional audio):
    "{farmer_transcript}"
    
    Provide a brief, actionable 2-sentence solution in simple English. 
    Keep it conversational, empathetic, and natural. Do not use markdown or bold formatting.
    """
    
    engine_used = "Google Gemini"
    try:
        gemini_response = gemini_model.generate_content(prompt)
        english_advisory = gemini_response.text.strip()
        print("🧠 [AI Engine]: Processed successfully via Google Gemini")
        
    except (ResourceExhausted, Exception) as e:
        engine_used = "Sarvam AI (Fallback)"
        print("⚠️ [Quota 429]: Gemini limit reached. Seamlessly switching to Sarvam AI...")
        
        chat_url = "https://api.sarvam.ai/v1/chat/completions"
        chat_payload = {
            "model": "sarvam-105b-conversations",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert Agronomy AI working in India. Provide a brief, actionable 2-sentence solution in simple English. Keep it conversational and natural. Do not use markdown."
                },
                {
                    "role": "user",
                    "content": f"A farmer asked: {farmer_transcript}"
                }
            ]
        }
        
        chat_res = requests.post(
            chat_url, 
            headers={**sarvam_headers, "Content-Type": "application/json"}, 
            json=chat_payload
        )
        
        if chat_res.status_code == 200:
            english_advisory = chat_res.json()["choices"][0]["message"]["content"].strip()
            print("🧠 [AI Engine]: Processed successfully via Sarvam AI Fallback")
        else:
            raise HTTPException(status_code=502, detail=f"Sarvam fallback error: {chat_res.text}")


    # ==========================================
    # STEP 3: Translate to Regional Language
    # ==========================================
    translate_payload = {
        "input": english_advisory,
        "source_language_code": "en-IN",
        "target_language_code": active_lang,
        "model": "sarvam-translate:v1"
    }
    trans_headers = {**sarvam_headers, "Content-Type": "application/json"}
    
    trans_res = requests.post(
        "https://api.sarvam.ai/translate", 
        headers=trans_headers, 
        json=translate_payload
    )
    if trans_res.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Translation Error: {trans_res.text}")
        
    regional_advisory = trans_res.json().get("translated_text", "")


    # ==========================================
    # STEP 4: Text-to-Speech (Speak to the Farmer)
    # ==========================================
    tts_payload = {
        "text": regional_advisory,
        "language_code": active_lang,
        "model": "bulbul:v3",
        "speaker": "shubh"
    }
    
    tts_res = requests.post(
        "https://api.sarvam.ai/text-to-speech", 
        headers=trans_headers, 
        json=tts_payload
    )
    if tts_res.status_code != 200:
        raise HTTPException(status_code=502, detail=f"TTS Error: {tts_res.text}")
        
    base64_audio = tts_res.json().get("audios", [])[0]
    
    # Decode and save the audio locally so you can play it immediately
    output_filename = "digital_twin_response.wav"
    with open(output_filename, "wb") as f:
        f.write(base64.b64decode(base64_audio))


    # ==========================================
    # STEP 5: Return Clean Response
    # ==========================================
    return {
        "status": "success",
        "engine_used": engine_used,
        "pipeline_results": {
            "farmer_query": farmer_transcript,
            "advisory_english": english_advisory,
            "advisory_regional": regional_advisory,
            "audio_file": output_filename,
            
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("voice_pipeline:app", host="127.0.0.1", port=8000, reload=True)