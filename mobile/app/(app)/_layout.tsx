import { Tabs } from 'expo-router';
import { View, StyleSheet } from 'react-native';
import { Text, useTheme, Avatar } from 'react-native-paper';
import { useSelector } from 'react-redux';
import { RootState } from '../../store/store';
import { getInitials } from '../../utils/helpers';

const TAB_SCREENS = [
  {
    name: 'home',
    title: 'Home',
    icon: 'view-dashboard-outline',
  },
  {
    name: 'academics',
    title: 'Academics',
    icon: 'school-outline',
  },
  {
    name: 'fees',
    title: 'Fees',
    icon: 'cash-outline',
  },
  {
    name: 'chat',
    title: 'Messages',
    icon: 'chat-outline',
  },
  {
    name: 'profile',
    title: 'Profile',
    icon: 'account-outline',
  },
];

export default function AppLayout() {
  const theme = useTheme();
  const { user } = useSelector((state: RootState) => state.auth);

  return (
    <Tabs
      screenOptions={{
        headerShown: true,
        headerStyle: {
          backgroundColor: theme.colors.primary,
        },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
        headerRight: () => (
          <View style={styles.headerRight}>
            <View style={styles.notificationBadge}>
              <Text style={styles.badgeText}>3</Text>
            </View>
          </View>
        ),
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopWidth: 1,
          borderTopColor: '#E5E7EB',
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: '#9CA3AF',
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
        },
        tabBarIconStyle: {
          marginBottom: 2,
        },
      }}
    >
      {TAB_SCREENS.map((screen) => (
        <Tabs.Screen
          key={screen.name}
          name={screen.name}
          options={{
            title: screen.title,
            tabBarIcon: ({ color, focused }) => (
              <View style={styles.tabIconContainer}>
                <View style={[styles.iconWrapper, focused && styles.iconFocused]}>
                  <TabIcon icon={screen.icon} color={color} />
                </View>
              </View>
            ),
          }}
        />
      ))}
    </Tabs>
  );
}

const TabIcon = ({ icon, color }: { icon: string; color: string }) => {
  // Using a simple text fallback since we don't have the icons package imported
  return <Text style={{ fontSize: 22, color }}>●</Text>;
};

const styles = StyleSheet.create({
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  notificationBadge: {
    backgroundColor: '#EF4444',
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 6,
  },
  badgeText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: 'bold',
  },
  tabIconContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconWrapper: {
    padding: 4,
    borderRadius: 8,
  },
  iconFocused: {
    backgroundColor: 'rgba(79, 70, 229, 0.1)',
  },
});
