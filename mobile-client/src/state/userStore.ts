/**
 * User state management with Zustand
 * Handles user progress, settings, and preferences
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { UserProgress, Language, Theme } from '@/config/types';
import { defaultUserProgress } from '@/config';

interface UserState {
  // User data
  progress: UserProgress;
  
  // Actions
  updateNickname: (nickname: string) => void;
  updateLanguage: (language: Language) => void;
  updateTheme: (theme: Theme) => void;
  resetProgress: () => void;
  exportData: () => string;
  
  // Migration
  migrateUserData: () => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      progress: defaultUserProgress,

      // Migration function to ensure all required fields exist
      migrateUserData: () => {
        const state = get();
        const needsMigration = !state.progress.notifications || !state.progress.sounds;
        
        if (needsMigration) {
          set((state) => ({
            progress: {
              ...state.progress,
              notifications: state.progress.notifications || defaultUserProgress.notifications!,
              sounds: state.progress.sounds || defaultUserProgress.sounds!,
              lastActiveAt: new Date().toISOString(),
            },
          }));
        }
      },

      updateNickname: (nickname: string) =>
        set((state) => ({
          progress: {
            ...state.progress,
            nickname,
            lastActiveAt: new Date().toISOString(),
          },
        })),

      updateLanguage: (language: Language) =>
        set((state) => ({
          progress: {
            ...state.progress,
            language,
            lastActiveAt: new Date().toISOString(),
          },
        })),

      updateTheme: (theme: Theme) =>
        set((state) => ({
          progress: {
            ...state.progress,
            theme,
            lastActiveAt: new Date().toISOString(),
          },
        })),

      resetProgress: () =>
        set(() => ({
          progress: {
            ...defaultUserProgress,
            lastActiveAt: new Date().toISOString(),
          },
        })),

      exportData: () => {
        const state = get();
        return JSON.stringify(state.progress, null, 2);
      },
    }),
    {
      name: 'user-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({ progress: state.progress }),
    }
  )
);
