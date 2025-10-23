/**
 * Reusable Button component with consistent styling
 */

import React, { useRef } from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
  ActivityIndicator,
  Animated,
} from 'react-native';
import { typography } from '@/config/typography';
import { spacing } from '@/config/spacing';
import { useAppTheme } from '@/theme/provider';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  style,
  textStyle,
}) => {
  const theme = useAppTheme();
  const scaleAnim = useRef(new Animated.Value(1)).current;
  
  const handlePressIn = () => {
    if (!disabled && !loading) {
      Animated.spring(scaleAnim, {
        toValue: 0.95,
        tension: 300,
        friction: 10,
        useNativeDriver: true,
      }).start();
    }
  };
  
  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      tension: 300,
      friction: 10,
      useNativeDriver: true,
    }).start();
  };
  
  const getButtonStyle = (): ViewStyle => {
    const baseStyle: ViewStyle = {
      borderRadius: theme.radius.md,
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'row',
      opacity: disabled ? theme.opacity.disabled : 1,
    };
    
    // Size styles
    const sizeStyles = {
      small: {
        paddingHorizontal: spacing.md,
        paddingVertical: spacing.sm,
        minHeight: 36,
      },
      medium: {
        paddingHorizontal: spacing.lg,
        paddingVertical: spacing.md,
        minHeight: 44,
      },
      large: {
        paddingHorizontal: spacing.xl,
        paddingVertical: spacing.lg,
        minHeight: 52,
      },
    };
    
    // Variant styles
    const variantStyles = {
      primary: {
        backgroundColor: theme.brand.primary,
        borderWidth: 0,
      },
      secondary: {
        backgroundColor: theme.colors.surface,
        borderWidth: 1,
        borderColor: theme.colors.border,
      },
      outline: {
        backgroundColor: 'transparent',
        borderWidth: 1,
        borderColor: theme.brand.primary,
      },
      ghost: {
        backgroundColor: 'transparent',
        borderWidth: 0,
      },
    };
    
    return {
      ...baseStyle,
      ...sizeStyles[size],
      ...variantStyles[variant],
    };
  };
  
  const getTextStyle = (): TextStyle => {
    const baseStyle: TextStyle = {
      ...typography.scale.button,
      textAlign: 'center',
    };
    
    // Size text styles
    const sizeTextStyles = {
      small: typography.scale.buttonSmall,
      medium: typography.scale.button,
      large: typography.scale.bodyLarge,
    };
    
    // Variant text styles
    const variantTextStyles = {
      primary: { color: theme.colors.background },
      secondary: { color: theme.colors.text },
      outline: { color: theme.brand.primary },
      ghost: { color: theme.colors.text },
    };
    
    return {
      ...baseStyle,
      ...sizeTextStyles[size],
      ...variantTextStyles[variant],
    };
  };
  
  return (
    <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
      <TouchableOpacity
        style={[getButtonStyle(), style]}
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        disabled={disabled || loading}
        activeOpacity={0.8}
      >
        {loading ? (
          <ActivityIndicator
            size="small"
            color={variant === 'primary' ? theme.colors.background : theme.brand.primary}
          />
        ) : (
          <Text style={[getTextStyle(), textStyle]}>{title}</Text>
        )}
      </TouchableOpacity>
    </Animated.View>
  );
};

export default Button;
