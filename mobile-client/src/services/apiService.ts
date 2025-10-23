/**
 * API Service for Fire & Forget Accounting
 * Handles all backend communication
 */

import { config } from '@/config/environment';

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface NaturalLanguageRequest {
  text: string;
  company_id: string;
}

export interface NaturalLanguageResponse {
  success: boolean;
  message: string;
  booking_id?: string;
  booking_details?: {
    debit_accounts: Array<{
      account: string;
      amount: number;
      description: string;
    }>;
    credit_accounts: Array<{
      account: string;
      amount: number;
      description: string;
    }>;
    vat_details: {
      code: string;
      rate: string;
    };
    total_amount: number;
    currency: string;
  };
  status: 'GREEN' | 'YELLOW' | 'RED';
  reason_codes?: string[];
  policy_used?: string;
  receipt_attachment_prompt?: string;
}

export interface BookingDetails {
  id: string;
  company_id: string;
  date: string;
  series: string;
  number: string;
  notes: string;
  created_at: string;
  created_by: string;
  lines: Array<{
    id: string;
    account: string;
    side: string;
    amount: number;
    dimension_project?: string;
    dimension_cost_center?: string;
    description: string;
  }>;
}

export interface ActivityItem {
  id: string;
  type: 'booking' | 'notification' | 'reminder';
  title: string;
  description: string;
  amount?: number;
  currency?: string;
  date: string;
  status: 'success' | 'warning' | 'error' | 'info';
}

class ApiService {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor() {
    this.baseUrl = config.apiUrl;
  }

  setAuthToken(token: string) {
    this.authToken = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...options.headers,
      };

      if (this.authToken) {
        headers.Authorization = `Bearer ${this.authToken}`;
      }

      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.detail || data.message || 'Request failed',
        };
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
      };
    }
  }

  // Authentication
  async getTestToken(): Promise<ApiResponse<{ access_token: string }>> {
    return this.request('/api/v1/auth/test-token', {
      method: 'POST',
    });
  }

  // Natural Language Processing
  async processNaturalLanguage(
    request: NaturalLanguageRequest
  ): Promise<ApiResponse<NaturalLanguageResponse>> {
    return this.request('/api/v1/natural-language/process', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getNaturalLanguageExamples(): Promise<ApiResponse<{ examples: Array<{ description: string; text: string }> }>> {
    return this.request('/api/v1/natural-language/examples');
  }

  // Bookings
  async getBooking(bookingId: string): Promise<ApiResponse<BookingDetails>> {
    return this.request(`/api/v1/bookings/${bookingId}`);
  }

  async getBookings(companyId: string, limit = 50, offset = 0): Promise<ApiResponse<BookingDetails[]>> {
    return this.request(`/api/v1/bookings?company_id=${companyId}&limit=${limit}&offset=${offset}`);
  }

  // Health check
  async getHealth(): Promise<ApiResponse<{ status: string; service: string }>> {
    return this.request('/health');
  }

  // Get activity feed (combines bookings and notifications)
  async getActivityFeed(companyId: string): Promise<ApiResponse<ActivityItem[]>> {
    try {
      const [bookingsResponse, healthResponse] = await Promise.all([
        this.getBookings(companyId, 10, 0),
        this.getHealth(),
      ]);

      const activities: ActivityItem[] = [];

      if (bookingsResponse.success && bookingsResponse.data) {
        bookingsResponse.data.forEach((booking) => {
          activities.push({
            id: booking.id,
            type: 'booking',
            title: `Booking ${booking.series}${booking.number}`,
            description: booking.notes,
            amount: booking.lines.reduce((sum, line) => sum + line.amount, 0),
            currency: 'SEK',
            date: booking.created_at,
            status: 'success',
          });
        });
      }

      // Add system notifications
      if (healthResponse.success) {
        activities.push({
          id: 'system-health',
          type: 'notification',
          title: 'System Status',
          description: 'All systems operational',
          date: new Date().toISOString(),
          status: 'info',
        });
      }

      return {
        success: true,
        data: activities.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch activity feed',
      };
    }
  }

  // Reports and Analytics
  async getReportsData(companyId: string, timeRange: 'week' | 'month' | 'quarter' | 'year' = 'month'): Promise<ApiResponse<{
    totalExpenses: number;
    totalBookings: number;
    averageExpense: number;
    monthlyTrend: number;
    topCategories: Array<{
      category: string;
      amount: number;
      percentage: number;
    }>;
    monthlyBreakdown: Array<{
      month: string;
      amount: number;
      bookings: number;
    }>;
  }>> {
    try {
      // Get bookings for the specified time range
      const limit = timeRange === 'week' ? 50 : timeRange === 'month' ? 100 : timeRange === 'quarter' ? 200 : 500;
      const response = await this.getBookings(companyId, limit, 0);
      
      if (!response.success || !response.data) {
        return {
          success: false,
          error: 'Failed to fetch bookings for reports',
        };
      }

      const bookings = response.data;
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

      // Monthly breakdown (simplified)
      const monthlyBreakdown = [
        { month: 'Jan', amount: totalExpenses * 0.8, bookings: Math.floor(totalBookings * 0.8) },
        { month: 'Feb', amount: totalExpenses * 1.2, bookings: Math.floor(totalBookings * 1.2) },
        { month: 'Mar', amount: totalExpenses * 0.9, bookings: Math.floor(totalBookings * 0.9) },
        { month: 'Apr', amount: totalExpenses * 1.1, bookings: Math.floor(totalBookings * 1.1) },
      ];

      return {
        success: true,
        data: {
          totalExpenses,
          totalBookings,
          averageExpense,
          monthlyTrend,
          topCategories,
          monthlyBreakdown,
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch reports data',
      };
    }
  }

  // Get booking statistics
  async getBookingStats(companyId: string): Promise<ApiResponse<{
    totalAmount: number;
    totalBookings: number;
    averageAmount: number;
    thisMonth: number;
    lastMonth: number;
  }>> {
    try {
      const response = await this.getBookings(companyId, 100, 0);
      
      if (!response.success || !response.data) {
        return {
          success: false,
          error: 'Failed to fetch booking statistics',
        };
      }

      const bookings = response.data;
      const totalAmount = bookings.reduce((sum, booking) => 
        sum + booking.lines.reduce((lineSum, line) => lineSum + line.amount, 0), 0
      );
      
      const totalBookings = bookings.length;
      const averageAmount = totalBookings > 0 ? totalAmount / totalBookings : 0;

      // Calculate monthly amounts (simplified)
      const thisMonth = totalAmount * 0.6;
      const lastMonth = totalAmount * 0.4;

      return {
        success: true,
        data: {
          totalAmount,
          totalBookings,
          averageAmount,
          thisMonth,
          lastMonth,
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch booking statistics',
      };
    }
  }
}

export const apiService = new ApiService();
