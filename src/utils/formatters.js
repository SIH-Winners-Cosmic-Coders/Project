export const formatCoordinates = (lat, lng) => {
  const latDirection = lat >= 0 ? 'N' : 'S'
  const lngDirection = lng >= 0 ? 'E' : 'W'
  return `${Math.abs(lat).toFixed(4)}° ${latDirection}, ${Math.abs(lng).toFixed(4)}° ${lngDirection}`
}

// Accepts either a number (0-100) or a legacy string like "88%".
export const normalizeConfidence = (confidence) => {
  if (typeof confidence === 'number') return Math.round(confidence)
  const parsed = parseInt(confidence, 10)
  return Number.isNaN(parsed) ? 0 : parsed
}

export const getConfidenceColor = (confidence) => {
  const value = normalizeConfidence(confidence)
  if (value >= 80) return '#7BA05B' // leaf green
  if (value >= 60) return '#E8C468' // wheat gold
  return '#C9663B' // rust — low confidence, flag for review
}
