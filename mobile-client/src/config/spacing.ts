/**
 * Spacing System
 * Consistent spacing scale for margins, padding, and layout
 */

export const spacing = {
  // Base spacing unit (4px)
  unit: 4,
  
  // Spacing scale
  xs: 4,    // 4px
  sm: 8,    // 8px
  md: 12,   // 12px
  lg: 16,   // 16px
  xl: 20,   // 20px
  '2xl': 24, // 24px
  '3xl': 32, // 32px
  '4xl': 40, // 40px
  '5xl': 48, // 48px
  '6xl': 64, // 64px
  '7xl': 80, // 80px
  '8xl': 96, // 96px
  
  // Semantic spacing
  screen: {
    horizontal: 20, // Screen horizontal padding
    vertical: 24,   // Screen vertical padding
  },
  
  component: {
    padding: 16,    // Standard component padding
    margin: 12,     // Standard component margin
    gap: 12,        // Standard gap between elements
  },
  
  // Touch targets (accessibility)
  touchTarget: 44, // Minimum touch target size
  
  // Border radius
  radius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
    '2xl': 20,
    full: 9999,
  },
  
  // Shadows
  shadow: {
    sm: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.1,
      shadowRadius: 2,
      elevation: 2,
    },
    md: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.15,
      shadowRadius: 4,
      elevation: 4,
    },
    lg: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.2,
      shadowRadius: 8,
      elevation: 8,
    },
  },
} as const;

export type SpacingKey = keyof typeof spacing;
