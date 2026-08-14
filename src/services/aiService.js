import { GoogleGenAI } from '@google/genai'

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY

const RESPONSE_SCHEMA_PROMPT = `
Return response ONLY in strict JSON matching this schema, no markdown fences:
{
  "cropChoice": "Best crop recommendation for this soil and weather",
  "soilHealthImprovement": {
    "action": "Detailed action to improve soil quality, organic matter, pH or structure",
    "confidence": 88,
    "costBenefit": "Cost estimate; expected long-term yield or quality gain",
    "influencingFactors": ["factor1", "factor2", "factor3"]
  },
  "irrigation": {
    "action": "Irrigation timing/volume advice",
    "confidence": 85,
    "costBenefit": "Cost/water-savings estimate",
    "influencingFactors": ["factor1", "factor2"]
  },
  "nutrientApplication": {
    "action": "Organic & NPK fertilizer recommendation",
    "confidence": 90,
    "costBenefit": "Cost estimate; expected yield impact",
    "influencingFactors": ["factor1", "factor2"]
  },
  "riskMitigation": {
    "action": "Pest, disease or erosion prevention advice",
    "confidence": 80,
    "costBenefit": "Cost of prevention vs cost of potential crop loss",
    "influencingFactors": ["factor1", "factor2"]
  }
}
confidence must be a number 0-100 (no % sign). Keep every "action" to 1-2 sentences.
`

function buildPrompt({ lat, lon, weather, soil, ndvi, farmRecord }) {
  return `
You are an expert Agricultural & Soil Health Scientist AI advising a smallholder farmer in India.

Location: ${lat.toFixed(4)}, ${lon.toFixed(4)}
Weather: ${JSON.stringify(weather)}
Soil: ${JSON.stringify(soil)}
Satellite vegetation index (NDVI, simulated pending live feed): ${ndvi.value} (${ndvi.label})
Farmer record: ${JSON.stringify(farmRecord)}

Give specific, practical, low-cost-first recommendations for: soil health improvement,
irrigation, nutrient/fertilizer application, and risk mitigation (pest/disease/erosion),
plus the single best crop choice given all of the above.
${RESPONSE_SCHEMA_PROMPT}
`
}

async function callGemini(context) {
  const ai = new GoogleGenAI({ apiKey: API_KEY })
  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: buildPrompt(context),
  })
  const text = response.text.replace(/```json|```/g, '').trim()
  return JSON.parse(text)
}

// Deterministic, offline-safe fallback so the app is still useful with no
// API key and no connectivity — the PS explicitly calls for offline
// support, and recommendations should never simply fail to appear.
function ruleBasedFallback({ weather, soil, ndvi, farmRecord }) {
  const soilMoisture = soil.raw?.soilMoisture ?? 0.2
  const rain = weather.raw?.precipitation ?? 0
  const temp = weather.raw?.temperature_2m ?? 28

  const irrigationNeeded = soilMoisture < 0.2 && rain < 2
  const cropChoice =
    soilMoisture < 0.15
      ? 'Pearl Millet (Bajra) — drought-tolerant, suits low soil moisture'
      : soilMoisture > 0.3
      ? 'Paddy (Rice) — thrives with current high soil moisture'
      : 'Pigeon Pea (Tur/Arhar) — resilient, improves soil nitrogen'

  return {
    cropChoice,
    soilHealthImprovement: {
      action:
        ndvi.value < 0.35
          ? 'Vegetation cover is sparse — incorporate 2-3 tons/acre of farmyard manure or compost and consider a green-manure cover crop before next sowing.'
          : 'Maintain organic matter with a light compost top-dressing and rotate with a legume next season to sustain soil nitrogen.',
      confidence: 72,
      costBenefit: '≈ ₹2,000–2,500/acre; typically raises yield 10–20% over 2 seasons',
      influencingFactors: ['NDVI (' + ndvi.value + ')', 'Soil type: ' + farmRecord.soilType],
    },
    irrigation: {
      action: irrigationNeeded
        ? 'Soil moisture is low with little rain forecast — irrigate within the next 24-48 hours, preferably early morning or evening to reduce evaporation loss.'
        : 'Soil moisture is adequate — hold off irrigation and recheck in 2-3 days.',
      confidence: 78,
      costBenefit: irrigationNeeded ? 'Prevents yield loss from moisture stress' : 'Saves water and pumping cost',
      influencingFactors: ['Soil moisture: ' + soil.soilMoisture, 'Recent rainfall: ' + weather.precipitation],
    },
    nutrientApplication: {
      action:
        farmRecord.cropStage.includes('Vegetative') || farmRecord.cropStage.includes('Flowering')
          ? 'Apply a split dose of urea/NPK aligned to current growth stage; pair with micronutrient spray (zinc/boron) if leaf yellowing is seen.'
          : 'Base-dose NPK at sowing/land preparation per local soil-test recommendation.',
      confidence: 70,
      costBenefit: 'Moderate cost; targeted timing avoids nutrient waste and runoff',
      influencingFactors: ['Crop stage: ' + farmRecord.cropStage, 'Soil type: ' + farmRecord.soilType],
    },
    riskMitigation: {
      action:
        temp > 35
          ? 'Heat stress risk — mulch the root zone and irrigate lightly during peak heat to protect flowering/fruiting stages.'
          : rain > 20
          ? 'Heavy rain risk — check field drainage channels to prevent waterlogging and fungal disease onset.'
          : 'Conditions are stable — maintain routine pest scouting, especially around the current crop stage.',
      confidence: 65,
      costBenefit: 'Prevention is typically far cheaper than crop-loss recovery',
      influencingFactors: ['Air temp: ' + weather.temperature, 'Rainfall: ' + weather.precipitation],
    },
    engine: 'rule-based (offline)',
  }
}

export async function getFarmRecommendations(context) {
  if (!API_KEY) {
    return ruleBasedFallback(context)
  }

  try {
    const result = await callGemini(context)
    return { ...result, engine: 'Gemini' }
  } catch (err) {
    console.warn('Gemini unavailable, falling back to rule-based engine:', err.message)
    return ruleBasedFallback(context)
  }
}
