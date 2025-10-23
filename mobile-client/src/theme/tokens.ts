import { colors } from '@/config/colors';
import { spacing } from '@/config/spacing';
import { typography } from '@/config/typography';

export type ThemeMode = 'light' | 'dark';

export const tokens = {
  colors: {
    light: colors.light,
    dark: colors.dark,
    brand: {
      primary: colors.primary,
      secondary: colors.secondary,
      accent: colors.accent,
      gray: {
        100: colors.gray100,
        200: colors.gray200,
        300: colors.gray300,
        400: colors.gray400,
        500: colors.gray500,
        600: colors.gray600,
        700: colors.gray700,
        800: colors.gray800,
        900: colors.gray900,
      },
    },
  },
  spacing,
  radius: {
    sm: 6,
    md: 10,
    lg: 14,
    round: 999,
  },
  elevation: {
    card: 3,
    modal: 5,
  },
  typography: typography.scale,
  motion: {
    duration: { fast: 200, medium: 400, slow: 800 },
    easing: { standard: 'ease-in-out' },
  },
  opacity: { overlay: 0.5, disabled: 0.4, subtle: 0.08 },
  components: {
    card: { padding: spacing.lg },
    button: { minHeight: spacing.touchTarget },
    progress: { height: 8 },
    chip: { paddingX: spacing.md, paddingY: spacing.xs },
  },
} as const;

export const getTheme = (mode: ThemeMode) => ({
  mode,
  colors: mode === 'dark' ? tokens.colors.dark : tokens.colors.light,
  brand: tokens.colors.brand,
  spacing: tokens.spacing,
  radius: tokens.radius,
  elevation: tokens.elevation,
  typography: tokens.typography,
  motion: tokens.motion,
  opacity: tokens.opacity,
  components: tokens.components,
});

export type AppTheme = ReturnType<typeof getTheme>;
