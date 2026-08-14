import React from 'react'
import { normalizeConfidence, getConfidenceColor } from '../utils/formatters'

// A small stamped-dial gauge, styled after the pressure/moisture dials on
// farm equipment — used instead of a plain percentage chip so confidence
// reads at a glance.
export default function ConfidenceGauge({ confidence, size = 46 }) {
  const value = normalizeConfidence(confidence)
  const color = getConfidenceColor(value)
  const radius = (size - 6) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - value / 100)

  return (
    <div className="gauge" style={{ width: size, height: size }} role="img" aria-label={`Confidence ${value}%`}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--gauge-track)"
          strokeWidth="4"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <span className="gauge-value" style={{ color }}>{value}</span>
    </div>
  )
}
