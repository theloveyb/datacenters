import * as Notifications from 'expo-notifications';
import { Coupon } from '../types/coupon';
import { getExpiringCoupons } from '../db/couponRepository';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

export async function requestNotificationPermissions(): Promise<boolean> {
  const { status: existing } = await Notifications.getPermissionsAsync();
  if (existing === 'granted') return true;

  const { status } = await Notifications.requestPermissionsAsync();
  return status === 'granted';
}

export async function scheduleExpiryReminder(coupon: Coupon): Promise<void> {
  if (!coupon.expirationDate) return;

  const expiry = new Date(coupon.expirationDate);
  const now = new Date();

  // Schedule reminder 2 days before expiry
  const twoDaysBefore = new Date(expiry.getTime() - 2 * 24 * 60 * 60 * 1000);
  if (twoDaysBefore > now) {
    await Notifications.scheduleNotificationAsync({
      content: {
        title: 'Coupon expiring soon',
        body: `Your ${coupon.storeName} coupon (${coupon.discountDescription}) expires in 2 days.`,
        data: { couponId: coupon.id, type: 'expiry_reminder' },
      },
      trigger: { type: Notifications.SchedulableTriggerInputTypes.DATE, date: twoDaysBefore },
    });
  }

  // Schedule final-day reminder
  const finalDay = new Date(expiry.getTime() - 8 * 60 * 60 * 1000); // morning of expiry day
  if (finalDay > now) {
    await Notifications.scheduleNotificationAsync({
      content: {
        title: 'Coupon expires today!',
        body: `Last chance! Your ${coupon.storeName} coupon (${coupon.discountDescription}) expires today.`,
        data: { couponId: coupon.id, type: 'expiry_final' },
      },
      trigger: { type: Notifications.SchedulableTriggerInputTypes.DATE, date: finalDay },
    });
  }
}

export async function cancelRemindersForCoupon(couponId: string): Promise<void> {
  const scheduled = await Notifications.getAllScheduledNotificationsAsync();
  for (const notification of scheduled) {
    if (notification.content.data?.couponId === couponId) {
      await Notifications.cancelScheduledNotificationAsync(notification.identifier);
    }
  }
}

export async function refreshAllReminders(): Promise<void> {
  // Cancel all existing coupon reminders
  await Notifications.cancelAllScheduledNotificationsAsync();

  // Re-schedule for all active coupons expiring within 14 days
  const expiring = await getExpiringCoupons(14);
  for (const coupon of expiring) {
    await scheduleExpiryReminder(coupon);
  }
}
