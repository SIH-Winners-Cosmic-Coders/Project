import React, { useState, useEffect } from 'react'
import { ThumbsUp, ThumbsDown } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'
import {
  queueAction,
  isOnline,
  feedbackKey,
  getFeedbackForField,
  persistSyncedFeedback,
} from '../services/offlineSync'

export default function FeedbackForm({ selectedPoint, recommendations }) {
  const { t } = useLanguage()
  const [rating, setRating] = useState(null)
  const [comment, setComment] = useState('')
  const [status, setStatus] = useState(null) // 'saved' | 'queued'
  const [history, setHistory] = useState([])

  useEffect(() => {
    if (!selectedPoint) return
    setHistory(getFeedbackForField(selectedPoint.lat, selectedPoint.lng))
    setRating(null)
    setComment('')
    setStatus(null)
  }, [selectedPoint])

  if (!selectedPoint) return null

  const handleSubmit = (e) => {
    e.preventDefault()
    if (rating === null) return

    const payload = {
      fieldKey: feedbackKey(selectedPoint.lat, selectedPoint.lng),
      lat: selectedPoint.lat,
      lng: selectedPoint.lng,
      rating,
      comment,
      recommendedCrop: recommendations?.cropChoice ?? null,
      submittedAt: new Date().toISOString(),
    }

    const record = queueAction('feedback', payload)
    if (record.synced) {
      persistSyncedFeedback(record)
      setStatus('saved')
    } else {
      setStatus('queued')
    }
    setHistory((h) => [record, ...h])
    setComment('')
    setRating(null)
  }

  return (
    <div className="feedback-panel">
      <form onSubmit={handleSubmit} className="feedback-form">
        <p className="feedback-prompt">{t('feedbackPrompt')}</p>
        <div className="feedback-buttons">
          <button
            type="button"
            className={`feedback-btn ${rating === 'helpful' ? 'active' : ''}`}
            onClick={() => setRating('helpful')}
          >
            <ThumbsUp size={16} /> {t('feedbackHelpful')}
          </button>
          <button
            type="button"
            className={`feedback-btn ${rating === 'not_helpful' ? 'active not-helpful' : ''}`}
            onClick={() => setRating('not_helpful')}
          >
            <ThumbsDown size={16} /> {t('feedbackNotHelpful')}
          </button>
        </div>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder={t('feedbackCommentPlaceholder')}
          rows={3}
        />
        <button type="submit" className="feedback-submit" disabled={rating === null}>
          {t('feedbackSubmit')}
        </button>
        {status && (
          <p className={`feedback-status ${status}`}>
            {status === 'saved' ? t('feedbackThanks') : t('feedbackQueued')}
          </p>
        )}
      </form>

      <div className="feedback-history">
        <h5>{t('recentFeedback')}</h5>
        {history.length === 0 ? (
          <p className="instruction">{t('noFeedbackYet')}</p>
        ) : (
          <ul>
            {history.slice(0, 5).map((r) => (
              <li key={r.id} className={r.payload.rating === 'helpful' ? 'good' : 'bad'}>
                {r.payload.rating === 'helpful' ? <ThumbsUp size={13} /> : <ThumbsDown size={13} />}
                <span>{r.payload.comment || '—'}</span>
                {!r.synced && <em className="pending-tag">pending sync</em>}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
