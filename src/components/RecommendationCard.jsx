import React from 'react'
import ConfidenceGauge from './ConfidenceGauge'
import { useLanguage } from '../context/LanguageContext'

export default function RecommendationCard({ title, icon, data, variant }) {
  const { t } = useLanguage()
  if (!data) return null

  return (
    <div className={`rec-card ${variant ? `rec-card--${variant}` : ''}`}>
      <div className="rec-card-header">
        <h5><span className="rec-icon">{icon}</span>{title}</h5>
        <ConfidenceGauge confidence={data.confidence} />
      </div>
      <p className="rec-action">{data.action}</p>
      <div className="rec-details">
        <div className="rec-costbenefit">
          <strong>{t('costBenefit')}:</strong> {data.costBenefit}
        </div>
        {data.influencingFactors?.length > 0 && (
          <div className="factors-list">
            <strong>{t('keyFactors')}:</strong>
            <ul>
              {data.influencingFactors.map((factor, index) => (
                <li key={index}>{factor}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
