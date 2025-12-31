import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
  TouchableOpacity,
} from 'react-native';
import {
  Text,
  TextInput,
  Button,
  Surface,
  ActivityIndicator,
  useTheme,
} from 'react-native-paper';
import { useRouter } from 'expo-router';
import { useDispatch, useSelector } from 'react-redux';
import { loginUser, restoreSession } from '../../store/slices/authSlice';
import { RootState, AppDispatch } from '../../store/store';
import * as LocalAuthentication from 'expo-local-authentication';
import { MOCK_USERS } from '../../services/mockData';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();
  const { isLoading, error } = useSelector((state: RootState) => state.auth);
  const theme = useTheme();

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please enter email and password');
      return;
    }
    
    const result = await dispatch(loginUser({ email, password }));
    if (loginUser.fulfilled.match(result)) {
      router.replace('/(app)/home');
    }
  };

  const handleBiometricLogin = async () => {
    const hasHardware = await LocalAuthentication.hasHardwareAsync();
    const isEnrolled = await LocalAuthentication.isEnrolledAsync();
    
    if (!hasHardware || !isEnrolled) {
      Alert.alert(
        'Not Available',
        'Biometric authentication is not available on this device'
      );
      return;
    }

    const result = await LocalAuthentication.authenticateAsync({
      promptMessage: 'Authenticate to access SchoolOps',
      cancelLabel: 'Use Password',
    });

    if (result.success) {
      // Restore session with mock parent user
      const mockUser = MOCK_USERS.parent;
      dispatch(loginUser({ 
        email: mockUser.email, 
        password: 'biometric-auth' 
      }));
      router.replace('/(app)/home');
    }
  };

  const handleDemoLogin = async (role: string) => {
    let mockUser;
    switch (role) {
      case 'admin':
        mockUser = MOCK_USERS.admin;
        break;
      case 'teacher':
        mockUser = MOCK_USERS.teacher;
        break;
      case 'student':
        mockUser = MOCK_USERS.student;
        break;
      case 'parent':
        mockUser = MOCK_USERS.parent;
        break;
      default:
        mockUser = MOCK_USERS.teacher;
    }
    
    await dispatch(loginUser({ email: mockUser.email, password: 'demo' }));
    router.replace('/(app)/home');
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Logo and Title */}
        <View style={styles.logoContainer}>
          <View style={styles.logoCircle}>
            <Text style={styles.logoText}>S</Text>
          </View>
          <Text style={styles.title}>SchoolOps</Text>
          <Text style={styles.subtitle}>Smart School Management</Text>
        </View>

        {/* Login Form */}
        <Surface style={styles.formCard} elevation={2}>
          <Text style={styles.formTitle}>Welcome Back</Text>
          <Text style={styles.formSubtitle}>Sign in to continue</Text>

          {error && (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          )}

          <TextInput
            label="Email"
            value={email}
            onChangeText={setEmail}
            mode="outlined"
            style={styles.input}
            keyboardType="email-address"
            autoCapitalize="none"
            left={<TextInput.Icon icon="email-outline" />}
          />

          <TextInput
            label="Password"
            value={password}
            onChangeText={setPassword}
            mode="outlined"
            style={styles.input}
            secureTextEntry={!showPassword}
            left={<TextInput.Icon icon="lock-outline" />}
            right={
              <TextInput.Icon
                icon={showPassword ? 'eye-off' : 'eye'}
                onPress={() => setShowPassword(!showPassword)}
              />
            }
          />

          <TouchableOpacity style={styles.forgotPassword}>
            <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
          </TouchableOpacity>

          <Button
            mode="contained"
            onPress={handleLogin}
            style={styles.loginButton}
            contentStyle={styles.loginButtonContent}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              'Sign In'
            )}
          </Button>

          <View style={styles.divider}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>or continue with</Text>
            <View style={styles.dividerLine} />
          </View>

          <TouchableOpacity
            style={styles.biometricButton}
            onPress={handleBiometricLogin}
          >
            <Ionicons name="finger-print" size={28} color="#4F46E5" />
            <Text style={styles.biometricText}>Use Biometrics</Text>
          </TouchableOpacity>
        </Surface>

        {/* Demo Login Options */}
        <View style={styles.demoSection}>
          <Text style={styles.demoTitle}>Quick Demo Access</Text>
          <View style={styles.demoButtons}>
            <TouchableOpacity
              style={[styles.demoButton, { backgroundColor: '#4F46E5' }]}
              onPress={() => handleDemoLogin('student')}
            >
              <Text style={styles.demoButtonText}>Student</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.demoButton, { backgroundColor: '#10B981' }]}
              onPress={() => handleDemoLogin('parent')}
            >
              <Text style={styles.demoButtonText}>Parent</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.demoButton, { backgroundColor: '#F59E0B' }]}
              onPress={() => handleDemoLogin('teacher')}
            >
              <Text style={styles.demoButtonText}>Teacher</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.demoButton, { backgroundColor: '#8B5CF6' }]}
              onPress={() => handleDemoLogin('admin')}
            >
              <Text style={styles.demoButtonText}>Admin</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Footer */}
        <Text style={styles.footer}>
          Don't have an account?{' '}
          <Text style={styles.footerLink}>Contact School</Text>
        </Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 40,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 32,
  },
  logoCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#4F46E5',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  logoText: {
    fontSize: 40,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
  },
  formCard: {
    padding: 24,
    borderRadius: 16,
    backgroundColor: '#FFFFFF',
  },
  formTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  formSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 24,
  },
  errorContainer: {
    backgroundColor: '#FEE2E2',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  errorText: {
    color: '#EF4444',
    fontSize: 14,
  },
  input: {
    marginBottom: 12,
    backgroundColor: '#FFFFFF',
  },
  forgotPassword: {
    alignSelf: 'flex-end',
    marginBottom: 16,
  },
  forgotPasswordText: {
    color: '#4F46E5',
    fontSize: 14,
  },
  loginButton: {
    marginTop: 8,
    borderRadius: 12,
  },
  loginButtonContent: {
    paddingVertical: 8,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 24,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#E5E7EB',
  },
  dividerText: {
    marginHorizontal: 16,
    color: '#9CA3AF',
    fontSize: 14,
  },
  biometricButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 12,
  },
  biometricText: {
    marginLeft: 8,
    color: '#4F46E5',
    fontSize: 16,
    fontWeight: '600',
  },
  demoSection: {
    marginTop: 24,
  },
  demoTitle: {
    textAlign: 'center',
    color: '#6B7280',
    fontSize: 14,
    marginBottom: 12,
  },
  demoButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 8,
  },
  demoButton: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
  },
  demoButtonText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  footer: {
    textAlign: 'center',
    color: '#6B7280',
    marginTop: 24,
    fontSize: 14,
  },
  footerLink: {
    color: '#4F46E5',
    fontWeight: '600',
  },
});
