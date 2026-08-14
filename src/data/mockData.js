// Placeholder farmer-record & crop-stage data.
//
// In production this comes from a farm-management backend (per-farmer
// records, sensor IDs, sowing dates). Until that's wired up, AnnaDATA
// derives a plausible record from the season and location so the rest of
// the pipeline (recommendations, feedback) has something real to work
// against.

const SOIL_TYPES = ['Clay Loam', 'Sandy Loam', 'Alluvial', 'Black Cotton Soil', 'Red Loam']
const CROP_STAGES = [
  'Land Preparation',
  'Sowing (Day 1-10)',
  'Vegetative Stage',
  'Flowering Stage',
  'Grain Filling',
  'Maturity / Pre-Harvest',
]

function hashToIndex(str, mod) {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = (hash * 31 + str.charCodeAt(i)) >>> 0
  }
  return hash % mod
}

// Deterministic per-coordinate mock so the same field always shows the
// same "farmer record" during a session, instead of re-randomizing.
export function getFarmerRecord(lat, lng) {
  const key = `${lat.toFixed(2)}_${lng.toFixed(2)}`
  const soilType = SOIL_TYPES[hashToIndex(key, SOIL_TYPES.length)]
  const cropStage = CROP_STAGES[hashToIndex(key + 'stage', CROP_STAGES.length)]
  const daysSinceIrrigation = 1 + (hashToIndex(key + 'irr', 6))
  const yieldTons = (2.5 + (hashToIndex(key + 'yield', 30) / 10)).toFixed(1)

  return {
    cropStage,
    lastIrrigationDate: `${daysSinceIrrigation} day${daysSinceIrrigation > 1 ? 's' : ''} ago`,
    soilType,
    farmerHistoricalYield: `${yieldTons} tons/hectare`,
    sensorsInstalled: {
      soilMoistureSensor: hashToIndex(key + 's1', 2) === 0,
      leafWetnessSensor: hashToIndex(key + 's2', 2) === 0,
      localWeatherStation: hashToIndex(key + 's3', 2) === 0,
    },
  }
}
