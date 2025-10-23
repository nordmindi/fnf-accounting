/**
 * TypeScript type definitions
 * Core types used throughout the application
 */

// Theme types
export type Theme = 'light' | 'dark' | 'auto';

// Language types
export type Language = 'en' | 'sv';

// User progress types
export interface UserProgress {
  nickname: string;
  language: Language;
  theme: Theme;
  totalXp: number;
  currentLevel: number;
  streak: number;
  badges: string[];
  dailyProgress: Record<string, string[]>;
  notes: Record<string, string>;
  lastActiveAt: string;
  notifications?: NotificationSettings;
  sounds?: SoundSettings;
}

// Notification settings
export interface NotificationSettings {
  enabled: boolean;
  morningEnabled: boolean;
  eveningEnabled: boolean;
  morningTime: string;
  eveningTime: string;
}

// Sound settings
export interface SoundSettings {
  enabled: boolean;
  volume: number;
  taskCompletion: boolean;
  levelUp: boolean;
  badgeUnlock: boolean;
}

// Task types
export interface Task {
  id: string;
  title: string;
  description: string;
  difficulty: 'easy' | 'medium' | 'hard';
  category: string;
  xp: number;
  unlockedAtLevel: number;
}

// Task completion
export interface TaskCompletion {
  taskId: string;
  xpEarned: number;
  newTotalXp: number;
  levelUp?: LevelUnlock;
  badgeUnlock?: Badge;
  streakUpdate?: number;
}

// Level unlock
export interface LevelUnlock {
  newLevel: number;
  newXp: number;
  unlockedTasks: Task[];
  unlockedBadge?: Badge;
}

// Badge types
export interface Badge {
  id: string;
  title: string;
  description: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  icon: string;
  unlockedAtLevel?: number;
}

// UI state types
export interface UIState {
  isOnboardingComplete: boolean;
  currentScreen: string;
  isLoading: boolean;
  error: string | null;
}

// API response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Navigation types
export type RootStackParamList = {
  Main: undefined;
  Onboarding: undefined;
  TaskDetail: { taskId: string };
  LevelUp: { level: number; xp: number };
};

export type MainTabParamList = {
  Home: undefined;
  Progress: undefined;
  Settings: undefined;
};

// Component prop types
export interface BaseComponentProps {
  style?: any;
  testID?: string;
}

// Form types
export interface FormField {
  value: string;
  error?: string;
  touched: boolean;
}

// Animation types
export interface AnimationConfig {
  duration: number;
  easing: string;
  delay?: number;
}
