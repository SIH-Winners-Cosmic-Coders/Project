// Satellite vegetation index (NDVI).
//
// A production build would pull this from Sentinel-2 / MODIS via Google
// Earth Engine or Copernicus, keyed by field polygon. That needs server-side
// credentials, so here we derive a clearly-labeled *simulated* NDVI from
// season + soil moisture, so the recommendation engine has a value to
// reason over today. Replace `estimateNDVI` with a real fetch once a
// satellite data provider is wired up.
export function estimateNDVI(lat, soilMoisture) {
  const month = new Date().getMonth() // 0-11
  const isKharif = month >= 5 && month <= 9 // Jun-Oct: monsoon cropping season
  const isNorthernHemisphere = lat >= 0

  const seasonFactor = isNorthernHemisphere
    ? (isKharif ? 0.15 : -0.05)
    : (!isKharif ? 0.15 : -0.05)

  const moistureFactor = Math.min(Math.max(soilMoisture, 0), 0.4) * 0.6

  const ndvi = Math.min(0.92, Math.max(0.08, 0.45 + seasonFactor + moistureFactor))

  return {
    value: Number(ndvi.toFixed(2)),
    label: ndvi > 0.6 ? 'Dense healthy canopy' : ndvi > 0.35 ? 'Moderate cover' : 'Sparse / stressed cover',
    simulated: true,
  }
}
