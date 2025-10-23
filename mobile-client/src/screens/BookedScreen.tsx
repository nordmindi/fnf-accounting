/**
 * Booked Expenses Screen
 * Shows all booked expenses with filtering, search, and detailed view
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  RefreshControl,
  Alert,
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
import { apiService, BookingDetails, ActivityItem } from '@/services/apiService';

interface FilterState {
  dateRange: 'all' | 'today' | 'week' | 'month';
  amountRange: 'all' | 'low' | 'medium' | 'high';
  status: 'all' | 'success' | 'warning' | 'error';
}

const BookedScreen: React.FC = () => {
  const { t } = useTranslation();
  const theme = useAppTheme();
  const { isDark } = useTheme();
  
  const [bookings, setBookings] = useState<BookingDetails[]>([]);
  const [filteredBookings, setFilteredBookings] = useState<BookingDetails[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterState>({
    dateRange: 'all',
    amountRange: 'all',
    status: 'all',
  });
  const [showFilters, setShowFilters] = useState(false);

  // Mock company ID for testing
  const companyId = '123e4567-e89b-12d3-a456-426614174007';

  useEffect(() => {
    loadBookings();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [bookings, searchQuery, filters]);

  const loadBookings = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.getBookings(companyId, 50, 0);
      if (response.success && response.data) {
        setBookings(response.data);
      } else {
        Alert.alert('Error', 'Failed to load bookings');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadBookings();
    setIsRefreshing(false);
  };

  const applyFilters = () => {
    let filtered = [...bookings];

    // Search filter
    if (searchQuery.trim()) {
      filtered = filtered.filter(booking =>
        booking.notes.toLowerCase().includes(searchQuery.toLowerCase()) ||
        booking.series.toLowerCase().includes(searchQuery.toLowerCase()) ||
        booking.number.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Date range filter
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    if (filters.dateRange !== 'all') {
      filtered = filtered.filter(booking => {
        const bookingDate = new Date(booking.created_at);
        switch (filters.dateRange) {
          case 'today':
            return bookingDate >= today;
          case 'week':
            const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            return bookingDate >= weekAgo;
          case 'month':
            const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
            return bookingDate >= monthAgo;
          default:
            return true;
        }
      });
    }

    // Amount range filter
    if (filters.amountRange !== 'all') {
      filtered = filtered.filter(booking => {
        const totalAmount = booking.lines.reduce((sum, line) => sum + line.amount, 0);
        switch (filters.amountRange) {
          case 'low':
            return totalAmount < 500;
          case 'medium':
            return totalAmount >= 500 && totalAmount < 2000;
          case 'high':
            return totalAmount >= 2000;
          default:
            return true;
        }
      });
    }

    setFilteredBookings(filtered);
  };

  const getTotalAmount = (booking: BookingDetails) => {
    return booking.lines.reduce((sum, line) => sum + line.amount, 0);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('sv-SE', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('sv-SE', {
      style: 'currency',
      currency: 'SEK',
    }).format(amount);
  };

  const getStatusColor = (booking: BookingDetails) => {
    // This would be determined by the booking status in a real implementation
    return '#2DD4BF'; // Default to success
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
    filterButton: {
      padding: spacing.sm,
      borderRadius: theme.radius.md,
      backgroundColor: theme.colors.surface,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    searchContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: theme.colors.surface,
      borderRadius: theme.radius.lg,
      paddingHorizontal: spacing.md,
      marginBottom: spacing.lg,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    searchInput: {
      flex: 1,
      ...typography.scale.body,
      color: theme.colors.text,
      paddingVertical: spacing.md,
    },
    clearButton: {
      padding: spacing.sm,
    },
    filtersContainer: {
      backgroundColor: theme.colors.surface,
      borderRadius: theme.radius.lg,
      padding: spacing.lg,
      marginBottom: spacing.lg,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    filterRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      marginBottom: spacing.md,
    },
    filterLabel: {
      ...typography.scale.body,
      color: theme.colors.text,
      fontWeight: '500',
    },
    filterButtons: {
      flexDirection: 'row',
      gap: spacing.sm,
    },
    filterButton: {
      paddingHorizontal: spacing.md,
      paddingVertical: spacing.sm,
      borderRadius: theme.radius.md,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    filterButtonActive: {
      backgroundColor: theme.brand.primary,
      borderColor: theme.brand.primary,
    },
    filterButtonText: {
      ...typography.scale.bodySmall,
      color: theme.colors.text,
    },
    filterButtonTextActive: {
      color: theme.colors.background,
    },
    bookingCard: {
      marginBottom: spacing.md,
    },
    bookingHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: spacing.sm,
    },
    bookingId: {
      ...typography.scale.body,
      color: theme.colors.text,
      fontWeight: '600',
    },
    bookingDate: {
      ...typography.scale.bodySmall,
      color: theme.colors.textSecondary,
    },
    bookingAmount: {
      ...typography.scale.bodyLarge,
      color: theme.colors.text,
      fontWeight: '700',
    },
    bookingNotes: {
      ...typography.scale.body,
      color: theme.colors.textSecondary,
      marginBottom: spacing.sm,
    },
    bookingLines: {
      marginTop: spacing.sm,
    },
    bookingLine: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingVertical: spacing.xs,
    },
    bookingLineAccount: {
      ...typography.scale.bodySmall,
      color: theme.colors.text,
      flex: 1,
    },
    bookingLineAmount: {
      ...typography.scale.bodySmall,
      color: theme.colors.textSecondary,
      fontWeight: '500',
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
    statsContainer: {
      flexDirection: 'row',
      justifyContent: 'space-around',
      backgroundColor: theme.colors.surface,
      borderRadius: theme.radius.lg,
      padding: spacing.lg,
      marginBottom: spacing.lg,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    statItem: {
      alignItems: 'center',
    },
    statValue: {
      ...typography.scale.h3,
      color: theme.colors.text,
      fontWeight: '700',
    },
    statLabel: {
      ...typography.scale.bodySmall,
      color: theme.colors.textSecondary,
      marginTop: spacing.xs,
    },
  });

  const getStats = () => {
    const totalAmount = filteredBookings.reduce((sum, booking) => sum + getTotalAmount(booking), 0);
    const totalCount = filteredBookings.length;
    const avgAmount = totalCount > 0 ? totalAmount / totalCount : 0;

    return {
      totalAmount,
      totalCount,
      avgAmount,
    };
  };

  const stats = getStats();

  if (isLoading && bookings.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.content}>
          <View style={styles.emptyState}>
            <ActivityIndicator size="large" color={theme.brand.primary} />
            <Text style={styles.emptyStateTitle}>Loading bookings...</Text>
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
              name="receipt" 
              size={24} 
              color={theme.brand.primary} 
            />
            <Text style={styles.headerTitle}>Bokfört</Text>
          </View>
          <TouchableOpacity 
            style={styles.filterButton}
            onPress={() => setShowFilters(!showFilters)}
          >
            <Ionicons 
              name={showFilters ? "close" : "filter"} 
              size={20} 
              color={theme.colors.text} 
            />
          </TouchableOpacity>
        </View>

        {/* Search */}
        <View style={styles.searchContainer}>
          <Ionicons name="search" size={20} color={theme.colors.textSecondary} />
          <TextInput
            style={styles.searchInput}
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholder="Search bookings..."
            placeholderTextColor={theme.colors.textSecondary}
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity 
              style={styles.clearButton}
              onPress={() => setSearchQuery('')}
            >
              <Ionicons name="close-circle" size={20} color={theme.colors.textSecondary} />
            </TouchableOpacity>
          )}
        </View>

        {/* Filters */}
        {showFilters && (
          <View style={styles.filtersContainer}>
            <View style={styles.filterRow}>
              <Text style={styles.filterLabel}>Date Range</Text>
              <View style={styles.filterButtons}>
                {['all', 'today', 'week', 'month'].map((range) => (
                  <TouchableOpacity
                    key={range}
                    style={[
                      styles.filterButton,
                      filters.dateRange === range && styles.filterButtonActive,
                    ]}
                    onPress={() => setFilters(prev => ({ ...prev, dateRange: range as any }))}
                  >
                    <Text style={[
                      styles.filterButtonText,
                      filters.dateRange === range && styles.filterButtonTextActive,
                    ]}>
                      {range.charAt(0).toUpperCase() + range.slice(1)}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <View style={styles.filterRow}>
              <Text style={styles.filterLabel}>Amount Range</Text>
              <View style={styles.filterButtons}>
                {['all', 'low', 'medium', 'high'].map((range) => (
                  <TouchableOpacity
                    key={range}
                    style={[
                      styles.filterButton,
                      filters.amountRange === range && styles.filterButtonActive,
                    ]}
                    onPress={() => setFilters(prev => ({ ...prev, amountRange: range as any }))}
                  >
                    <Text style={[
                      styles.filterButtonText,
                      filters.amountRange === range && styles.filterButtonTextActive,
                    ]}>
                      {range.charAt(0).toUpperCase() + range.slice(1)}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </View>
        )}

        {/* Stats */}
        {filteredBookings.length > 0 && (
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{stats.totalCount}</Text>
              <Text style={styles.statLabel}>Bookings</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{formatAmount(stats.totalAmount)}</Text>
              <Text style={styles.statLabel}>Total Amount</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{formatAmount(stats.avgAmount)}</Text>
              <Text style={styles.statLabel}>Average</Text>
            </View>
          </View>
        )}

        {/* Bookings List */}
        {filteredBookings.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons 
              name="receipt-outline" 
              size={64} 
              color={theme.colors.textSecondary} 
              style={styles.emptyStateIcon}
            />
            <Text style={styles.emptyStateTitle}>
              {searchQuery || filters.dateRange !== 'all' || filters.amountRange !== 'all' 
                ? 'No bookings found' 
                : 'No bookings yet'
              }
            </Text>
            <Text style={styles.emptyStateText}>
              {searchQuery || filters.dateRange !== 'all' || filters.amountRange !== 'all'
                ? 'Try adjusting your search or filters'
                : 'Start by adding your first expense in the Fire tab'
              }
            </Text>
            {!searchQuery && filters.dateRange === 'all' && filters.amountRange === 'all' && (
              <Button
                title="Go to Fire"
                onPress={() => {/* Navigate to Fire tab */}}
                variant="primary"
              />
            )}
          </View>
        ) : (
          filteredBookings.map((booking) => (
            <Card key={booking.id} style={styles.bookingCard}>
              <View style={styles.bookingHeader}>
                <View>
                  <Text style={styles.bookingId}>
                    {booking.series}{booking.number}
                  </Text>
                  <Text style={styles.bookingDate}>
                    {formatDate(booking.created_at)}
                  </Text>
                </View>
                <Text style={styles.bookingAmount}>
                  {formatAmount(getTotalAmount(booking))}
                </Text>
              </View>

              {booking.notes && (
                <Text style={styles.bookingNotes}>{booking.notes}</Text>
              )}

              <View style={styles.bookingLines}>
                {booking.lines.slice(0, 3).map((line, index) => (
                  <View key={index} style={styles.bookingLine}>
                    <Text style={styles.bookingLineAccount}>
                      {line.account} - {line.description}
                    </Text>
                    <Text style={styles.bookingLineAmount}>
                      {formatAmount(line.amount)}
                    </Text>
                  </View>
                ))}
                {booking.lines.length > 3 && (
                  <Text style={styles.bookingLineAccount}>
                    +{booking.lines.length - 3} more lines
                  </Text>
                )}
              </View>
            </Card>
          ))
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

export default BookedScreen;
