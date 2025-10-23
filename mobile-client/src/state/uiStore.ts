/**
 * UI state management with Zustand
 * Handles UI-specific state like onboarding, loading, and navigation
 */

import { create } from 'zustand';
import { UIState } from '@/config/types';

interface UIStore extends UIState {
  setOnboardingComplete: (complete: boolean) => void;
  setCurrentScreen: (screen: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

export const useUIStore = create<UIStore>((set) => ({
  isOnboardingComplete: false,
  currentScreen: 'Home',
  isLoading: false,
  error: null,

  setOnboardingComplete: (complete: boolean) =>
    set({ isOnboardingComplete: complete }),

  setCurrentScreen: (screen: string) =>
    set({ currentScreen: screen }),

  setLoading: (loading: boolean) =>
    set({ isLoading: loading }),

  setError: (error: string | null) =>
    set({ error }),

  clearError: () =>
    set({ error: null }),
}));
