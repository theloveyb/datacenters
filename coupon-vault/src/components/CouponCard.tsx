import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Coupon } from '../types/coupon';
import { getUrgencyLevel, getUrgencyColor, formatExpiryText } from '../utils/expiry';

interface CouponCardProps {
  coupon: Coupon;
  onPress: (coupon: Coupon) => void;
  onMarkUsed: (coupon: Coupon) => void;
}

export function CouponCard({ coupon, onPress, onMarkUsed }: CouponCardProps) {
  const urgency = getUrgencyLevel(coupon.expirationDate);
  const urgencyColor = getUrgencyColor(urgency);
  const expiryText = formatExpiryText(coupon.expirationDate, coupon.expirationDisplayText);

  return (
    <TouchableOpacity style={styles.card} onPress={() => onPress(coupon)} activeOpacity={0.7}>
      <View style={[styles.urgencyStripe, { backgroundColor: urgencyColor }]} />
      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.storeName} numberOfLines={1}>
            {coupon.storeName}
          </Text>
          {coupon.couponCode && (
            <View style={styles.codeBadge}>
              <Text style={styles.codeText}>{coupon.couponCode}</Text>
            </View>
          )}
        </View>

        <Text style={styles.discount} numberOfLines={2}>
          {coupon.discountDescription}
        </Text>

        <View style={styles.footer}>
          <Text style={[styles.expiry, { color: urgencyColor }]}>{expiryText}</Text>
          <TouchableOpacity
            style={styles.usedButton}
            onPress={() => onMarkUsed(coupon)}
            hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
          >
            <Text style={styles.usedButtonText}>Mark Used</Text>
          </TouchableOpacity>
        </View>

        {coupon.extractionConfidence < 0.7 && (
          <View style={styles.reviewBadge}>
            <Text style={styles.reviewText}>Needs review</Text>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginHorizontal: 16,
    marginVertical: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
    overflow: 'hidden',
  },
  urgencyStripe: {
    width: 4,
  },
  content: {
    flex: 1,
    padding: 14,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  storeName: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1F2937',
    flex: 1,
  },
  codeBadge: {
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    marginLeft: 8,
  },
  codeText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#4F46E5',
    fontFamily: 'monospace',
  },
  discount: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 8,
    lineHeight: 20,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  expiry: {
    fontSize: 13,
    fontWeight: '500',
  },
  usedButton: {
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 6,
    backgroundColor: '#F3F4F6',
  },
  usedButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6B7280',
  },
  reviewBadge: {
    marginTop: 8,
    alignSelf: 'flex-start',
    backgroundColor: '#FEF3C7',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
  },
  reviewText: {
    fontSize: 11,
    color: '#92400E',
    fontWeight: '500',
  },
});
