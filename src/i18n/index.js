import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import mr from './locales/mr.json';

const resources = {
  en: { translation: en },
  mr: { translation: mr },
};

const getInitialLanguage = () => {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('sitaphal-lang');
    if (stored) {
      return stored;
    }
    if (navigator.language?.startsWith('mr')) {
      return 'mr';
    }
  }
  return 'en';
};

i18n.use(initReactI18next).init({
  resources,
  fallbackLng: 'en',
  lng: getInitialLanguage(),
  interpolation: { escapeValue: false },
});

if (typeof window !== 'undefined') {
  i18n.on('languageChanged', (lng) => {
    localStorage.setItem('sitaphal-lang', lng);
  });
}

export default i18n;
