import React, { useEffect, useState } from 'react'
import { useLanguage } from '../context/LanguageContext'
import { flushQueue, isOnline } from '../services/offlineSync'

export default function OfflineBanner() {
  const { t } = useLanguage()
  const [online, setOnline] = useState(isOnline())
  const [justSynced, setJustSynced] = useState(false)

  useEffect(() => {
    function handleOnline() {
      setOnline(true)
      const synced = flushQueue()
      if (synced.length > 0) {
        setJustSynced(true)
        setTimeout(() => setJustSynced(false), 4000)
      }
    }
    function handleOffline() {
      setOnline(false)
    }
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  if (online && !justSynced) return null

  return (
    <div className={`offline-banner ${!online ? 'offline-banner--offline' : 'offline-banner--synced'}`}>
      {!online ? t('offlineBanner') : t('backOnline')}
    </div>
  )
}
