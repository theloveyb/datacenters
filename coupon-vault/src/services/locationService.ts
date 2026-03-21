import * as Location from 'expo-location';
import * as Notifications from 'expo-notifications';
import { getAllActiveCoupons } from '../db/couponRepository';

export async function requestLocationPermissions(): Promise<boolean> {
  const { status: foreground } = await Location.requestForegroundPermissionsAsync();
  if (foreground !== 'granted') return false;

  const { status: background } = await Location.requestBackgroundPermissionsAsync();
  return background === 'granted';
}

export async function getCurrentLocation(): Promise<Location.LocationObject | null> {
  try {
    const { status } = await Location.getForegroundPermissionsAsync();
    if (status !== 'granted') return null;

    return await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.Balanced,
    });
  } catch {
    return null;
  }
}

export async function checkNearbyCoupons(): Promise<void> {
  const location = await getCurrentLocation();
  if (!location) return;

  const coupons = await getAllActiveCoupons();
  const userLat = location.coords.latitude;
  const userLng = location.coords.longitude;

  // Group coupons by store and check if any stores are nearby
  const storeDistances = new Map<string, number>();

  for (const coupon of coupons) {
    // In a full implementation, we'd look up store locations.
    // For now, this is a placeholder that can be connected to a places API.
    // Store locations would come from the stores table.
  }
}

/**
 * Calculate distance between two coordinates in meters using Haversine formula.
 */
export function distanceBetween(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371e3; // Earth's radius in meters
  const toRad = (deg: number) => (deg * Math.PI) / 180;

  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;
}

const PROXIMITY_THRESHOLD_METERS = 300;

export async function startGeofenceMonitoring(): Promise<void> {
  const hasPermission = await requestLocationPermissions();
  if (!hasPermission) return;

  // Start background location task that checks proximity to stores
  // In production, this would use Location.startGeofencingAsync with
  // specific store coordinates from the database.
  // For v1, we use a simpler approach: periodic location checks.
  await Location.startLocationUpdatesAsync('COUPON_LOCATION_TASK', {
    accuracy: Location.Accuracy.Balanced,
    distanceInterval: 200, // Update every 200 meters
    deferredUpdatesInterval: 60000, // Or at least every minute
    showsBackgroundLocationIndicator: true,
    foregroundService: {
      notificationTitle: 'Coupon Vault',
      notificationBody: 'Watching for nearby stores with coupons',
    },
  });
}

export async function stopGeofenceMonitoring(): Promise<void> {
  const isRunning = await Location.hasStartedLocationUpdatesAsync('COUPON_LOCATION_TASK');
  if (isRunning) {
    await Location.stopLocationUpdatesAsync('COUPON_LOCATION_TASK');
  }
}
