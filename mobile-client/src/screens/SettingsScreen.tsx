/**
 * Settings Screen
 * User preferences and app settings
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  TextInput,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTranslation } from 'react-i18next';
import { useAppTheme } from '@/theme/provider';
import { useTheme } from '@/hooks/useTheme';
import { useUserStore } from '@/state';
import { spacing } from '@/config/spacing';
import { typography } from '@/config/typography';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { Language, Theme } from '@/config/types';

interface SettingsSection {
  title: string;
  items: SettingsItem[];
}

interface SettingsItem {
  id: string;
  title: string;
  subtitle?: string;
  type: 'switch' | 'select' | 'input' | 'button' | 'info';
  value?: any;
  onPress?: () => void;
  onValueChange?: (value: any) => void;
  options?: Array<{ label: string; value: any }>;
  placeholder?: string;
  secureTextEntry?: boolean;
}

const SettingsScreen: React.FC = () => {
  const { t, i18n } = useTranslation();
  const theme = useAppTheme();
  const { isDark } = useTheme();
  const { progress, updateNickname, updateLanguage, updateTheme } = useUserStore();
  
  const [nickname, setNickname] = useState(progress.nickname);
  const [isEditingNickname, setIsEditingNickname] = useState(false);

  const handleSaveNickname = () => {
    if (nickname.trim()) {
      updateNickname(nickname.trim());
      setIsEditingNickname(false);
    } else {
      Alert.alert('Error', 'Nickname cannot be empty');
    }
  };

  const handleLanguageChange = (language: Language) => {
    updateLanguage(language);
    i18n.changeLanguage(language);
  };

  const handleThemeChange = (theme: Theme) => {
    updateTheme(theme);
  };

  const handleExportData = () => {
    Alert.alert(
      'Export Data',
      'Your data will be exported as a JSON file. This includes your preferences and settings.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Export', 
          onPress: () => {
            // In a real implementation, this would trigger a file download
            Alert.alert('Success', 'Data exported successfully!');
          }
        },
      ]
    );
  };

  const handleResetData = () => {
    Alert.alert(
      'Reset All Data',
      'This will delete all your preferences and settings. This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Reset', 
          style: 'destructive',
          onPress: () => {
            // In a real implementation, this would reset all user data
            Alert.alert('Success', 'All data has been reset!');
          }
        },
      ]
    );
  };

  const settingsSections: SettingsSection[] = [
    {
      title: 'Profile',
      items: [
        {
          id: 'nickname',
          title: 'Nickname',
          subtitle: progress.nickname || 'Not set',
          type: 'input',
          value: nickname,
          onValueChange: setNickname,
          placeholder: 'Enter your nickname',
        },
      ],
    },
    {
      title: 'Appearance',
      items: [
        {
          id: 'language',
          title: 'Language',
          subtitle: progress.language === 'en' ? 'English' : 'Svenska',
          type: 'select',
          value: progress.language,
          onValueChange: handleLanguageChange,
          options: [
            { label: 'English', value: 'en' },
            { label: 'Svenska', value: 'sv' },
          ],
        },
        {
          id: 'theme',
          title: 'Theme',
          subtitle: progress.theme === 'auto' ? 'Auto' : progress.theme === 'light' ? 'Light' : 'Dark',
          type: 'select',
          value: progress.theme,
          onValueChange: handleThemeChange,
          options: [
            { label: 'Auto', value: 'auto' },
            { label: 'Light', value: 'light' },
            { label: 'Dark', value: 'dark' },
          ],
        },
      ],
    },
    {
      title: 'Notifications',
      items: [
        {
          id: 'notifications',
          title: 'Push Notifications',
          subtitle: 'Receive notifications about new bookings',
          type: 'switch',
          value: progress.notifications?.enabled ?? true,
          onValueChange: (value) => {
            // In a real implementation, this would update notification settings
            console.log('Notifications:', value);
          },
        },
        {
          id: 'morning_reminder',
          title: 'Morning Reminder',
          subtitle: 'Daily reminder at 8:00 AM',
          type: 'switch',
          value: progress.notifications?.morningEnabled ?? true,
          onValueChange: (value) => {
            console.log('Morning reminder:', value);
          },
        },
        {
          id: 'evening_reminder',
          title: 'Evening Reminder',
          subtitle: 'Daily reminder at 8:00 PM',
          type: 'switch',
          value: progress.notifications?.eveningEnabled ?? true,
          onValueChange: (value) => {
            console.log('Evening reminder:', value);
          },
        },
      ],
    },
    {
      title: 'Sounds',
      items: [
        {
          id: 'sounds_enabled',
          title: 'Sound Effects',
          subtitle: 'Play sounds for actions and notifications',
          type: 'switch',
          value: progress.sounds?.enabled ?? true,
          onValueChange: (value) => {
            console.log('Sounds enabled:', value);
          },
        },
        {
          id: 'task_completion',
          title: 'Task Completion',
          subtitle: 'Sound when expense is processed',
          type: 'switch',
          value: progress.sounds?.taskCompletion ?? true,
          onValueChange: (value) => {
            console.log('Task completion sound:', value);
          },
        },
      ],
    },
    {
      title: 'Data & Privacy',
      items: [
        {
          id: 'export_data',
          title: 'Export Data',
          subtitle: 'Download your data as JSON',
          type: 'button',
          onPress: handleExportData,
        },
        {
          id: 'reset_data',
          title: 'Reset All Data',
          subtitle: 'Delete all preferences and settings',
          type: 'button',
          onPress: handleResetData,
        },
      ],
    },
    {
      title: 'About',
      items: [
        {
          id: 'version',
          title: 'App Version',
          subtitle: '1.0.0',
          type: 'info',
        },
        {
          id: 'build',
          title: 'Build Number',
          subtitle: '1',
          type: 'info',
        },
      ],
    },
  ];

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
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: spacing.lg,
    },
    headerTitle: {
      ...typography.scale.h2,
      color: theme.colors.text,
      marginLeft: spacing.sm,
    },
    section: {
      marginBottom: spacing.xl,
    },
    sectionTitle: {
      ...typography.scale.h3,
      color: theme.colors.text,
      marginBottom: spacing.md,
      marginTop: spacing.lg,
    },
    settingItem: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: spacing.md,
      paddingHorizontal: spacing.lg,
      backgroundColor: theme.colors.surface,
      borderRadius: theme.radius.lg,
      marginBottom: spacing.sm,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    settingItemContent: {
      flex: 1,
    },
    settingTitle: {
      ...typography.scale.body,
      color: theme.colors.text,
      fontWeight: '500',
      marginBottom: spacing.xs,
    },
    settingSubtitle: {
      ...typography.scale.bodySmall,
      color: theme.colors.textSecondary,
    },
    settingAction: {
      marginLeft: spacing.md,
    },
    inputContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      marginTop: spacing.sm,
    },
    input: {
      flex: 1,
      ...typography.scale.body,
      color: theme.colors.text,
      paddingVertical: spacing.sm,
      paddingHorizontal: spacing.md,
      backgroundColor: theme.colors.background,
      borderRadius: theme.radius.md,
      borderWidth: 1,
      borderColor: theme.colors.border,
      marginRight: spacing.sm,
    },
    buttonContainer: {
      flexDirection: 'row',
      gap: spacing.sm,
    },
    saveButton: {
      paddingHorizontal: spacing.md,
      paddingVertical: spacing.sm,
    },
    cancelButton: {
      paddingHorizontal: spacing.md,
      paddingVertical: spacing.sm,
    },
    selectModal: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
    },
    selectContainer: {
      backgroundColor: theme.colors.surface,
      borderRadius: theme.radius.lg,
      padding: spacing.lg,
      margin: spacing.lg,
      maxWidth: 300,
      width: '100%',
    },
    selectTitle: {
      ...typography.scale.h3,
      color: theme.colors.text,
      marginBottom: spacing.lg,
      textAlign: 'center',
    },
    selectOption: {
      paddingVertical: spacing.md,
      paddingHorizontal: spacing.lg,
      borderRadius: theme.radius.md,
      marginBottom: spacing.sm,
      backgroundColor: theme.colors.background,
    },
    selectOptionActive: {
      backgroundColor: theme.brand.primary,
    },
    selectOptionText: {
      ...typography.scale.body,
      color: theme.colors.text,
      textAlign: 'center',
    },
    selectOptionTextActive: {
      color: theme.colors.background,
    },
    dangerButton: {
      backgroundColor: '#FF8A65',
    },
    dangerButtonText: {
      color: theme.colors.background,
    },
  });

  const renderSettingItem = (item: SettingsItem) => {
    switch (item.type) {
      case 'switch':
        return (
          <View style={styles.settingItem}>
            <View style={styles.settingItemContent}>
              <Text style={styles.settingTitle}>{item.title}</Text>
              {item.subtitle && (
                <Text style={styles.settingSubtitle}>{item.subtitle}</Text>
              )}
            </View>
            <View style={styles.settingAction}>
              <Switch
                value={item.value}
                onValueChange={item.onValueChange}
                trackColor={{ false: theme.colors.border, true: theme.brand.primary }}
                thumbColor={theme.colors.background}
              />
            </View>
          </View>
        );

      case 'input':
        if (item.id === 'nickname') {
          return (
            <View style={styles.settingItem}>
              <View style={styles.settingItemContent}>
                <Text style={styles.settingTitle}>{item.title}</Text>
                {!isEditingNickname ? (
                  <Text style={styles.settingSubtitle}>
                    {progress.nickname || 'Not set'}
                  </Text>
                ) : (
                  <View style={styles.inputContainer}>
                    <TextInput
                      style={styles.input}
                      value={nickname}
                      onChangeText={setNickname}
                      placeholder="Enter your nickname"
                      placeholderTextColor={theme.colors.textSecondary}
                      autoFocus
                    />
                    <View style={styles.buttonContainer}>
                      <TouchableOpacity
                        style={[styles.saveButton, { backgroundColor: theme.brand.primary }]}
                        onPress={handleSaveNickname}
                      >
                        <Text style={{ color: theme.colors.background, fontWeight: '600' }}>
                          Save
                        </Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={[styles.cancelButton, { backgroundColor: theme.colors.border }]}
                        onPress={() => {
                          setNickname(progress.nickname);
                          setIsEditingNickname(false);
                        }}
                      >
                        <Text style={{ color: theme.colors.text, fontWeight: '600' }}>
                          Cancel
                        </Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                )}
              </View>
              {!isEditingNickname && (
                <TouchableOpacity
                  style={styles.settingAction}
                  onPress={() => setIsEditingNickname(true)}
                >
                  <Ionicons name="pencil" size={20} color={theme.colors.text} />
                </TouchableOpacity>
              )}
            </View>
          );
        }
        return null;

      case 'select':
        return (
          <TouchableOpacity
            style={styles.settingItem}
            onPress={() => {
              // In a real implementation, this would show a modal with options
              Alert.alert(
                item.title,
                'Select an option',
                item.options?.map(option => ({
                  text: option.label,
                  onPress: () => item.onValueChange?.(option.value),
                })) || []
              );
            }}
          >
            <View style={styles.settingItemContent}>
              <Text style={styles.settingTitle}>{item.title}</Text>
              {item.subtitle && (
                <Text style={styles.settingSubtitle}>{item.subtitle}</Text>
              )}
            </View>
            <View style={styles.settingAction}>
              <Ionicons name="chevron-forward" size={20} color={theme.colors.textSecondary} />
            </View>
          </TouchableOpacity>
        );

      case 'button':
        const isDanger = item.id === 'reset_data';
        return (
          <TouchableOpacity
            style={[
              styles.settingItem,
              isDanger && { backgroundColor: '#FF8A65' },
            ]}
            onPress={item.onPress}
          >
            <View style={styles.settingItemContent}>
              <Text style={[
                styles.settingTitle,
                isDanger && { color: theme.colors.background },
              ]}>
                {item.title}
              </Text>
              {item.subtitle && (
                <Text style={[
                  styles.settingSubtitle,
                  isDanger && { color: theme.colors.background },
                ]}>
                  {item.subtitle}
                </Text>
              )}
            </View>
            <View style={styles.settingAction}>
              <Ionicons 
                name="chevron-forward" 
                size={20} 
                color={isDanger ? theme.colors.background : theme.colors.textSecondary} 
              />
            </View>
          </TouchableOpacity>
        );

      case 'info':
        return (
          <View style={styles.settingItem}>
            <View style={styles.settingItemContent}>
              <Text style={styles.settingTitle}>{item.title}</Text>
              {item.subtitle && (
                <Text style={styles.settingSubtitle}>{item.subtitle}</Text>
              )}
            </View>
          </View>
        );

      default:
        return null;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Ionicons 
            name="settings" 
            size={24} 
            color={theme.brand.primary} 
          />
          <Text style={styles.headerTitle}>Inställningar</Text>
        </View>

        {/* Settings Sections */}
        {settingsSections.map((section, sectionIndex) => (
          <View key={sectionIndex} style={styles.section}>
            <Text style={styles.sectionTitle}>{section.title}</Text>
            {section.items.map((item) => (
              <View key={item.id}>
                {renderSettingItem(item)}
              </View>
            ))}
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
};

export default SettingsScreen;
