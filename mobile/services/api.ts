import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
import * as SecureStore from 'expo-secure-store';
import { API_CONFIG } from '../theme';

class ApiService {
  private client: AxiosInstance;
  private static instance: ApiService;

  private constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  public static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  private setupInterceptors(): void {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      async (config) => {
        const token = await SecureStore.getItemAsync('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid - logout user
          await SecureStore.deleteItemAsync('authToken');
          await SecureStore.deleteItemAsync('user');
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

export const api = ApiService.getInstance();

// API Endpoints
export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  REGISTER: '/auth/register',
  FORGOT_PASSWORD: '/auth/forgot-password',
  CHANGE_PASSWORD: '/auth/change-password',

  // Students
  STUDENTS: '/students',
  STUDENT_BY_ID: (id: string) => `/students/${id}`,
  STUDENT_ATTENDANCE: (id: string) => `/students/${id}/attendance`,
  STUDENT_GRADES: (id: string) => `/students/${id}/grades`,

  // Teachers
  TEACHERS: '/teachers',
  TEACHER_BY_ID: (id: string) => `/teachers/${id}`,

  // Classes
  CLASSES: '/classes',
  CLASS_BY_ID: (id: string) => `/classes/${id}`,
  CLASS_STUDENTS: (id: string) => `/classes/${id}/students`,

  // Attendance
  ATTENDANCE: '/attendance',
  ATTENDANCE_MARK: '/attendance/mark',
  ATTENDANCE_CLASS: (classId: string) => `/attendance/class/${classId}`,
  ATTENDANCE_STUDENT: (studentId: string) => `/attendance/student/${studentId}`,

  // Grades
  GRADES: '/grades',
  GRADES_BY_STUDENT: (studentId: string) => `/grades/student/${studentId}`,
  GRADES_BY_CLASS: (classId: string) => `/grades/class/${classId}`,

  // Fees
  FEES: '/fees',
  FEES_BY_STUDENT: (studentId: string) => `/fees/student/${studentId}`,
  FEE_PAY: '/fees/pay',

  // Academic Years
  ACADEMIC_YEARS: '/academic-years',

  // Reports
  ATTENDANCE_REPORT: '/reports/attendance',
  GRADES_REPORT: '/reports/grades',
  FINANCIAL_REPORT: '/reports/financial',
};

// Helper function for handling API errors
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string; message?: string }>;
    return axiosError.response?.data?.detail || 
           axiosError.response?.data?.message || 
           axiosError.message || 
           'An unexpected error occurred';
  }
  return 'An unexpected error occurred';
};
