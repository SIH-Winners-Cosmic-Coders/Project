import React, { useState, useEffect } from 'react'
import { Sprout, Droplets, FlaskConical, ShieldAlert, Satellite } from 'lucide-react'
import RecommendationCard from './RecommendationCard'
import FeedbackForm from './FeedbackForm'
import LanguageSwitcher from './LanguageSwitcher'
import { useLanguage } from '../context/LanguageContext'
import { formatCoordinates } from '../utils/formatters'

export default function DataSidebar({
  selectedPoint,
  loading,
  farmData,
  farmRecord,
  recommendations,
}) {
  const { t } = useLanguage()
  const [tab, setTab] = useState('data')

  // Recommendations arriving is the natural moment to jump the farmer to
  // that tab, without forcing it every re-render.
  useEffect(() => {
    if (recommendations) setTab('recommendations')
  }, [recommendations])

  useEffect(() => {
    if (selectedPoint) setTab(recommendations ? 'recommendations' : 'data')
  }, [selectedPoint])

  return (
    <div className="sidebar">
      <div className="sidebar-top">
        <div className="brand">
          <h2>🌾 AnnaDATA</h2>
          <p className="tagline">{t('tagline')}</p>
        </div>
        <LanguageSwitcher />
      </div>

      {!selectedPoint && <p className="instruction">{t('instruction')}</p>}

      {selectedPoint && (
        <>
          <h3 className="coord-line">
            📍 {t('coordinates')}: {formatCoordinates(selectedPoint.lat, selectedPoint.lng)}
          </h3>

          {loading && <div className="loader">⏳ {t('syncing')}</div>}

          {!loading && (farmData || recommendations) && (
            <div className="tabs">
              <button className={tab === 'data' ? 'active' : ''} onClick={() => setTab('data')}>
                {t('tabData')}
              </button>
              <button
                className={tab === 'recommendations' ? 'active' : ''}
                onClick={() => setTab('recommendations')}
                disabled={!recommendations}
              >
                {t('tabRecommendations')}
              </button>
              <button className={tab === 'feedback' ? 'active' : ''} onClick={() => setTab('feedback')}>
                {t('tabFeedback')}
              </button>
            </div>
          )}

          {!loading && tab === 'data' && farmData && (
            <div className="data-section">
              <h4>{t('envMetrics')}</h4>
              <ul className="metrics-list">
                <li><span>{t('temperature')}</span><b>{farmData.weather.temperature}</b></li>
                <li><span>{t('humidity')}</span><b>{farmData.weather.humidity}</b></li>
                <li><span>{t('rainfall')}</span><b>{farmData.weather.precipitation}</b></li>
                <li><span>{t('windSpeed')}</span><b>{farmData.weather.windSpeed}</b></li>
                <li><span>{t('soilTemp')}</span><b>{farmData.soil.soilTemp}</b></li>
                <li><span>{t('soilMoisture')}</span><b>{farmData.soil.soilMoisture}</b></li>
                <li>
                  <span><Satellite size={13} style={{ verticalAlign: '-2px' }} /> {t('ndvi')}</span>
                  <b>{farmData.ndvi.value} — {farmData.ndvi.label}</b>
                </li>
              </ul>

              {farmRecord && (
                <>
                  <h4>{t('farmRecord')}</h4>
                  <ul className="metrics-list">
                    <li><span>{t('cropStage')}</span><b>{farmRecord.cropStage}</b></li>
                    <li><span>{t('lastIrrigation')}</span><b>{farmRecord.lastIrrigationDate}</b></li>
                    <li><span>{t('soilType')}</span><b>{farmRecord.soilType}</b></li>
                    <li><span>{t('historicalYield')}</span><b>{farmRecord.farmerHistoricalYield}</b></li>
                  </ul>
                </>
              )}
            </div>
          )}

          {!loading && tab === 'recommendations' && recommendations && (
            <div className="recommendations-section">
              <p className="rec-headline">
                🌱 <strong>{t('recommendedCrop')}:</strong> {recommendations.cropChoice}
              </p>
              {recommendations.engine !== 'Gemini' && (
                <p className="ai-fallback-note">{t('aiUnavailable')}</p>
              )}

              <RecommendationCard
                title={t('soilHealth')}
                icon={<Sprout size={15} />}
                data={recommendations.soilHealthImprovement}
                variant="soil"
              />
              <RecommendationCard
                title={t('irrigation')}
                icon={<Droplets size={15} />}
                data={recommendations.irrigation}
              />
              <RecommendationCard
                title={t('nutrients')}
                icon={<FlaskConical size={15} />}
                data={recommendations.nutrientApplication}
              />
              <RecommendationCard
                title={t('riskMitigation')}
                icon={<ShieldAlert size={15} />}
                data={recommendations.riskMitigation}
              />
            </div>
          )}

          {!loading && tab === 'feedback' && (
            <FeedbackForm selectedPoint={selectedPoint} recommendations={recommendations} />
          )}
        </>
      )}
    </div>
  )
}
