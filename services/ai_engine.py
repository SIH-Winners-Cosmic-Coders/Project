import json
import os
import re
import asyncio
import ollama
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Global Engine Memory
INTENTS = {}
VECTOR_STORE = None
OLLAMA_MODEL = "qwen2.5:3b"

def initialize_ai():
    """Run this once when the FastAPI server starts"""
    global INTENTS, VECTOR_STORE
    
    print("🧠 Initializing AnnaDATA Edge AI Engine...")

    # 1. Load the Instant Safety Net (Defense 1)
    try:
        if os.path.exists("intents.json"):
            with open("intents.json", "r", encoding="utf-8") as f:
                INTENTS = json.load(f)
            print(f"✅ Loaded {len(INTENTS)} quick-response intents.")
        else:
            print("⚠️ intents.json not found.")
    except Exception as e:
        print(f"⚠️ Intents load warning: {e}")

    # 2. Build the Document RAG Database
    try:
        if not os.path.exists("docs"):
            os.makedirs("docs")
            
        loader = PyPDFDirectoryLoader("docs")
        docs = loader.load()
        
        if docs:
            print(f"📚 Found {len(docs)} document pages. Building vector index...")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            splits = text_splitter.split_documents(docs)
            
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            
            VECTOR_STORE = Chroma.from_documents(
                documents=splits, 
                embedding=embeddings, 
                persist_directory="./chroma_db"
            )
            print("✅ RAG Database initialized successfully.")
        else:
            print("⚠️ No PDFs found in 'docs/' folder. RAG is disabled.")
    except Exception as e:
        print(f"⚠️ RAG Initialization Error: {e}")

def dynamic_heuristic_agronomist(raw_query: str, system_context: str, rag_snippet: str = "") -> str:
    """Defense 2: Context-Aware Dynamic Fallback Engine when local LLM is offline"""
    query_lower = raw_query.lower()
    context_lower = system_context.lower()

    # Extract Crop from context
    detected_crop = "your crop"
    crops = ["paddy", "rice", "sugarcane", "maize", "corn", "cotton", "wheat", "mustard", "groundnut", "potato", "tomato", "ragi", "moong"]
    for c in crops:
        if c in context_lower or c in query_lower:
            detected_crop = c.capitalize()
            if detected_crop == "Rice":
                detected_crop = "Paddy"
            break

    # If RAG found an exact match snippet from the PDF, use it to frame the answer
    if rag_snippet and len(rag_snippet.strip()) > 30:
        clean_rag = rag_snippet.replace("\n", " ").strip()
        first_sentence = clean_rag.split(". ")[0] + "."
        return f"Based on verified agronomic records for {detected_crop}: {first_sentence}"

    # Heuristic Rule 1: Fertilizer & Nutrition
    if any(w in query_lower for w in ["fertilizer", "fertiliser", "khaad", "npk", "urea", "dap", "potash", "nutrient"]):
        if "Sugarcane" in detected_crop:
            return "For Sugarcane, apply NPK at 250:100:60 kg/ha. Apply full Phosphorus and 50% Potash as a basal dose, and top-dress Nitrogen in equal splits at 45 and 90 days."
        elif "Paddy" in detected_crop:
            return "For Paddy, apply 100-120:50-60:50-60 kg NPK/ha. Give 25% Nitrogen, full Phosphorus, and 50% Potash as basal puddle application, then top-dress Nitrogen at active tillering."
        elif "Maize" in detected_crop:
            return "For Maize, apply 120:60:50 kg NPK/ha. Apply full P and K as basal, and top-dress Nitrogen in two equal splits at knee-high and tasseling stages."
        elif "Cotton" in detected_crop:
            return "For Cotton, apply 120:60:60 kg NPK/ha with split Nitrogen applications during vegetative, square formation, and flowering stages."
        return f"For {detected_crop}, apply balanced NPK based on soil test values, split Nitrogen into basal and top-dressing phases, and supplement with organic compost."

    # Heuristic Rule 2: Water & Irrigation
    if any(w in query_lower for w in ["irrigation", "water", "irrigate", "moisture", "dry", "watering"]):
        return f"For {detected_crop}, maintain steady root zone moisture and avoid water stagnation. Prioritize irrigation during critical stages like tillering and flowering."

    # Heuristic Rule 3: Pest, Disease & Symptoms
    if any(w in query_lower for w in ["pest", "disease", "insect", "bug", "fungus", "yellow", "blight", "borer", "spray"]):
        if "Paddy" in detected_crop:
            return "For Paddy pests like Stem Borer or BPH, install pheromone traps and maintain field alleyways. Spray Chlorantraniliprole 18.5% SC if infestation crosses economic thresholds."
        elif "Sugarcane" in detected_crop:
            return "For Early Shoot Borer in Sugarcane, apply Chlorantraniliprole 0.4% G in planting furrows and avoid water stress during early shoot formation."
        return f"Inspect {detected_crop} foliage for discolored lesions or pest damage. Apply targeted bio-pesticides like Neem oil (1500 ppm) or recommended chemical formulations if symptoms persist."

    # Heuristic Rule 4: Subsidies & Government Schemes
    if any(w in query_lower for w in ["subsidy", "scheme", "government", "pm", "kalia", "kusum", "loan", "kisan"]):
        return "Eligible farmers can access up to 70% subsidy on solar irrigation under PM-KUSUM Component-B, direct input support via KALIA and PM-KISAN, and micro-irrigation support through PMKSY."

    # Heuristic Rule 5: Mandi & Economics
    if any(w in query_lower for w in ["mandi", "msp", "price", "profit", "sell", "market", "revenue"]):
        return f"Market advisories recommend comparing current spot mandi rates with national MSP thresholds before selling {detected_crop}. If rates are below MSP, utilize government procurement channels."

    # Default Context Fallback
    return f"AnnaDATA digital twin is tracking your {detected_crop} field. Ensure timely weeding, monitor topsoil moisture, and maintain scheduled nutrient top-dressing."

