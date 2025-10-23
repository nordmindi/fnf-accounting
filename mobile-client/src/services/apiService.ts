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
}

export const apiService = new ApiService();
