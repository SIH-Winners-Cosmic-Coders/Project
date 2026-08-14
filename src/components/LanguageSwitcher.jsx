import React from 'react'
import { useLanguage } from '../context/LanguageContext'

export default function LanguageSwitcher() {
  const { lang, setLang, languages } = useLanguage()

  return (
    <select
      className="lang-switcher"
      value={lang}
      onChange={(e) => setLang(e.target.value)}
      aria-label="Choose language"
    >
      {languages.map((l) => (
        <option key={l.code} value={l.code}>
          {l.native}
        </option>
      ))}
    </select>
  )
}
