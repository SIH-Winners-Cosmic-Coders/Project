import torch
from datetime import datetime
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 1. Meta NLLB-200 Translation Engine
NMT_MODEL_ID = "facebook/nllb-200-distilled-600M"
nmt_tokenizer = None
nmt_model = None

# Mapping standard codes to NLLB codes
LANG_CODES_NLLB = {
    "od": "ory_Orya",  # Odia
    "hi": "hin_Deva",  # Hindi
    "te": "tel_Telu",  # Telugu
    "ta": "tam_Taml",  # Tamil
    "bn": "ben_Beng",  # Bengali
    "en": "eng_Latn",  # English
    # Fallback mappings for teammate's 3-letter codes
    "ory": "ory_Orya",
    "hin": "hin_Deva",
    "tel": "tel_Telu",
    "tam": "tam_Taml",
    "ben": "ben_Beng",
    "eng": "eng_Latn"
}

def load_nmt_engine():
    """Lazy loader for NLLB-200 model to preserve VRAM/RAM until needed."""
    global nmt_tokenizer, nmt_model
    if nmt_model is None:
        print("⏳ [NLLB-200] Loading local translation weights...")
        nmt_tokenizer = AutoTokenizer.from_pretrained(NMT_MODEL_ID)
        nmt_model = AutoModelForSeq2SeqLM.from_pretrained(NMT_MODEL_ID).to(DEVICE)
        print("✅ [NLLB-200] Translation engine ready!")
    return nmt_tokenizer, nmt_model


def get_offline_weather_and_soil_context(location: str = "Odisha", soil_type: str = "Alluvial") -> dict:
    """Deterministic Rule-Based Agro-Climatology Engine using system date."""
    month = datetime.now().month  # 1-12
    
    # 1. Agro-Climatic Season Rules
    if 6 <= month <= 9:
        season_name = "Kharif (Monsoon / High Humidity)"
        spray_rule = "Avoid foliar sprays if rain is expected within 4 hours; always mix a sticker/spreader agent (0.5ml/L)."
        drainage_rule = "Maintain drainage furrows to prevent root stagnation and fungal collar rot."
        risk_profile = "High humidity (>85%) favours blast, sheath blight, and leaf spot."
    elif 10 <= month <= 11:
        season_name = "Post-Monsoon / Autumn"
        spray_rule = "Spray in the early afternoon after heavy morning dew dries."
        drainage_rule = "Conserve residual soil moisture."
        risk_profile = "Vulnerable to sucking pests and leaf miners during vegetative/flowering phase."
    elif 12 <= month or month <= 2:
        season_name = "Rabi (Winter / Heavy Dew)"
        spray_rule = "Apply fungicides after 10 AM once dew clears from foliage."
        drainage_rule = "Irrigate at critical stages (e.g., crown root initiation / pod filling)."
        risk_profile = "High likelihood of powdery mildew, rust, and aphid colonies."
    else:
        season_name = "Zaid (Summer / High Heat)"
        spray_rule = "Strictly spray before 8:30 AM or after 5:00 PM to prevent chemical scorch."
        drainage_rule = "Apply organic mulch around root zones to retain water."
        risk_profile = "High heat stress and red spider mite infestation."

    # 2. Soil-Specific Absorption Adjustments
    soil_lower = (soil_type or "alluvial").lower()
    if "sandy" in soil_lower:
        soil_advisory = "Sandy soil leaches nitrogen rapidly; split fertilizer into smaller, frequent doses."
    elif "clay" in soil_lower or "black" in soil_lower:
        soil_advisory = "Heavy clay retains moisture; avoid over-watering to prevent fungal root suffocation."
    elif "red" in soil_lower or "laterite" in soil_lower:
        soil_advisory = "Red laterite soils tend to be acidic; combine rock phosphate or lime to optimize nutrient uptake."
    else:
        soil_advisory = "Alluvial soil has balanced retention; follow standard recommended fertilizer schedules."

    return {
        "season": season_name,
        "spray_rule": spray_rule,
        "drainage_rule": drainage_rule,
        "risk_profile": risk_profile,
        "soil_advisory": soil_advisory
    }


def translate_to_indic(english_text: str, lang_key: str) -> str:
    """Translates English text into target Indic language using local NLLB-200."""
    target_lang_code = LANG_CODES_NLLB.get(lang_key, "ory_Orya")
    
    if target_lang_code == "eng_Latn" or not english_text.strip():
        return english_text

    tokenizer, model = load_nmt_engine()
    lines = [line.strip() for line in english_text.split("\n") if line.strip()]
    if not lines:
        return ""

    target_token_id = tokenizer.convert_tokens_to_ids(target_lang_code)
    translated_lines = []

    for line in lines:
        inputs = tokenizer(line, return_tensors="pt", truncation=True, max_length=256).to(DEVICE)
        with torch.no_grad():
            generated_tokens = model.generate(
                **inputs,
                forced_bos_token_id=target_token_id,
                max_length=256,
                num_beams=2
            )
        decoded = tokenizer.decode(generated_tokens[0], skip_special_tokens=True)
        translated_lines.append(decoded.strip())

    return "\n".join(translated_lines)