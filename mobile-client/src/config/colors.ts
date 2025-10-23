/**
 * Color Palette
 * Based on modern design principles with theme support
 */

export const colors = {
  // Primary brand colors
  primary: '#2DD4BF',     // Teal - primary actions
  secondary: '#FF8A65',   // Coral - secondary actions
  accent: '#FFD166',      // Gold - highlights and rewards
  
  // Neutral colors
  navy: '#0F1724',        // Deep Navy - backgrounds
  slate: '#E6EEF4',       // Soft Slate - muted surfaces
  
  // Semantic colors
  success: '#2DD4BF',     // Teal for success states
  warning: '#FFD166',     // Gold for warnings
  error: '#FF8A65',       // Coral for errors
  info: '#2DD4BF',        // Teal for informational content
  
  // Neutral grays
  white: '#FFFFFF',
  gray50: '#F8FAFC',
  gray100: '#F1F5F9',
  gray200: '#E2E8F0',
  gray300: '#CBD5E1',
  gray400: '#94A3B8',
  gray500: '#64748B',
  gray600: '#475569',
  gray700: '#334155',
  gray800: '#1E293B',
  gray900: '#0F172A',
  
  // Theme variants
  dark: {
    background: '#0F1724',
    surface: '#1E293B',
    text: '#F8FAFC',
    textSecondary: '#CBD5E1',
    border: '#334155',
  },
  
  light: {
    background: '#FFFFFF',
    surface: '#F8FAFC',
    text: '#0F1724',
    textSecondary: '#475569',
    border: '#E2E8F0',
  },
} as const;

export type ColorKey = keyof typeof colors;
export type ThemeColors = typeof colors.light | typeof colors.dark;
