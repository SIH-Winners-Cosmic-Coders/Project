import axios from 'axios'

// Open-Meteo — free, no API key required.
export async function fetchWeather(lat, lon) {
  const response = await axios.get('https://api.open-meteo.com/v1/forecast', {
    params: {
      latitude: lat,
      longitude: lon,
      current: [
        'temperature_2m',
        'relative_humidity_2m',
        'precipitation',
        'surface_pressure',
        'wind_speed_10m',
      ].join(','),
      timezone: 'auto',
    },
  })

  const current = response.data.current
  return {
    temperature: `${current.temperature_2m} °C`,
    humidity: `${current.relative_humidity_2m} %`,
    precipitation: `${current.precipitation} mm`,
    windSpeed: `${current.wind_speed_10m} km/h`,
    raw: current,
  }
}
