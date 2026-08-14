import React, { useState } from 'react'
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet'
import axios from 'axios'
import L from 'leaflet'
import { useLanguage } from '../context/LanguageContext'

import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

let DefaultIcon = L.icon({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
  iconAnchor: [12, 41],
})
L.Marker.prototype.options.icon = DefaultIcon

function ChangeView({ center }) {
  const map = useMap()
  if (center) {
    map.flyTo(center, 14, { duration: 1.5 })
  }
  return null
}

function LocationMarker({ onPointSelect, selectedPoint }) {
  useMapEvents({
    click(e) {
      onPointSelect({ lat: e.latlng.lat, lng: e.latlng.lng })
    },
  })

  return selectedPoint ? <Marker position={[selectedPoint.lat, selectedPoint.lng]} /> : null
}

export default function MapView({ onPointSelect, selectedPoint }) {
  const { t } = useLanguage()
  const [searchQuery, setSearchQuery] = useState('')
  const [searching, setSearching] = useState(false)
  const [mapCenter, setMapCenter] = useState([20.5937, 78.9629]) // India center
  const [tileType, setTileType] = useState('street')

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    setSearching(true)
    try {
      const res = await axios.get('https://nominatim.openstreetmap.org/search', {
        params: { q: searchQuery, format: 'json', limit: 1 },
      })

      if (res.data && res.data.length > 0) {
        const { lat, lon } = res.data[0]
        const newLat = parseFloat(lat)
        const newLng = parseFloat(lon)
        setMapCenter([newLat, newLng])
        onPointSelect({ lat: newLat, lng: newLng })
      } else {
        alert('Location not found. Please check the spelling and try again.')
      }
    } catch (err) {
      console.error(err)
      alert('Search failed. Check your connection and try again.')
    } finally {
      setSearching(false)
    }
  }

  return (
    <div style={{ position: 'relative', width: '100%', height: '100vh' }}>
      <div className="search-box">
        <form onSubmit={handleSearch}>
          <input
            type="text"
            placeholder={t('searchPlaceholder')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit" disabled={searching}>
            {searching ? '…' : `🔍 ${t('search')}`}
          </button>
        </form>

        <div className="map-toggle">
          <button className={tileType === 'street' ? 'active' : ''} onClick={() => setTileType('street')}>
            🗺️ {t('streetView')}
          </button>
          <button className={tileType === 'satellite' ? 'active' : ''} onClick={() => setTileType('satellite')}>
            🛰️ {t('satelliteView')}
          </button>
        </div>
      </div>

      <MapContainer center={mapCenter} zoom={5} style={{ width: '100%', height: '100%' }}>
        <ChangeView center={selectedPoint ? [selectedPoint.lat, selectedPoint.lng] : mapCenter} />

        {tileType === 'street' ? (
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            maxZoom={19}
          />
        ) : (
          <TileLayer
            attribution='Tiles &copy; Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            maxZoom={18}
          />
        )}

        <LocationMarker onPointSelect={onPointSelect} selectedPoint={selectedPoint} />
      </MapContainer>
    </div>
  )
}
