/**
 * Reports Screen
 * Financial analytics and reporting dashboard
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Alert,
  Dimensions,
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
import { apiService, BookingDetails } from '@/services/apiService';

interface ReportData {
  totalExpenses: number;
  totalBookings: number;
  averageExpense: number;
  monthlyTrend: number;
  topCategories: Array<{
    category: string;
    amount: number;
    percentage: number;
  }>;
  recentActivity: BookingDetails[];
  monthlyBreakdown: Array<{
    month: string;
    amount: number;
    bookings: number;
  }>;
}

interface TimeRange {
  label: string;
  value: 'week' | 'month' | 'quarter' | 'year';
}

const { width } = Dimensions.get('window');

const ReportsScreen: React.FC = () => {
  const { t } = useTranslation();
  const theme = useAppTheme();
  const { isDark } = useTheme();
  
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState<TimeRange['value']>('month');
  const [selectedView, setSelectedView] = useState<'overview' | 'categories' | 'trends'>('overview');

  const timeRanges: TimeRange[] = [
    { label: 'Week', value: 'week' },
    { label: 'Month', value: 'month' },
    { label: 'Quarter', value: 'quarter' },
    { label: 'Year', value: 'year' },
  ];

  // Mock company ID for testing
  const companyId = '123e4567-e89b-12d3-a456-426614174007';

  useEffect(() => {
    loadReportData();
  }, [selectedTimeRange]);

  const loadReportData = async () => {
    setIsLoading(true);
    try {
      // In a real implementation, this would call a dedicated reports API
      const response = await apiService.getBookings(companyId, 100, 0);
      if (response.success && response.data) {
        const data = generateReportData(response.data);
        setReportData(data);
      } else {
        Alert.alert('Error', 'Failed to load report data');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadReportData();
    setIsRefreshing(false);
  };

  const generateReportData = (bookings: BookingDetails[]): ReportData => {
    const totalExpenses = bookings.reduce((sum, booking) => 
      sum + booking.lines.reduce((lineSum, line) => lineSum + line.amount, 0), 0
    );
    
    const totalBookings = bookings.length;
    const averageExpense = totalBookings > 0 ? totalExpenses / totalBookings : 0;

    // Calculate monthly trend (simplified)
    const monthlyTrend = 12.5; // This would be calculated from historical data

    // Generate top categories (simplified)
    const topCategories = [
      { category: 'Representation', amount: totalExpenses * 0.4, percentage: 40 },
      { category: 'Transport', amount: totalExpenses * 0.3, percentage: 30 },
      { category: 'SaaS', amount: totalExpenses * 0.2, percentage: 20 },
      { category: 'Office', amount: totalExpenses * 0.1, percentage: 10 },
    ];

    // Recent activity (last 5 bookings)
    const recentActivity = bookings.slice(0, 5);

    // Monthly breakdown (simplified)
    const monthlyBreakdown = [
      { month: 'Jan', amount: totalExpenses * 0.8, bookings: Math.floor(totalBookings * 0.8) },
      { month: 'Feb', amount: totalExpenses * 1.2, bookings: Math.floor(totalBookings * 1.2) },
      { month: 'Mar', amount: totalExpenses * 0.9, bookings: Math.floor(totalBookings * 0.9) },
      { month: 'Apr', amount: totalExpenses * 1.1, bookings: Math.floor(totalBookings * 1.1) },
    ];

    return {
      totalExpenses,
      totalBookings,
      averageExpense,
      monthlyTrend,
      topCategories,
      recentActivity,
      monthlyBreakdown,
    };
  };

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('sv-SE', {
      style: 'currency',
      currency: 'SEK',
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('sv-SE', {
      month: 'short',
      day: 'numeric',
    });
  };

  const getTrendIcon = (trend: number) => {
    return trend > 0 ? 'trending-up' : 'trending-down';
  };

  const getTrendColor = (trend: number) => {
    return trend > 0 ? '#2DD4BF' : '#FF8A65';
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
    headerTitle: {
      ...typography.scale.h2,
      color: theme.colors.text,
      marginLeft: spacing.sm,
    },
    timeRangeSelector: {
      flexDirection: 'row',
      backgroundColor: theme.colors.surface,
      borderRadius: theme.radius.lg,
      padding: spacing.xs,
      marginBottom: spacing.lg,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    timeRangeButton: {
      flex: 1,
      paddingVertical: spacing.sm,
      paddingHorizontal: spacing.md,
      borderRadius: theme.radius.md,
      alignItems: 'center',
    },
    timeRangeButtonActive: {
      backgroundColor: theme.brand.primary,
    },
    timeRangeButtonText: {
      ...typography.scale.bodySmall,
      color: theme.colors.text,
      fontWeight: '500',
    },
    timeRangeButtonTextActive: {
      color: theme.colors.background,
    },
    viewSelector: {
      flexDirection: 'row',
      marginBottom: spacing.lg,
    },
    viewButton: {
      flex: 1,
      paddingVertical: spacing.md,
      paddingHorizontal: spacing.lg,
      borderRadius: theme.radius.lg,
      alignItems: 'center',
      marginHorizontal: spacing.xs,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    viewButtonActive: {
      backgroundColor: theme.brand.primary,
      borderColor: theme.brand.primary,
    },
    viewButtonText: {
      ...typography.scale.body,
      color: theme.colors.text,
      fontWeight: '500',
    },
    viewButtonTextActive: {
      color: theme.colors.background,
    },
    overviewCard: {
      marginBottom: spacing.lg,
    },
    overviewGrid: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      justifyContent: 'space-between',
    },
    overviewItem: {
      width: (width - spacing.screen.horizontal * 2 - spacing.md) / 2,
      backgroundColor: theme.colors.surface,
      borderRadius: theme.radius.lg,
      padding: spacing.lg,
      marginBottom: spacing.md,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    overviewItemFull: {
      width: '100%',
    },
    overviewValue: {
      ...typography.scale.h2,
      color: theme.colors.text,
      fontWeight: '700',
      marginBottom: spacing.xs,
    },
    overviewLabel: {
      ...typography.scale.bodySmall,
      color: theme.colors.textSecondary,
      marginBottom: spacing.sm,
    },
    overviewTrend: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    overviewTrendText: {
      ...typography.scale.bodySmall,
      color: theme.colors.textSecondary,
      marginLeft: spacing.xs,
    },
    categoryCard: {
      marginBottom: spacing.lg,
    },
    categoryItem: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: spacing.md,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
    },
    categoryBar: {
      height: 8,
      backgroundColor: theme.colors.border,
      borderRadius: 4,
      marginRight: spacing.md,
      flex: 1,
    },
    categoryBarFill: {
      height: '100%',
      borderRadius: 4,
    },
    categoryInfo: {
      flex: 1,
    },
    categoryName: {
      ...typography.scale.body,
      color: theme.colors.text,
      fontWeight: '500',
      marginBottom: spacing.xs,
    },
    categoryAmount: {
      ...typography.scale.bodySmall,
      color: theme.colors.textSecondary,
    },
    categoryPercentage: {
      ...typography.scale.body,
      color: theme.colors.text,
      fontWeight: '600',
      marginLeft: spacing.md,
    },
    trendsCard: {
      marginBottom: spacing.lg,
    },
    monthlyChart: {
      flexDirection: 'row',
      alignItems: 'flex-end',
      justifyContent: 'space-between',
      height: 120,
      marginBottom: spacing.lg,
    },
    monthlyBar: {
      backgroundColor: theme.brand.primary,
      borderRadius: 4,
      marginHorizontal: 2,
      minHeight: 20,
    },
    monthlyLabel: {
      ...typography.scale.bodySmall,
      color: theme.colors.textSecondary,
      textAlign: 'center',
      marginTop: spacing.sm,
    },
    recentActivityCard: {
      marginBottom: spacing.lg,
    },
    activityItem: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: spacing.md,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
    },
    activityIcon: {
      width: 40,
      height: 40,
      borderRadius: 20,
      backgroundColor: theme.brand.primary,
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
      marginBottom: spacing.xs,
    },
    activityDate: {
      ...typography.scale.bodySmall,
      color: theme.colors.textSecondary,
    },
    activityAmount: {
      ...typography.scale.body,
      color: theme.colors.text,
      fontWeight: '600',
    },
    emptyState: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      paddingVertical: spacing['4xl'],
    },
    emptyStateIcon: {
      marginBottom: spacing.lg,
    },
    emptyStateTitle: {
      ...typography.scale.h3,
      color: theme.colors.text,
      marginBottom: spacing.sm,
      textAlign: 'center',
    },
    emptyStateText: {
      ...typography.scale.body,
      color: theme.colors.textSecondary,
      textAlign: 'center',
      marginBottom: spacing.lg,
    },
  });

  if (isLoading && !reportData) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.content}>
          <View style={styles.emptyState}>
            <ActivityIndicator size="large" color={theme.brand.primary} />
            <Text style={styles.emptyStateTitle}>Loading reports...</Text>
          </View>
        </View>
      </SafeAreaView>
    );
  }

  if (!reportData) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.content}>
          <View style={styles.emptyState}>
            <Ionicons 
              name="bar-chart-outline" 
              size={64} 
              color={theme.colors.textSecondary} 
              style={styles.emptyStateIcon}
            />
            <Text style={styles.emptyStateTitle}>No data available</Text>
            <Text style={styles.emptyStateText}>
              Start by adding some expenses to see your reports
            </Text>
            <Button
              title="Go to Fire"
              onPress={() => {/* Navigate to Fire tab */}}
              variant="primary"
            />
          </View>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        style={styles.content} 
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={handleRefresh}
            tintColor={theme.brand.primary}
          />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <Ionicons 
              name="bar-chart" 
              size={24} 
              color={theme.brand.primary} 
            />
            <Text style={styles.headerTitle}>Rapporter</Text>
          </View>
        </View>

        {/* Time Range Selector */}
        <View style={styles.timeRangeSelector}>
          {timeRanges.map((range) => (
            <TouchableOpacity
              key={range.value}
              style={[
                styles.timeRangeButton,
                selectedTimeRange === range.value && styles.timeRangeButtonActive,
              ]}
              onPress={() => setSelectedTimeRange(range.value)}
            >
              <Text style={[
                styles.timeRangeButtonText,
                selectedTimeRange === range.value && styles.timeRangeButtonTextActive,
              ]}>
                {range.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* View Selector */}
        <View style={styles.viewSelector}>
          <TouchableOpacity
            style={[
              styles.viewButton,
              selectedView === 'overview' && styles.viewButtonActive,
            ]}
            onPress={() => setSelectedView('overview')}
          >
            <Text style={[
              styles.viewButtonText,
              selectedView === 'overview' && styles.viewButtonTextActive,
            ]}>
              Overview
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[
              styles.viewButton,
              selectedView === 'categories' && styles.viewButtonActive,
            ]}
            onPress={() => setSelectedView('categories')}
          >
            <Text style={[
              styles.viewButtonText,
              selectedView === 'categories' && styles.viewButtonTextActive,
            ]}>
              Categories
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[
              styles.viewButton,
              selectedView === 'trends' && styles.viewButtonActive,
            ]}
            onPress={() => setSelectedView('trends')}
          >
            <Text style={[
              styles.viewButtonText,
              selectedView === 'trends' && styles.viewButtonTextActive,
            ]}>
              Trends
            </Text>
          </TouchableOpacity>
        </View>

        {/* Overview View */}
        {selectedView === 'overview' && (
          <Card style={styles.overviewCard}>
            <View style={styles.overviewGrid}>
              <View style={styles.overviewItem}>
                <Text style={styles.overviewValue}>
                  {formatAmount(reportData.totalExpenses)}
                </Text>
                <Text style={styles.overviewLabel}>Total Expenses</Text>
                <View style={styles.overviewTrend}>
                  <Ionicons 
                    name={getTrendIcon(reportData.monthlyTrend)} 
                    size={16} 
                    color={getTrendColor(reportData.monthlyTrend)} 
                  />
                  <Text style={[styles.overviewTrendText, { color: getTrendColor(reportData.monthlyTrend) }]}>
                    {Math.abs(reportData.monthlyTrend)}%
                  </Text>
                </View>
              </View>

              <View style={styles.overviewItem}>
                <Text style={styles.overviewValue}>{reportData.totalBookings}</Text>
                <Text style={styles.overviewLabel}>Total Bookings</Text>
              </View>

              <View style={styles.overviewItem}>
                <Text style={styles.overviewValue}>
                  {formatAmount(reportData.averageExpense)}
                </Text>
                <Text style={styles.overviewLabel}>Average Expense</Text>
              </View>

              <View style={[styles.overviewItem, styles.overviewItemFull]}>
                <Text style={styles.overviewValue}>
                  {formatAmount(reportData.totalExpenses * 0.25)}
                </Text>
                <Text style={styles.overviewLabel}>VAT Deductible</Text>
              </View>
            </View>
          </Card>
        )}

        {/* Categories View */}
        {selectedView === 'categories' && (
          <Card style={styles.categoryCard}>
            <Text style={[styles.overviewLabel, { marginBottom: spacing.lg }]}>
              Expense Categories
            </Text>
            {reportData.topCategories.map((category, index) => (
              <View key={index} style={styles.categoryItem}>
                <View style={styles.categoryBar}>
                  <View 
                    style={[
                      styles.categoryBarFill,
                      { 
                        width: `${category.percentage}%`,
                        backgroundColor: theme.brand.primary,
                      }
                    ]} 
                  />
                </View>
                <View style={styles.categoryInfo}>
                  <Text style={styles.categoryName}>{category.category}</Text>
                  <Text style={styles.categoryAmount}>
                    {formatAmount(category.amount)}
                  </Text>
                </View>
                <Text style={styles.categoryPercentage}>
                  {category.percentage}%
                </Text>
              </View>
            ))}
          </Card>
        )}

        {/* Trends View */}
        {selectedView === 'trends' && (
          <Card style={styles.trendsCard}>
            <Text style={[styles.overviewLabel, { marginBottom: spacing.lg }]}>
              Monthly Breakdown
            </Text>
            <View style={styles.monthlyChart}>
              {reportData.monthlyBreakdown.map((month, index) => {
                const maxAmount = Math.max(...reportData.monthlyBreakdown.map(m => m.amount));
                const height = (month.amount / maxAmount) * 100;
                return (
                  <View key={index} style={{ alignItems: 'center', flex: 1 }}>
                    <View 
                      style={[
                        styles.monthlyBar,
                        { 
                          height: Math.max(height, 20),
                          backgroundColor: theme.brand.primary,
                        }
                      ]} 
                    />
                    <Text style={styles.monthlyLabel}>{month.month}</Text>
                  </View>
                );
              })}
            </View>
          </Card>
        )}

        {/* Recent Activity */}
        <Card style={styles.recentActivityCard}>
          <Text style={[styles.overviewLabel, { marginBottom: spacing.lg }]}>
            Recent Activity
          </Text>
          {reportData.recentActivity.map((booking, index) => {
            const totalAmount = booking.lines.reduce((sum, line) => sum + line.amount, 0);
            return (
              <View key={index} style={styles.activityItem}>
                <View style={styles.activityIcon}>
                  <Ionicons name="receipt" size={20} color={theme.colors.background} />
                </View>
                <View style={styles.activityContent}>
                  <Text style={styles.activityTitle}>
                    {booking.series}{booking.number}
                  </Text>
                  <Text style={styles.activityDate}>
                    {formatDate(booking.created_at)}
                  </Text>
                </View>
                <Text style={styles.activityAmount}>
                  {formatAmount(totalAmount)}
                </Text>
              </View>
            );
          })}
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
};

export default ReportsScreen;
