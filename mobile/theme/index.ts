import { MD3LightTheme as DefaultTheme } from 'react-native-paper';

export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#4F46E5',
    onPrimary: '#FFFFFF',
    secondary: '#10B981',
    onSecondary: '#FFFFFF',
    tertiary: '#F59E0B',
    error: '#EF4444',
    onError: '#FFFFFF',
    background: '#F9FAFB',
    surface: '#FFFFFF',
    onSurface: '#1F2937',
    surfaceVariant: '#F3F4F6',
    outline: '#D1D5DB',
  },
  roundness: 12,
  fonts: {
    ...DefaultTheme.fonts,
    titleLarge: {
      ...DefaultTheme.fonts.titleLarge,
      fontWeight: 'bold',
    },
  },
};

export const COLORS = {
  primary: '#4F46E5',
  secondary: '#10B981',
  error: '#EF4444',
  warning: '#F59E0B',
  background: '#F9FAFB',
  surface: '#FFFFFF',
  text: '#1F2937',
  textSecondary: '#6B7280',
  border: '#E5E7EB',
  success: '#10B981',
  pending: '#F59E0B',
  absent: '#EF4444',
  present: '#10B981',
};

export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/api/v1',
  GRAPHQL_URL: 'http://localhost:8000/graphql',
  AI_SERVICES_URL: 'http://localhost:8001',
  TIMEOUT: 30000,
};
