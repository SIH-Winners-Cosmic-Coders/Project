import axios from 'axios'

// Open-Meteo also exposes modeled soil temperature/moisture layers, which
// stand in for a physical soil-sensor feed until real sensor hardware is
// connected. Swap this for your sensor gateway's endpoint when available —
// the shape returned below is what the rest of the app expects.
export async function fetchSoil(lat, lon) {
  const response = await axios.get('https://api.open-meteo.com/v1/forecast', {
    params: {
      latitude: lat,
      longitude: lon,
      hourly: ['soil_temperature_0cm', 'soil_moisture_0_to_1cm'].join(','),
      timezone: 'auto',
    },
  })

  const hourly = response.data.hourly
  const nowIndex = 0 // first entry is the current/nearest hour

  return {
    soilTemp: `${hourly.soil_temperature_0cm[nowIndex]} °C`,
    soilMoisture: `${hourly.soil_moisture_0_to_1cm[nowIndex]} m³/m³`,
    raw: {
      soilTemp: hourly.soil_temperature_0cm[nowIndex],
      soilMoisture: hourly.soil_moisture_0_to_1cm[nowIndex],
    },
  }
}
