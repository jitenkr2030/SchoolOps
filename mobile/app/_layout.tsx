import { Stack } from 'expo-router';
import { Provider } from 'react-redux';
import { PaperProvider } from 'react-native-paper';
import { store } from '../store/store';
import { theme } from '../theme';
import { useEffect } from 'react';
import * as Notifications from 'expo-notifications';

export default function RootLayout() {
  useEffect(() => {
    // Set up notification handler
    Notifications.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: true,
      }),
    });

    // Register for push notifications
    registerForPushNotifications();
  }, []);

  const registerForPushNotifications = async () => {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
  };

  return (
    <Provider store={store}>
      <PaperProvider theme={theme}>
        <Stack
          screenOptions={{
            headerShown: false,
            animation: 'slide_from_right',
          }}
        >
          <Stack.Screen name="(auth)" />
          <Stack.Screen name="(app)" />
        </Stack>
      </PaperProvider>
    </Provider>
  );
}
