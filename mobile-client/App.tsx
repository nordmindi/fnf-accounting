/**
 * Main App Component
 * Entry point of the application
 */

import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { useTranslation } from 'react-i18next';
import { Ionicons } from '@expo/vector-icons';

// Import screens
import FireScreen from '@/screens/FireScreen';
import HomeScreen from '@/screens/HomeScreen';
import BookedScreen from '@/screens/BookedScreen';
import ReportsScreen from '@/screens/ReportsScreen';
import SettingsScreen from '@/screens/SettingsScreen';

// Import state and theme
import { useUserStore, useUIStore } from '@/state';
import { useTheme } from '@/hooks/useTheme';
import { ThemeProvider } from '@/theme/provider';

// Import i18n
import '@/i18n';

// Import types
import { MainTabParamList } from '@/config/types';

const Tab = createBottomTabNavigator<MainTabParamList>();

function MainNavigator() {
  const { t } = useTranslation();
  const theme = useTheme();
  
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;
          
          if (route.name === 'Fire') {
            iconName = focused ? 'flame' : 'flame-outline';
          } else if (route.name === 'Bokfört') {
            iconName = focused ? 'receipt' : 'receipt-outline';
          } else if (route.name === 'Rapporter') {
            iconName = focused ? 'bar-chart' : 'bar-chart-outline';
          } else if (route.name === 'Inställningar') {
            iconName = focused ? 'settings' : 'settings-outline';
          } else {
            iconName = 'help-outline';
          }
          
          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#2DD4BF',
        tabBarInactiveTintColor: theme.isDark ? '#CBD5E1' : '#64748B',
        tabBarStyle: {
          backgroundColor: theme.isDark ? '#1E293B' : '#FFFFFF',
          borderTopColor: theme.isDark ? '#334155' : '#E2E8F0',
        },
        headerStyle: {
          backgroundColor: theme.isDark ? '#0F1724' : '#FFFFFF',
        },
        headerTintColor: theme.isDark ? '#F8FAFC' : '#0F1724',
      })}
    >
      <Tab.Screen 
        name="Fire" 
        component={FireScreen}
        options={{ title: 'Fire' }}
      />
      <Tab.Screen 
        name="Bokfört" 
        component={BookedScreen}
        options={{ title: 'Bokfört' }}
      />
      <Tab.Screen 
        name="Rapporter" 
        component={ReportsScreen}
        options={{ title: 'Rapporter' }}
      />
      <Tab.Screen 
        name="Inställningar" 
        component={SettingsScreen}
        options={{ title: 'Inställningar' }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  const { isOnboardingComplete } = useUIStore();
  const { progress, migrateUserData } = useUserStore();
  const { isDark } = useTheme();
  const resolvedThemeMode = isDark ? 'dark' : 'light';

  // Initialize app state
  useEffect(() => {
    // Migrate user data to ensure all required fields exist
    migrateUserData();
    
    // Check if user has completed onboarding
    if (progress.nickname && progress.nickname.length > 0) {
      useUIStore.getState().setOnboardingComplete(true);
    }
  }, [progress.nickname, migrateUserData]);

  return (
    <SafeAreaProvider>
      <ThemeProvider mode={resolvedThemeMode}>
        <NavigationContainer
          theme={{
            dark: isDark,
            colors: {
              primary: '#2DD4BF',
              background: isDark ? '#0F1724' : '#FFFFFF',
              card: isDark ? '#1E293B' : '#FFFFFF',
              text: isDark ? '#F8FAFC' : '#0F1724',
              border: isDark ? '#334155' : '#E2E8F0',
              notification: '#2DD4BF',
            },
          }}
        >
          <StatusBar style={isDark ? 'light' : 'dark'} />
          <MainNavigator />
        </NavigationContainer>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}
