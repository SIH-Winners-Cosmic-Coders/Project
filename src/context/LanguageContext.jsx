import React, { createContext, useContext, useState, useMemo, useCallback } from 'react'
import { translations, LANGUAGES } from '../i18n/translations'

const LanguageContext = createContext(null)

const STORAGE_KEY = 'annadata:lang'

export function LanguageProvider({ children }) {
  const [lang, setLangState] = useState(
    () => localStorage.getItem(STORAGE_KEY) || 'en'
  )

  const setLang = useCallback((code) => {
    setLangState(code)
    localStorage.setItem(STORAGE_KEY, code)
  }, [])

  // Falls back to English key-by-key so a partially-translated language
  // never shows a blank string.
  const t = useCallback(
    (key) => {
      const dict = translations[lang] || {}
      return dict[key] ?? translations.en[key] ?? key
    },
    [lang]
  )

  const value = useMemo(
    () => ({ lang, setLang, t, languages: LANGUAGES }),
    [lang, setLang, t]
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export function useLanguage() {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useLanguage must be used within a LanguageProvider')
  return ctx
}
