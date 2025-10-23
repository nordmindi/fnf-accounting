/**
 * Typography System
 * Consistent typography scale for all text elements
 */

export const typography = {
  // Font families
  fonts: {
    system: 'System',
    inter: 'Inter',
    poppins: 'Poppins',
  },
  
  // Font weights
  weights: {
    regular: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
  
  // Font sizes
  sizes: {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 28,
    '4xl': 32,
    '5xl': 36,
    '6xl': 48,
  },
  
  // Line heights
  lineHeights: {
    tight: 1.2,
    normal: 1.4,
    relaxed: 1.6,
    loose: 1.8,
  },
  
  // Typography scale
  scale: {
    // Display headings
    h1: {
      fontFamily: 'System',
      fontSize: 32,
      fontWeight: '700',
      lineHeight: 38,
    },
    h2: {
      fontFamily: 'System',
      fontSize: 24,
      fontWeight: '600',
      lineHeight: 30,
    },
    h3: {
      fontFamily: 'System',
      fontSize: 20,
      fontWeight: '600',
      lineHeight: 26,
    },
    
    // Body text
    body: {
      fontFamily: 'System',
      fontSize: 16,
      fontWeight: '400',
      lineHeight: 24,
    },
    bodyLarge: {
      fontFamily: 'System',
      fontSize: 18,
      fontWeight: '400',
      lineHeight: 26,
    },
    bodySmall: {
      fontFamily: 'System',
      fontSize: 14,
      fontWeight: '400',
      lineHeight: 20,
    },
    
    // UI elements
    button: {
      fontFamily: 'System',
      fontSize: 16,
      fontWeight: '600',
      lineHeight: 20,
    },
    buttonSmall: {
      fontFamily: 'System',
      fontSize: 14,
      fontWeight: '600',
      lineHeight: 18,
    },
    caption: {
      fontFamily: 'System',
      fontSize: 12,
      fontWeight: '500',
      lineHeight: 16,
    },
    
    // Special elements
    display: {
      fontFamily: 'System',
      fontSize: 36,
      fontWeight: '700',
      lineHeight: 42,
    },
  },
} as const;

export type TypographyScale = keyof typeof typography.scale;
