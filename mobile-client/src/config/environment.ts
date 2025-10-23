/**
 * Environment Configuration
 * Centralized configuration for different environments
 */

export const config = {
  // App information
  appName: 'Fire & Forget Accounting',
  version: '1.0.0',
  buildNumber: '1',
  
  // Environment
  isDev: __DEV__,
  isProduction: !__DEV__,
  
  // API configuration
  apiUrl: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',
  apiTimeout: 10000,
  
  // Feature flags
  features: {
    notifications: true,
    sounds: true,
    analytics: !__DEV__,
    crashReporting: !__DEV__,
  },
  
  // Storage keys
  storage: {
    userProgress: 'user_progress',
    settings: 'app_settings',
    cache: 'app_cache',
  },
  
  // Animation settings
  animation: {
    duration: {
      fast: 200,
      medium: 400,
      slow: 800,
    },
    easing: 'ease-in-out',
  },
  
  // Pagination
  pagination: {
    defaultPageSize: 20,
    maxPageSize: 100,
  },
  
  // Validation
  validation: {
    nickname: {
      minLength: 1,
      maxLength: 50,
    },
    email: {
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    },
  },
} as const;

export type Config = typeof config;
