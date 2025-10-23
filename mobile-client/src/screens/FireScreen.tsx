/**
 * Fire Screen - Main NLP interface for Fire & Forget Accounting
 * Allows users to input expenses in natural language
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTranslation } from 'react-i18next';
import { useAppTheme } from '@/theme/provider';
import { useTheme } from '@/hooks/useTheme';
import { spacing } from '@/config/spacing';
import { typography } from '@/config/typography';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { apiService, NaturalLanguageResponse, ActivityItem } from '@/services/apiService';

const FireScreen: React.FC = () => {
  const { t } = useTranslation();
  const theme = useAppTheme();
  const { isDark } = useTheme();
  
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastResponse, setLastResponse] = useState<NaturalLanguageResponse | null>(null);
  const [activityFeed, setActivityFeed] = useState<ActivityItem[]>([]);
  const [isLoadingActivity, setIsLoadingActivity] = useState(false);

  // Mock company ID for testing
  const companyId = '123e4567-e89b-12d3-a456-426614174007';

  useEffect(() => {
    loadActivityFeed();
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      const response = await apiService.getTestToken();
      if (response.success && response.data) {
        apiService.setAuthToken(response.data.access_token);
      }
    } catch (error) {
      console.error('Failed to initialize auth:', error);
    }
  };

  const loadActivityFeed = async () => {
    setIsLoadingActivity(true);
    try {
      const response = await apiService.getActivityFeed(companyId);
      if (response.success && response.data) {
        setActivityFeed(response.data);
      }
    } catch (error) {
      console.error('Failed to load activity feed:', error);
    } finally {
      setIsLoadingActivity(false);
    }
  };

  const handleSubmit = async () => {
    if (!inputText.trim()) {
      Alert.alert('Error', 'Please enter a description of your expense');
      return;
    }

    setIsProcessing(true);
    try {
      const response = await apiService.processNaturalLanguage({
        text: inputText,
        company_id: companyId,
      });

      if (response.success && response.data) {
        setLastResponse(response.data);
        setInputText('');
        
        // Reload activity feed to show new booking
        await loadActivityFeed();
        
        // Show success message
        Alert.alert(
          'Success!',
          response.data.message,
          [{ text: 'OK' }]
        );
      } else {
        Alert.alert('Error', response.error || 'Failed to process expense');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCameraPress = () => {
    Alert.alert(
      'Camera',
      'Camera functionality will be implemented in the next version',
      [{ text: 'OK' }]
    );
  };

  const handleAttachmentPress = () => {
    Alert.alert(
      'Attachment',
      'File attachment functionality will be implemented in the next version',
      [{ text: 'OK' }]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return '#2DD4BF';
      case 'warning':
        return '#FFD166';
      case 'error':
        return '#FF8A65';
      case 'info':
      default:
        return '#2DD4BF';
    }
  };

  const getStatusIcon = (type: string) => {
    switch (type) {
      case 'booking':
        return 'receipt-outline';
      case 'notification':
        return 'notifications-outline';
      case 'reminder':
        return 'time-outline';
      default:
        return 'information-circle-outline';
    }
  };

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
      justifyContent: 'space-between',
      paddingVertical: spacing.lg,
    },
    headerLeft: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    flameIcon: {
      marginRight: spacing.sm,
    },
    headerTitle: {
      ...typography.scale.h2,
      color: theme.colors.text,
    },
    profileContainer: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    profileImage: {
      width: 40,
      height: 40,
      borderRadius: 20,
      backgroundColor: theme.brand.primary,
      alignItems: 'center',
      justifyContent: 'center',
    },
    profileInitial: {
      ...typography.scale.body,
      color: theme.colors.background,
      fontWeight: '600',
    },
    statusIndicator: {
      position: 'absolute',
      bottom: 0,
      right: 0,
      width: 12,
      height: 12,
      borderRadius: 6,
      backgroundColor: '#2DD4BF',
      borderWidth: 2,
      borderColor: theme.colors.background,
    },
    successCard: {
      backgroundColor: '#2DD4BF',
      marginBottom: spacing.lg,
    },
    successCardContent: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    successText: {
      flex: 1,
    },
    successTitle: {
      ...typography.scale.body,
      color: theme.colors.background,
      fontWeight: '600',
      marginBottom: spacing.xs,
    },
    successDescription: {
      ...typography.scale.bodySmall,
      color: theme.colors.background,
    },
    systemIndicator: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    systemText: {
      ...typography.scale.caption,
      color: theme.colors.background,
      marginRight: spacing.xs,
    },
    sectionTitle: {
      ...typography.scale.h3,
      color: theme.colors.text,
      marginBottom: spacing.md,
    },
    activityItem: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: spacing.md,
    },
    activityIcon: {
      width: 40,
      height: 40,
      borderRadius: 20,
      alignItems: 'center',
      justifyContent: 'center',
      marginRight: spacing.md,
    },
    activityContent: {
      flex: 1,
    },
    activityTitle: {
      ...typography.scale.body,
      color: theme.colors.text,
      fontWeight: '500',
    },
    activityDescription: {
      ...typography.scale.bodySmall,
      color: theme.colors.textSecondary,
      marginTop: spacing.xs,
    },
    activityAmount: {
      ...typography.scale.body,
      color: theme.colors.text,
      fontWeight: '600',
    },
    inputContainer: {
      backgroundColor: theme.colors.surface,
      borderRadius: theme.radius.lg,
      padding: spacing.lg,
      marginBottom: spacing.lg,
    },
    inputLabel: {
      ...typography.scale.body,
      color: theme.colors.text,
      marginBottom: spacing.sm,
    },
    inputRow: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    textInput: {
      flex: 1,
      ...typography.scale.body,
      color: theme.colors.text,
      paddingVertical: spacing.md,
      paddingHorizontal: spacing.lg,
      backgroundColor: theme.colors.background,
      borderRadius: theme.radius.md,
      borderWidth: 1,
      borderColor: theme.colors.border,
      marginRight: spacing.sm,
    },
    actionButtons: {
      flexDirection: 'row',
      gap: spacing.sm,
    },
    actionButton: {
      width: 44,
      height: 44,
      borderRadius: 22,
      backgroundColor: theme.colors.surface,
      alignItems: 'center',
      justifyContent: 'center',
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    submitButton: {
      marginTop: spacing.lg,
    },
  });

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.headerLeft}>
              <Ionicons 
                name="flame" 
                size={24} 
                color={theme.brand.primary} 
                style={styles.flameIcon}
              />
              <Text style={styles.headerTitle}>Fire & Forget Accounting</Text>
            </View>
            <View style={styles.profileContainer}>
              <View style={styles.profileImage}>
                <Text style={styles.profileInitial}>JD</Text>
                <View style={styles.statusIndicator} />
              </View>
            </View>
          </View>

          {/* Success Message */}
          {lastResponse && (
            <Card style={styles.successCard}>
              <View style={styles.successCardContent}>
                <View style={styles.successText}>
                  <Text style={styles.successTitle}>Booking created successfully!</Text>
                  <Text style={styles.successDescription}>
                    {lastResponse.booking_details?.total_amount} {lastResponse.booking_details?.currency} has been automatically booked.
                  </Text>
                </View>
                <View style={styles.systemIndicator}>
                  <Text style={styles.systemText}>System:</Text>
                  <Ionicons name="checkmark" size={16} color={theme.colors.background} />
                </View>
              </View>
            </Card>
          )}

          {/* Activity Feed */}
          <Text style={styles.sectionTitle}>Activity Feed</Text>
          {isLoadingActivity ? (
            <ActivityIndicator size="small" color={theme.brand.primary} />
          ) : (
            activityFeed.slice(0, 3).map((item) => (
              <Card key={item.id} style={{ marginBottom: spacing.md }}>
                <View style={styles.activityItem}>
                  <View style={[
                    styles.activityIcon,
                    { backgroundColor: getStatusColor(item.status) }
                  ]}>
                    <Ionicons 
                      name={getStatusIcon(item.type) as any} 
                      size={20} 
                      color={theme.colors.background} 
                    />
                  </View>
                  <View style={styles.activityContent}>
                    <Text style={styles.activityTitle}>{item.title}</Text>
                    <Text style={styles.activityDescription}>{item.description}</Text>
                  </View>
                  {item.amount && (
                    <Text style={styles.activityAmount}>
                      {item.amount} {item.currency}
                    </Text>
                  )}
                </View>
              </Card>
            ))
          )}

          {/* System Notification */}
          <Text style={styles.sectionTitle}>System Notification</Text>
          <Card style={{ marginBottom: spacing.lg }}>
            <View style={styles.activityItem}>
              <View style={[
                styles.activityIcon,
                { backgroundColor: '#2DD4BF' }
              ]}>
                <Ionicons 
                  name="time-outline" 
                  size={20} 
                  color={theme.colors.background} 
                />
              </View>
              <View style={styles.activityContent}>
                <Text style={styles.activityTitle}>Reminder: Payroll for May due in 3 days</Text>
              </View>
            </View>
          </Card>

          {/* NLP Input */}
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Message / Scan / Describe expense...</Text>
            <View style={styles.inputRow}>
              <TextInput
                style={styles.textInput}
                value={inputText}
                onChangeText={setInputText}
                placeholder="Business lunch with clients today, 3 people - 1500 SEK"
                placeholderTextColor={theme.colors.textSecondary}
                multiline
                maxLength={500}
              />
              <View style={styles.actionButtons}>
                <TouchableOpacity 
                  style={styles.actionButton}
                  onPress={handleCameraPress}
                >
                  <Ionicons name="camera-outline" size={20} color={theme.colors.text} />
                </TouchableOpacity>
                <TouchableOpacity 
                  style={styles.actionButton}
                  onPress={handleAttachmentPress}
                >
                  <Ionicons name="attach-outline" size={20} color={theme.colors.text} />
                </TouchableOpacity>
              </View>
            </View>
            <Button
              title={isProcessing ? "Processing..." : "Submit Expense"}
              onPress={handleSubmit}
              variant="primary"
              size="large"
              loading={isProcessing}
              disabled={!inputText.trim() || isProcessing}
              style={styles.submitButton}
            />
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

export default FireScreen;
