import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import * as SecureStore from 'expo-secure-store';

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'admin' | 'principal' | 'teacher' | 'student' | 'parent' | 'accountant';
  avatar?: string;
  schoolId?: string;
  classId?: string;
  childIds?: string[];
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  biometricEnabled: boolean;
}

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  biometricEnabled: false,
};

// Async thunk for login
export const loginUser = createAsyncThunk(
  'auth/login',
  async ({ email, password }: { email: string; password: string }, { rejectWithValue }) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock user based on email/role
      let user: User;
      if (email.includes('admin')) {
        user = {
          id: 'admin-001',
          email,
          firstName: 'Admin',
          lastName: 'User',
          role: 'admin',
        };
      } else if (email.includes('teacher')) {
        user = {
          id: 'teacher-001',
          email,
          firstName: 'Mr.',
          lastName: 'Sharma',
          role: 'teacher',
          schoolId: 'school-001',
        };
      } else if (email.includes('student')) {
        user = {
          id: 'student-001',
          email,
          firstName: 'John',
          lastName: 'Doe',
          role: 'student',
          schoolId: 'school-001',
          classId: 'class-10-a',
        };
      } else if (email.includes('parent')) {
        user = {
          id: 'parent-001',
          email,
          firstName: 'Jane',
          lastName: 'Doe',
          role: 'parent',
          childIds: ['student-001'],
        };
      } else {
        user = {
          id: 'user-001',
          email,
          firstName: 'Test',
          lastName: 'User',
          role: 'teacher',
        };
      }
      
      const token = `mock-jwt-token-${Date.now()}`;
      
      // Save token securely
      await SecureStore.setItemAsync('authToken', token);
      await SecureStore.setItemAsync('user', JSON.stringify(user));
      
      return { user, token };
    } catch (error) {
      return rejectWithValue('Login failed. Please try again.');
    }
  }
);

// Async thunk for logout
export const logoutUser = createAsyncThunk('auth/logout', async () => {
  await SecureStore.deleteItemAsync('authToken');
  await SecureStore.deleteItemAsync('user');
});

// Async thunk for restore session
export const restoreSession = createAsyncThunk('auth/restoreSession', async () => {
  const token = await SecureStore.getItemAsync('authToken');
  const userStr = await SecureStore.getItemAsync('user');
  
  if (token && userStr) {
    const user = JSON.parse(userStr);
    return { user, token };
  }
  return { user: null, token: null };
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setBiometricEnabled: (state, action: PayloadAction<boolean>) => {
      state.biometricEnabled = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(logoutUser.fulfilled, (state) => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      })
      .addCase(restoreSession.fulfilled, (state, action) => {
        if (action.payload.user) {
          state.user = action.payload.user;
          state.token = action.payload.token;
          state.isAuthenticated = true;
        }
      });
  },
});

export const { setBiometricEnabled, clearError } = authSlice.actions;
export default authSlice.reducer;
