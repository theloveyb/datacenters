import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  RefreshControl,
  TextInput,
} from 'react-native';
import { useFocusEffect } from 'expo-router';
import { Coupon, CouponStatus } from '../../src/types/coupon';
import { getAllActiveCoupons, updateCouponStatus } from '../../src/db/couponRepository';
import { cancelRemindersForCoupon } from '../../src/services/notificationService';
import { CouponCard } from '../../src/components/CouponCard';
import { EmptyState } from '../../src/components/EmptyState';
import { useRouter } from 'expo-router';

export default function VaultScreen() {
  const [coupons, setCoupons] = useState<Coupon[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState('');
  const router = useRouter();

  const loadCoupons = useCallback(async () => {
    try {
      const data = await getAllActiveCoupons();
      setCoupons(data);
    } catch (error) {
      console.error('Failed to load coupons:', error);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadCoupons();
    }, [loadCoupons])
  );

  const onRefresh = async () => {
    setRefreshing(true);
    await loadCoupons();
    setRefreshing(false);
  };

  const handleMarkUsed = (coupon: Coupon) => {
    Alert.alert(
      'Mark as Used',
      `Mark this ${coupon.storeName} coupon as used?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Mark Used',
          onPress: async () => {
            await updateCouponStatus(coupon.id, 'used');
            await cancelRemindersForCoupon(coupon.id);
            loadCoupons();
          },
        },
      ]
    );
  };

  const handleCouponPress = (coupon: Coupon) => {
    router.push({ pathname: '/coupon-detail', params: { id: coupon.id } });
  };

  const filteredCoupons = filter
    ? coupons.filter(
        (c) =>
          c.storeName.toLowerCase().includes(filter.toLowerCase()) ||
          c.discountDescription.toLowerCase().includes(filter.toLowerCase())
      )
    : coupons;

  return (
    <View style={styles.container}>
      <View style={styles.headerSection}>
        <Text style={styles.title}>My Coupons</Text>
        <Text style={styles.subtitle}>
          {coupons.length} active coupon{coupons.length !== 1 ? 's' : ''}
        </Text>
      </View>

      {coupons.length > 3 && (
        <View style={styles.searchContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="Filter by store or description..."
            placeholderTextColor="#9CA3AF"
            value={filter}
            onChangeText={setFilter}
          />
        </View>
      )}

      <FlatList
        data={filteredCoupons}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <CouponCard
            coupon={item}
            onPress={handleCouponPress}
            onMarkUsed={handleMarkUsed}
          />
        )}
        contentContainerStyle={filteredCoupons.length === 0 ? styles.emptyList : styles.list}
        ListEmptyComponent={
          <EmptyState
            title="No coupons yet"
            message="Add your first coupon by taking a photo, pasting a code, or entering it manually."
            actionLabel="Add Coupon"
            onAction={() => router.push('/(tabs)/capture')}
          />
        }
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#4F46E5" />
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  headerSection: {
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    color: '#1F2937',
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  searchContainer: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  searchInput: {
    backgroundColor: '#F3F4F6',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 15,
    color: '#1F2937',
  },
  list: {
    paddingVertical: 10,
  },
  emptyList: {
    flex: 1,
  },
});
