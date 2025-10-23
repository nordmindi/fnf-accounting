/**
 * Home Screen
 * Main screen of the application
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTranslation } from 'react-i18next';
import { useAppTheme } from '@/theme/provider';
import { useTheme } from '@/hooks/useTheme';
import { spacing } from '@/config/spacing';
import { typography } from '@/config/typography';
import Card from '@/components/Card';
import Button from '@/components/Button';

const HomeScreen: React.FC = () => {
  const { t } = useTranslation();
  const theme = useAppTheme();
  const { isDark } = useTheme();
  
  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    content: {
      flex: 1,
      padding: spacing.screen.horizontal,
    },
    header: {
      paddingVertical: spacing.lg,
    },
    title: {
      ...typography.scale.h1,
      color: theme.colors.text,
      marginBottom: spacing.sm,
    },
    subtitle: {
      ...typography.scale.body,
      color: theme.colors.textSecondary,
    },
    card: {
      marginBottom: spacing.lg,
    },
    cardTitle: {
      ...typography.scale.h3,
      color: theme.colors.text,
      marginBottom: spacing.sm,
    },
    cardText: {
      ...typography.scale.body,
      color: theme.colors.textSecondary,
      marginBottom: spacing.md,
    },
    buttonContainer: {
      flexDirection: 'row',
      gap: spacing.md,
    },
  });
  
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>{t('screens.home.title')}</Text>
          <Text style={styles.subtitle}>{t('screens.home.subtitle')}</Text>
        </View>
        
        <Card style={styles.card}>
          <Text style={styles.cardTitle}>Welcome to Your App</Text>
          <Text style={styles.cardText}>
            This is a template built with React Native, Expo, and TypeScript.
            It includes a comprehensive design system, state management, and testing setup.
          </Text>
          <View style={styles.buttonContainer}>
            <Button
              title="Primary Action"
              onPress={() => console.log('Primary pressed')}
              variant="primary"
            />
            <Button
              title="Secondary"
              onPress={() => console.log('Secondary pressed')}
              variant="secondary"
            />
          </View>
        </Card>
        
        <Card style={styles.card}>
          <Text style={styles.cardTitle}>Theme System</Text>
          <Text style={styles.cardText}>
            Current theme: {isDark ? 'Dark' : 'Light'}
          </Text>
          <Text style={styles.cardText}>
            The app automatically adapts to your system theme preference.
          </Text>
        </Card>
        
        <Card style={styles.card}>
          <Text style={styles.cardTitle}>Features Included</Text>
          <Text style={styles.cardText}>
            • TypeScript with strict configuration{'\n'}
            • Comprehensive design system{'\n'}
            • State management with Zustand{'\n'}
            • Internationalization (i18n){'\n'}
            • Testing setup with Jest{'\n'}
            • Theme system (light/dark){'\n'}
            • Navigation with React Navigation{'\n'}
            • EAS Build configuration
          </Text>
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
};

export default HomeScreen;
