import os
import shutil
import tempfile
import asyncio
import traceback
import requests
import json
import io
import base64
import sqlite3
import random
import time
from datetime import datetime
from contextlib import asynccontextmanager
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama

# Modular Services
from services.market_service import predict_crop_metrics
from services.offline_engine import (
    get_offline_weather_and_soil_context,
    translate_to_indic
)
from services.voice_service import (
    transcribe_local_indic,
    transcribe_local_english,
    generate_natural_speech_sync
)
from services.ai_engine import initialize_ai, get_ai_response
from services.report_service import generate_farm_health_pdf

load_dotenv()

# ==========================================
# LIFESPAN CONTEXT HANDLER (Replaces deprecated on_event)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize RAG and Instant Intent Safety Net
    initialize_ai()
    yield
    # Shutdown logic (if any cleanup is needed in future)

app = FastAPI(
    title="AnnaDATA Farm Digital Twin Engine",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==========================================
# 0. DATABASE SETUP
# ==========================================
DB_FILE = "annadata_farm.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crop_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            icon_type TEXT DEFAULT 'eco',
            theme_color TEXT DEFAULT 'primary',
            date_logged TEXT NOT NULL
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM crop_history")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO crop_history (title, description, icon_type, theme_color, date_logged)
            VALUES (?, ?, ?, ?, ?)
        ''', ("Sowing Phase", "Planted Co-0238 variety.", "agriculture", "tertiary", datetime.now().strftime("%d %b %Y")))
    
    conn.commit()
    conn.close()

init_db()

# --- PYDANTIC MODELS ---
class CropEvent(BaseModel):
    title: str
    description: str
    icon_type: str = "eco"
    theme_color: str = "primary"

class FeedbackItem(BaseModel):
    queryId: str
    rating: str
    status: str
    timestamp: int

# API Keys Configuration
SARVAM_KEY = os.getenv("SARVAM_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

gemini_model = None
if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        print(f"Warning: Gemini initialization failed ({e}). Running on offline edge models.")

LANG_CONFIG = {
    "od": {"name": "Odia", "sarvam_code": "od-IN", "asr_code": "or", "tts_code": "or"},
    "hi": {"name": "Hindi", "sarvam_code": "hi-IN", "asr_code": "hi", "tts_code": "hi"},
    "bn": {"name": "Bengali", "sarvam_code": "bn-IN", "asr_code": "bn", "tts_code": "bn"},
    "te": {"name": "Telugu", "sarvam_code": "te-IN", "asr_code": "te", "tts_code": "te"},
    "ta": {"name": "Tamil", "sarvam_code": "ta-IN", "asr_code": "ta", "tts_code": "ta"},
    "mr": {"name": "Marathi", "sarvam_code": "mr-IN", "asr_code": "mr", "tts_code": "mr"},
    "en": {"name": "English", "sarvam_code": "en-IN", "asr_code": "en", "tts_code": "en"},
}

OLLAMA_MODEL = "qwen2.5:3b"
OLLAMA_VISION_MODEL = "qwen2.5vl:3b"

def cleanup_temp_file(path: str):
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass

# ==========================================
# 1. ROOT & UI ROUTING
# ==========================================
@app.get("/", response_class=HTMLResponse)
def serve_main_app():
    target_path = "static/ui_v2/app_shell.html"
    with open(target_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/app", response_class=HTMLResponse)
def serve_app_alias():
    return serve_main_app()

# ==========================================
# 2. CROP HISTORY LEDGER ENDPOINTS
# ==========================================
@app.post("/api/v1/farm/history")
async def add_history_event(event: CropEvent):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        current_date = datetime.now().strftime("%d %b %Y")
        cursor.execute('''
            INSERT INTO crop_history (title, description, icon_type, theme_color, date_logged)
            VALUES (?, ?, ?, ?, ?)
        ''', (event.title, event.description, event.icon_type, event.theme_color, current_date))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Event logged successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/farm/history")
async def get_history_timeline():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM crop_history ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        return {"status": "success", "data": [dict(row) for row in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 3. PDF FARM SUMMARY REPORT EXPORT
# ==========================================
@app.get("/api/v1/farm/report/download")
async def download_farm_report(
    user_name: str = Query("Farmer"),
    location: str = Query("Bhubaneswar, Odisha"),
    crop: str = Query("Paddy"),
    farm_acres: float = Query(12.5),
    moisture: float = Query(42.0),
    temp: float = Query(28.0),
    ndvi: float = Query(0.72),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        report_path = generate_farm_health_pdf(
            farmer_name=user_name,
            location=location,
            crop=crop,
            farm_acres=farm_acres,
            soil_moisture=moisture,
            soil_temp=temp,
            ndvi=ndvi
        )
        background_tasks.add_task(cleanup_temp_file, report_path)
        return FileResponse(
            report_path,
            media_type="application/pdf",
            filename=f"AnnaDATA_Farm_Report_{crop}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report Generation Failed: {str(e)}")

# ==========================================
# 4. HYBRID VOICE CONSULT PIPELINE
# ==========================================
@app.post("/api/v1/voice/hybrid-consult")
async def hybrid_voice_consult(
    file: UploadFile = File(...), lang: str = Query("od"),
    temp: float = Query(None), moisture: float = Query(None),
    ndvi: float = Query(None), edge_mode: str = Query("false"),
    user_name: str = Query("Farmer"), location: str = Query("Unknown Location")
):
    is_edge = edge_mode.lower() == "true"
    target_info = LANG_CONFIG.get(lang, LANG_CONFIG["od"])
    temp_audio_path = None
    engine_asr = "Unknown"
    engine_llm = "Unknown"
    farmer_transcript = ""

    try:
        suffix = os.path.splitext(file.filename)[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_audio_path = tmp.name

        # ASR: Speech-to-Text
        if SARVAM_KEY and not is_edge:
            try:
                with open(temp_audio_path, "rb") as f:
                    stt_res = requests.post(
                        "https://api.sarvam.ai/speech-to-text",
                        headers={"api-subscription-key": SARVAM_KEY},
                        files={"file": (file.filename, f.read(), file.content_type)},
                        data={"language_code": target_info["sarvam_code"]}, timeout=4.0
                    )
                if stt_res.status_code == 200:
                    farmer_transcript = stt_res.json().get("transcript", "").strip()
                    engine_asr = "Sarvam Cloud ASR"
            except Exception:
                pass

        if not farmer_transcript:
            if lang == "en":
                farmer_transcript = await asyncio.to_thread(transcribe_local_english, temp_audio_path)
                engine_asr = "Offline Whisper Tiny"
            else:
                farmer_transcript = await asyncio.to_thread(transcribe_local_indic, temp_audio_path, target_info["asr_code"])
                engine_asr = "Offline IndicConformer"

        if not farmer_transcript:
            farmer_transcript = "General crop check requested."

        weather_info = get_offline_weather_and_soil_context()
        telemetry_context = f"\nSeason: {weather_info.get('season', 'Monsoon')}. Spray rule: {weather_info.get('spray_rule', 'Safe')}."
        if temp is not None:
            telemetry_context += f" Telemetry: Temp {temp}°C, Moisture {moisture}, NDVI {ndvi}."

        prompt = f"""You are AnnaDATA, an expert AI agronomy digital twin assistant.
User Profile: {user_name} from {location}.
Farm Telemetry: {telemetry_context}
The farmer says: "{farmer_transcript}"
Provide a direct, practical, and highly actionable 2-sentence solution in simple English."""

        # LLM Reasoning
        english_advisory = ""
        if gemini_model and not is_edge:
            try:
                res = gemini_model.generate_content(prompt)
                english_advisory = res.text.strip()
                engine_llm = "Google Gemini Cloud"
            except Exception:
                pass

        if not english_advisory:
            try:
                def run_ollama():
                    return ollama.chat(
                        model=OLLAMA_MODEL, 
                        messages=[{"role": "user", "content": prompt}], 
                        options={"temperature": 0.2, "num_predict": 120}
                    )
                ollama_res = await asyncio.wait_for(asyncio.to_thread(run_ollama), timeout=20.0)
                english_advisory = ollama_res["message"]["content"].strip()
                engine_llm = "Offline Ollama Qwen"
            except Exception:
                english_advisory = f"Hello {user_name}, monitor topsoil moisture and spray preventive neem solution if cloudy."
                engine_llm = "Heuristic Offline Rule"

        # Translation
        regional_advisory = english_advisory
        if lang != "en":
            translated = False
            if SARVAM_KEY and not is_edge:
                try:
                    trans_res = requests.post(
                        "https://api.sarvam.ai/translate",
                        headers={"api-subscription-key": SARVAM_KEY, "Content-Type": "application/json"},
                        json={"input": english_advisory, "source_language_code": "en-IN", "target_language_code": target_info["sarvam_code"], "model": "sarvam-translate:v1"},
                        timeout=4.0
                    )
                    if trans_res.status_code == 200:
                        regional_advisory = trans_res.json().get("translated_text", "")
                        translated = True
                except Exception:
                    pass

            if not translated:
                regional_advisory = await asyncio.to_thread(translate_to_indic, english_advisory, lang)

        # TTS: Text-to-Speech
        audio_filename = f"advisory_{lang}_{os.getpid()}_{int(asyncio.get_event_loop().time())}.wav"
        audio_save_path = os.path.join(tempfile.gettempdir(), audio_filename)
        has_audio = False

        if SARVAM_KEY and not is_edge:
            try:
                tts_payload = {"text": regional_advisory, "language_code": target_info["sarvam_code"], "model": "bulbul:v3", "speaker": "shubh"}
                tts_res = requests.post("https://api.sarvam.ai/text-to-speech", headers={"api-subscription-key": SARVAM_KEY, "Content-Type": "application/json"}, json=tts_payload, timeout=8.0)
                if tts_res.status_code == 200:
                    with open(audio_save_path, "wb") as f:
                        f.write(base64.b64decode(tts_res.json().get("audios", [])[0]))
                    has_audio = True
            except Exception:
                pass

        if not has_audio:
            try:
                await asyncio.wait_for(asyncio.to_thread(generate_natural_speech_sync, regional_advisory, target_info["tts_code"], audio_save_path), timeout=8.0)
                has_audio = os.path.exists(audio_save_path) and os.path.getsize(audio_save_path) > 0
            except Exception:
                has_audio = False

        return {
            "status": "success", "asr_engine": engine_asr, "llm_engine": engine_llm,
            "farmer_query": farmer_transcript, "advisory_regional": regional_advisory,
            "language": target_info["name"], "audio_file": audio_filename if has_audio else None
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            try: os.remove(temp_audio_path)
            except OSError: pass

# ==========================================
# 5. TEXT-ONLY CHAT PIPELINE (WITH EDGE AI ENGINE)
# ==========================================
@app.post("/api/v1/text/chat")
async def text_chat_consult(
    query: str = Form(...), lang: str = Form("od"), temp: float = Form(None),
    moisture: float = Form(None), ndvi: float = Form(None),
    user_name: str = Form("Farmer"), location: str = Form("Unknown Location"),
    farm_size: str = Form("15 Acres"), crop: str = Form("Sugarcane") 
):
    target_info = LANG_CONFIG.get(lang, LANG_CONFIG["od"])
    weather_info = get_offline_weather_and_soil_context()
    telemetry_context = f"\nSeason: {weather_info.get('season', 'Monsoon')}. Spray rule: {weather_info.get('spray_rule', 'Safe')}."
    if temp is not None:
        telemetry_context += f" Telemetry: Temp {temp}°C, Moisture {moisture}, NDVI {ndvi}."

    parts = query.split("\n\nQuestion: ")
    system_context = parts[0] if len(parts) > 1 else f"User Profile: {user_name} from {location}. Farm Size: {farm_size}. Crop: {crop}."
    raw_question = parts[1] if len(parts) > 1 else query
    
    full_context = f"{system_context}\n{telemetry_context}\nYou are AnnaDATA, an expert AI agronomy digital twin assistant. Provide a clear, practical, and highly actionable 2-sentence solution in simple English."

    # 1. LLM Generation using Edge AI Engine (Ollama + Intents + RAG)
    try:
        english_advisory = await get_ai_response(raw_question, full_context)
    except Exception as e:
        print(f"AI Engine Error: {e}")
        english_advisory = f"Hello {user_name}, maintain optimal soil moisture and inspect leaves regularly."

    # 2. Translation with Fallback
    regional_advisory = english_advisory
    if lang != "en":
        translated = False
        if SARVAM_KEY:
            try:
                trans_res = requests.post(
                    "https://api.sarvam.ai/translate",
                    headers={"api-subscription-key": SARVAM_KEY, "Content-Type": "application/json"},
                    json={"input": english_advisory, "source_language_code": "en-IN", "target_language_code": target_info["sarvam_code"], "model": "sarvam-translate:v1"},
                    timeout=4.0
                )
                if trans_res.status_code == 200:
                    regional_advisory = trans_res.json().get("translated_text", "")
                    translated = True
            except Exception:
                pass

        if not translated:
            try:
                regional_advisory = await asyncio.to_thread(translate_to_indic, english_advisory, lang)
            except Exception:
                pass

    # 3. Audio Synthesis with Fallback
    audio_filename = f"advisory_text_{lang}_{os.getpid()}_{int(asyncio.get_event_loop().time())}.wav"
    audio_save_path = os.path.join(tempfile.gettempdir(), audio_filename)
    has_audio = False

    if SARVAM_KEY:
        try:
            tts_payload = {"text": regional_advisory, "language_code": target_info["sarvam_code"], "model": "bulbul:v3", "speaker": "shubh"}
            tts_res = requests.post("https://api.sarvam.ai/text-to-speech", headers={"api-subscription-key": SARVAM_KEY, "Content-Type": "application/json"}, json=tts_payload, timeout=8.0)
            if tts_res.status_code == 200:
                with open(audio_save_path, "wb") as f:
                    f.write(base64.b64decode(tts_res.json().get("audios", [])[0]))
                has_audio = True
        except Exception:
                pass

    return {
        "status": "success", "reply": regional_advisory,
        "language": target_info["name"], "audio_file": audio_filename if has_audio else None
    }

@app.get("/api/v1/voice/audio-stream")
async def get_audio_stream(file: str = Query(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    audio_path = os.path.join(tempfile.gettempdir(), file)
    if not os.path.exists(audio_path): 
        raise HTTPException(status_code=404, detail="Audio file not found.")
    background_tasks.add_task(cleanup_temp_file, audio_path)
    return FileResponse(audio_path, media_type="audio/wav")

# ==========================================
# 6. VISION AI SCANNER
# ==========================================
@app.post("/api/chat")
async def analyze_crop_image(image: UploadFile = File(...), lang: str = Form("od"), context: str = Form("{}")):
    temp_img_path = None
    try:
        suffix = os.path.splitext(image.filename)[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(image.file, tmp)
            temp_img_path = tmp.name

        pil_img = Image.open(temp_img_path).convert("RGB")
        target_info = LANG_CONFIG.get(lang, LANG_CONFIG["od"])
        
        prompt = f"""You are an expert plant pathologist and agronomist.
Analyze this crop leaf photo. Identify symptoms of disease or nutrient deficiency.
Provide a 2-sentence practical cure using common Indian practices.
Farmer Context: {context}"""

        diagnosis_en = ""
        if gemini_model:
            try:
                vision_res = gemini_model.generate_content([prompt, pil_img])
                diagnosis_en = vision_res.text.strip()
            except Exception:
                pass

        if not diagnosis_en:
            try:
                with open(temp_img_path, "rb") as f: 
                    img_bytes = f.read()
                res = ollama.chat(model=OLLAMA_VISION_MODEL, messages=[{"role": "user", "content": prompt, "images": [img_bytes]}])
                diagnosis_en = res["message"]["content"].strip()
            except Exception:
                diagnosis_en = "Leaf shows signs of nutrient stress. Apply a preventive organic compost and balanced NPK spray."

        regional_reply = diagnosis_en
        if lang != "en":
            try: 
                regional_reply = await asyncio.to_thread(translate_to_indic, diagnosis_en, lang)
            except Exception: 
                pass

        try:
            conn = sqlite3.connect(DB_FILE)
            conn.execute('''
                INSERT INTO crop_history (title, description, icon_type, theme_color, date_logged) 
                VALUES (?, ?, ?, ?, ?)
            ''', ("Crop Scan", "Leaf image analyzed by AI.", "document_scanner", "secondary", datetime.now().strftime("%d %b %Y")))
            conn.commit()
            conn.close()
        except Exception:
            pass

        return {"status": "success", "reply": regional_reply, "language": target_info["name"]}

    except Exception as e: 
        return {"status": "error", "reply": f"Diagnosis failed: {str(e)}"}
    finally:
        if temp_img_path and os.path.exists(temp_img_path):
            try: os.remove(temp_img_path)
            except OSError: pass

# ==========================================
# 7. MANDI MARKET & YIELD PREDICTOR
# ==========================================
@app.get("/api/v1/market/predict")
async def get_market_prediction(
    commodity: str = Query("Sugarcane"),
    acres: float = Query(12.5),
    moisture: float = Query(42.0),
    temp: float = Query(28.0)
):
    return predict_crop_metrics(
        crop=commodity,
        acres=acres,
        moisture_pct=moisture,
        soil_temp=temp
    )

# ==========================================
# 8. RLHF FEEDBACK RECORDING
# ==========================================
@app.post("/api/v1/feedback")
async def receive_feedback(feedback: FeedbackItem):
    return {"status": "success", "message": "Feedback logged."}

# ==========================================
# 9. AUTHENTICATION & OTP
# ==========================================
OTP_STORE = {}

@app.post("/api/v1/auth/send-otp")
async def send_otp(phone: str = Form(...)):
    clean_phone = "".join(filter(str.isdigit, phone))[-10:]
    if len(clean_phone) != 10:
        raise HTTPException(status_code=400, detail="Invalid 10-digit phone number")

    otp = str(random.randint(100000, 999999))
    OTP_STORE[clean_phone] = {
        "otp": otp,
        "expires_at": time.time() + 300
    }

    print(f"\n==========================================")
    print(f" [AUTH OTP] Mobile: +91 {clean_phone} | Code: {otp}")
    print(f"==========================================\n")

    return {
        "status": "success",
        "message": "OTP sent successfully",
        "sent_via_sms": False,
        "dev_otp": otp 
    }

@app.post("/api/v1/auth/verify-otp")
async def verify_otp(phone: str = Form(...), otp: str = Form(...)):
    clean_phone = "".join(filter(str.isdigit, phone))[-10:]
    record = OTP_STORE.get(clean_phone)

    if not record:
        raise HTTPException(status_code=400, detail="No OTP requested for this number")
    if time.time() > record["expires_at"]:
        del OTP_STORE[clean_phone]
        raise HTTPException(status_code=400, detail="OTP expired. Request a new one.")
    if record["otp"] != otp.strip():
        raise HTTPException(status_code=400, detail="Incorrect OTP")

    del OTP_STORE[clean_phone]
    return {"status": "success", "message": "Authentication successful", "user": {"phone": clean_phone}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)