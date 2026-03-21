import { useEffect } from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'react-native';
import { requestNotificationPermissions, refreshAllReminders } from '../src/services/notificationService';

export default function RootLayout() {
  useEffect(() => {
    async function init() {
      await requestNotificationPermissions();
      await refreshAllReminders();
    }
    init();
  }, []);

  return (
    <>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(tabs)" />
        <Stack.Screen
          name="coupon-detail"
          options={{
            presentation: 'modal',
            animation: 'slide_from_bottom',
          }}
        />
      </Stack>
    </>
  );
}
