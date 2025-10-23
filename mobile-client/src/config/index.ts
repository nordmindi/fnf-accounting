/**
 * Configuration exports
 * Centralized export of all configuration modules
 */

export * from './colors';
export * from './typography';
export * from './spacing';
export * from './types';
export * from './environment';

// Default user progress
export const defaultUserProgress = {
  nickname: '',
  language: 'en' as const,
  theme: 'auto' as const,
  totalXp: 0,
  currentLevel: 1,
  streak: 0,
  badges: [],
  dailyProgress: {},
  notes: {},
  lastActiveAt: new Date().toISOString(),
  notifications: {
    enabled: true,
    morningEnabled: true,
    eveningEnabled: true,
    morningTime: '08:00',
    eveningTime: '20:00',
  },
  sounds: {
    enabled: true,
    volume: 0.7,
    taskCompletion: true,
    levelUp: true,
    badgeUnlock: true,
  },
};