async def get_ai_response(raw_query: str, system_context: str) -> str:
    """Master routing function executing Strategy 3 -> Strategy 2 -> Strategy 1 -> Defense 2"""
    query_lower = raw_query.lower()

    # STRATEGY 3: Instant JSON Fallback Match (Defense 1)
    for key, answer in INTENTS.items():
        if all(word in query_lower for word in key.split()):
            print(f"⚡ Instant Intent Match: {key}")
            return answer

    # STRATEGY 2: RAG Context Retrieval
    rag_context = ""
    if VECTOR_STORE:
        try:
            results = VECTOR_STORE.similarity_search(raw_query, k=2)
            rag_context = "\n".join([doc.page_content for doc in results])
            if rag_context:
                print("📖 RAG Context retrieved from local PDFs.")
        except Exception as e:
            print(f"⚠️ Search warning: {e}")

    # STRATEGY 1: Local Ollama Generation
    final_prompt = f"{system_context}\n\n"
    if rag_context:
        final_prompt += f"--- LOCAL DOCUMENT KNOWLEDGE ---\n{rag_context}\n------------------------------\n\n"
    final_prompt += f"Farmer's Question: {raw_query}\n\nProvide a concise, practical agronomic recommendation in simple English."

    def call_ollama_sync():
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": final_prompt}],
            options={"temperature": 0.3, "num_predict": 120}
        )
        return response["message"]["content"].strip()

    try:
        reply = await asyncio.to_thread(call_ollama_sync)
        return reply
    except Exception as e:
        print(f"⚠️ Ollama unreachable/missing ({e}). Falling back to Heuristic Engine (Defense 2).")
        # DEFENSE 2: Dynamic Heuristic Fallback
        return dynamic_heuristic_agronomist(raw_query, system_context, rag_context)