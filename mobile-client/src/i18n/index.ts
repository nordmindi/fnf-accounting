/**
 * Internationalization setup
 * Configure i18next for multi-language support
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import 'intl-pluralrules';

// Import translation files
import en from './en.json';
import sv from './sv.json';

const resources = {
  en: {
    translation: en,
  },
  sv: {
    translation: sv,
  },
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en', // Default language
    fallbackLng: 'en',
    
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    
    // Enable pluralization
    pluralSeparator: '_',
    contextSeparator: '_',
    
    // Development options
    debug: __DEV__,
    
    // React options
    react: {
      useSuspense: false,
    },
  });

export default i18n;
