import React from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Linking,
} from 'react-native';
import {
  Text,
  Avatar,
  Card,
  Button,
  IconButton,
  Surface,
  Divider,
} from 'react-native-paper';
import { useRouter } from 'expo-router';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../../store/store';
import { logoutUser } from '../../store/slices/authSlice';
import { getInitials } from '../../utils/helpers';
import { COLORS } from '../../theme';

type MenuItem = {
  id: string;
  title: string;
  subtitle?: string;
  icon: string;
  onPress: () => void;
  showDivider?: boolean;
};

export default function ProfileScreen() {
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();
  const { user } = useSelector((state: RootState) => state.auth);

  const handleLogout = async () => {
    await dispatch(logoutUser());
    router.replace('/(auth)/login');
  };

  const handleSupport = () => {
    Linking.openURL('mailto:support@schoolops.com');
  };

  if (!user) return null;

  const menuItems: MenuItem[] = [
    {
      id: 'edit-profile',
      title: 'Edit Profile',
      subtitle: 'Update your personal information',
      icon: 'account-edit',
      onPress: () => router.push('/(app)/profile/edit' as any),
    },
    {
      id: 'notifications',
      title: 'Notifications',
      subtitle: 'Manage notification preferences',
      icon: 'bell-outline',
      onPress: () => router.push('/(app)/profile/notifications' as any),
    },
    {
      id: 'security',
      title: 'Security',
      subtitle: 'Password, PIN, Biometrics',
      icon: 'shield-lock-outline',
      onPress: () => router.push('/(app)/profile/security' as any),
      showDivider: true,
    },
    {
      id: 'school-info',
      title: 'School Information',
      subtitle: 'View school details',
      icon: 'school',
      onPress: () => router.push('/(app)/profile/school' as any),
    },
    {
      id: 'help',
      title: 'Help & Support',
      subtitle: 'FAQs, Contact us',
      icon: 'help-circle-outline',
      onPress: handleSupport,
    },
    {
      id: 'about',
      title: 'About',
      subtitle: 'Version 1.0.0',
      icon: 'information-outline',
      onPress: () => router.push('/(app)/profile/about' as any),
      showDivider: true,
    },
    {
      id: 'logout',
      title: 'Logout',
      icon: 'logout',
      onPress: handleLogout,
    },
  ];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Profile Header */}
      <Card style={styles.headerCard} mode="elevated">
        <Card.Content style={styles.headerContent}>
          <Avatar.Text
            size={80}
            label={getInitials(user.firstName, user.lastName)}
            style={styles.avatar}
          />
          <Text style={styles.userName}>
            {user.firstName} {user.lastName}
          </Text>
          <Text style={styles.userEmail}>{user.email}</Text>
          <View style={styles.roleBadge}>
            <Text style={styles.roleText}>{user.role.toUpperCase()}</Text>
          </View>

          <TouchableOpacity
            style={styles.editButton}
            onPress={() => router.push('/(app)/profile/edit' as any)}
          >
            <Text style={styles.editButtonText}>Edit Profile</Text>
          </TouchableOpacity>
        </Card.Content>
      </Card>

      {/* Quick Stats */}
      <View style={styles.statsRow}>
        <Card style={styles.statCard} mode="elevated">
          <Card.Content style={styles.statContent}>
            <Text style={styles.statValue}>94%</Text>
            <Text style={styles.statLabel}>Attendance</Text>
          </Card.Content>
        </Card>
        <Card style={styles.statCard} mode="elevated">
          <Card.Content style={styles.statContent}>
            <Text style={styles.statValue}>A-</Text>
            <Text style={styles.statLabel}>Avg Grade</Text>
          </Card.Content>
        </Card>
        <Card style={styles.statCard} mode="elevated">
          <Card.Content style={styles.statContent}>
            <Text style={styles.statValue}>12</Text>
            <Text style={styles.statLabel}>Days Left</Text>
          </Card.Content>
        </Card>
      </View>

      {/* Menu Items */}
      <Card style={styles.menuCard} mode="elevated">
        {menuItems.map((item, index) => (
          <React.Fragment key={item.id}>
            <TouchableOpacity style={styles.menuItem} onPress={item.onPress}>
              <View style={styles.menuItemLeft}>
                <View style={[styles.menuIcon, { backgroundColor: COLORS.primary + '15' }]}>
                  <Text style={styles.menuIconText}>{item.icon.charAt(0).toUpperCase()}</Text>
                </View>
                <View>
                  <Text style={styles.menuTitle}>{item.title}</Text>
                  {item.subtitle && (
                    <Text style={styles.menuSubtitle}>{item.subtitle}</Text>
                  )}
                </View>
              </View>
              <IconButton icon="chevron-right" size={20} color="#9CA3AF" />
            </TouchableOpacity>
            {item.showDivider && <Divider style={styles.divider} />}
          </React.Fragment>
        ))}
      </Card>

      {/* App Info */}
      <View style={styles.appInfo}>
        <Text style={styles.appName}>SchoolOps</Text>
        <Text style={styles.appVersion}>Version 1.0.0</Text>
        <Text style={styles.appCopyright}>© 2024 SchoolOps. All rights reserved.</Text>
      </View>

      {/* Bottom padding */}
      <View style={styles.bottomPadding} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  content: {
    padding: 16,
  },
  headerCard: {
    borderRadius: 16,
    marginBottom: 16,
  },
  headerContent: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  avatar: {
    backgroundColor: COLORS.primary + '20',
    marginBottom: 16,
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  userEmail: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  roleBadge: {
    backgroundColor: COLORS.primary + '20',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 16,
    marginTop: 12,
  },
  roleText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  editButton: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: 24,
    paddingVertical: 10,
    borderRadius: 20,
    marginTop: 16,
  },
  editButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
    gap: 12,
  },
  statCard: {
    flex: 1,
    borderRadius: 12,
  },
  statContent: {
    alignItems: 'center',
    padding: 12,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  statLabel: {
    fontSize: 11,
    color: '#6B7280',
    marginTop: 4,
  },
  menuCard: {
    borderRadius: 12,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
  menuItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  menuIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  menuIconText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  menuTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1F2937',
  },
  menuSubtitle: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  divider: {
    marginHorizontal: 16,
  },
  appInfo: {
    alignItems: 'center',
    marginTop: 24,
    marginBottom: 16,
  },
  appName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  appVersion: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  appCopyright: {
    fontSize: 10,
    color: '#9CA3AF',
    marginTop: 4,
  },
  bottomPadding: {
    height: 20,
  },
});
