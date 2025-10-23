/**
 * Reusable Card component with consistent styling
 */

import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { useAppTheme } from '@/theme/provider';

interface CardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  variant?: 'default' | 'elevated' | 'outlined';
}

const Card: React.FC<CardProps> = ({ 
  children, 
  style, 
  variant = 'default' 
}) => {
  const theme = useAppTheme();
  
  const getCardStyle = (): ViewStyle => {
    const baseStyle: ViewStyle = {
      backgroundColor: theme.colors.surface,
      borderRadius: theme.radius.lg,
      padding: theme.components.card.padding,
    };
    
    const variantStyles = {
      default: {
        borderWidth: 1,
        borderColor: theme.colors.border,
      },
      elevated: {
        ...theme.spacing.shadow.md,
        borderWidth: 0,
      },
      outlined: {
        borderWidth: 2,
        borderColor: theme.brand.primary,
      },
    };
    
    return {
      ...baseStyle,
      ...variantStyles[variant],
    };
  };
  
  return (
    <View style={[getCardStyle(), style]}>
      {children}
    </View>
  );
};

export default Card;
