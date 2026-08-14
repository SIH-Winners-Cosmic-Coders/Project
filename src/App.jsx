import React, { useState } from 'react'
import MapView from './components/MapView'
import DataSidebar from './components/DataSidebar'
import OfflineBanner from './components/OfflineBanner'
import { fetchWeather } from './services/weatherApi'
import { fetchSoil } from './services/soilApi'
import { estimateNDVI } from './services/satelliteApi'
import { getFarmRecommendations } from './services/aiService'
import { getFarmerRecord } from './data/mockData'
import { cacheFieldSnapshot, getCachedFieldSnapshot, isOnline, feedbackKey } from './services/offlineSync'
import './App.css'

export default function App() {
  const [selectedPoint, setSelectedPoint] = useState(null)
  const [farmData, setFarmData] = useState(null)
  const [farmRecord, setFarmRecord] = useState(null)
  const [recommendations, setRecommendations] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleLocationSelect = async ({ lat, lng }) => {
    setSelectedPoint({ lat, lng })
    setLoading(true)
    setRecommendations(null)
    setFarmData(null)

    const cacheKey = feedbackKey(lat, lng)
    const record = getFarmerRecord(lat, lng)
    setFarmRecord(record)

    // Offline: fall back straight to the last cached snapshot for this
    // field, if one exists, instead of attempting network calls.
    if (!isOnline()) {
      const cached = getCachedFieldSnapshot(cacheKey)
      if (cached) {
        setFarmData(cached.farmData)
        setRecommendations(cached.recommendations)
      } else {
        alert('You are offline and this field has not been synced before. Reconnect once to build its digital twin.')
      }
      setLoading(false)
      return
    }

    try {
      const [weather, soil] = await Promise.all([fetchWeather(lat, lng), fetchSoil(lat, lng)])
      const ndvi = estimateNDVI(lat, soil.raw.soilMoisture)
      const data = { weather, soil, ndvi }
      setFarmData(data)

      const recs = await getFarmRecommendations({ lat, lon: lng, weather, soil, ndvi, farmRecord: record })
      setRecommendations(recs)

      cacheFieldSnapshot(cacheKey, { farmData: data, recommendations: recs })
    } catch (err) {
      console.error(err)
      // Fall back to any earlier cached snapshot for this field before
      // giving up entirely — keeps the app useful on flaky connections.
      const cached = getCachedFieldSnapshot(cacheKey)
      if (cached) {
        setFarmData(cached.farmData)
        setRecommendations(cached.recommendations)
      } else {
        alert('Could not fetch field data. Please check your connection and try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <OfflineBanner />
      <MapView onPointSelect={handleLocationSelect} selectedPoint={selectedPoint} />
      <DataSidebar
        selectedPoint={selectedPoint}
        loading={loading}
        farmData={farmData}
        farmRecord={farmRecord}
        recommendations={recommendations}
      />
    </div>
  )
}
