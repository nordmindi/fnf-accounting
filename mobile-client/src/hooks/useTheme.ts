/**
 * Custom hook for theme management
 * Handles user theme preferences and system theme detection
 */

import { useColorScheme } from 'react-native';
import { useUserStore } from '@/state';

export const useTheme = () => {
  const { progress } = useUserStore();
  const systemColorScheme = useColorScheme();
  
  // Determine theme based on user preference
  const getIsDark = () => {
    switch (progress.theme) {
      case 'light':
        return false;
      case 'dark':
        return true;
      case 'auto':
      default:
        return systemColorScheme === 'dark';
    }
  };
  
  const isDark = getIsDark();
  
  return {
    isDark,
    theme: progress.theme,
    systemColorScheme,
  };
};
