import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  TextInput,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Coupon } from '../src/types/coupon';
import { getCouponById, updateCouponStatus, updateCoupon, deleteCoupon } from '../src/db/couponRepository';
import { cancelRemindersForCoupon } from '../src/services/notificationService';
import { getUrgencyLevel, getUrgencyColor, formatExpiryText } from '../src/utils/expiry';

export default function CouponDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [coupon, setCoupon] = useState<Coupon | null>(null);
  const [editingNotes, setEditingNotes] = useState(false);
  const [notes, setNotes] = useState('');

  useEffect(() => {
    loadCoupon();
  }, [id]);

  const loadCoupon = async () => {
    if (!id) return;
    const data = await getCouponById(id);
    setCoupon(data);
    setNotes(data?.notes || '');
  };

  if (!coupon) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  const urgency = getUrgencyLevel(coupon.expirationDate);
  const urgencyColor = getUrgencyColor(urgency);
  const expiryText = formatExpiryText(coupon.expirationDate, coupon.expirationDisplayText);

  const handleMarkUsed = () => {
    Alert.alert('Mark as Used', 'This coupon will be moved to your used history.', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Mark Used',
        onPress: async () => {
          await updateCouponStatus(coupon.id, 'used');
          await cancelRemindersForCoupon(coupon.id);
          router.back();
        },
      },
    ]);
  };

  const handleArchive = () => {
    Alert.alert('Archive Coupon', 'This coupon will be hidden from your vault.', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Archive',
        onPress: async () => {
          await updateCouponStatus(coupon.id, 'archived');
          await cancelRemindersForCoupon(coupon.id);
          router.back();
        },
      },
    ]);
  };

  const handleDelete = () => {
    Alert.alert('Delete Coupon', 'This cannot be undone.', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: async () => {
          await deleteCoupon(coupon.id);
          await cancelRemindersForCoupon(coupon.id);
          router.back();
        },
      },
    ]);
  };

  const handleSaveNotes = async () => {
    await updateCoupon(coupon.id, { notes });
    setEditingNotes(false);
    loadCoupon();
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.card}>
        <View style={[styles.urgencyBar, { backgroundColor: urgencyColor }]} />

        <Text style={styles.storeName}>{coupon.storeName}</Text>
        <Text style={styles.discount}>{coupon.discountDescription}</Text>

        <View style={styles.metaRow}>
          <Text style={[styles.expiryBadge, { color: urgencyColor }]}>{expiryText}</Text>
        </View>

        {coupon.couponCode && (
          <View style={styles.codeSection}>
            <Text style={styles.codeLabel}>Coupon Code</Text>
            <View style={styles.codeBox}>
              <Text style={styles.codeValue}>{coupon.couponCode}</Text>
            </View>
          </View>
        )}

        {coupon.minimumPurchase != null && (
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Minimum Purchase</Text>
            <Text style={styles.detailValue}>${coupon.minimumPurchase.toFixed(2)}</Text>
          </View>
        )}

        {coupon.productCategories.length > 0 && coupon.productCategories[0] !== 'any' && (
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Applies To</Text>
            <Text style={styles.detailValue}>{coupon.productCategories.join(', ')}</Text>
          </View>
        )}

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Source</Text>
          <Text style={styles.detailValue}>
            {coupon.sourceType === 'image' ? 'Photo' : coupon.sourceType === 'email' ? 'Pasted text' : 'Manual entry'}
          </Text>
        </View>

        {coupon.extractionConfidence < 0.7 && (
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>
              Low confidence extraction — please verify the details above are correct.
            </Text>
          </View>
        )}

        {/* Notes section */}
        <View style={styles.notesSection}>
          <View style={styles.notesHeader}>
            <Text style={styles.detailLabel}>Notes</Text>
            {!editingNotes && (
              <TouchableOpacity onPress={() => setEditingNotes(true)}>
                <Text style={styles.editText}>Edit</Text>
              </TouchableOpacity>
            )}
          </View>
          {editingNotes ? (
            <View>
              <TextInput
                style={styles.notesInput}
                multiline
                value={notes}
                onChangeText={setNotes}
                placeholder="Add notes..."
                placeholderTextColor="#9CA3AF"
              />
              <TouchableOpacity style={styles.saveNotesButton} onPress={handleSaveNotes}>
                <Text style={styles.saveNotesText}>Save Notes</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <Text style={styles.notesText}>{coupon.notes || 'No notes'}</Text>
          )}
        </View>
      </View>

      {/* Actions */}
      <View style={styles.actions}>
        <TouchableOpacity style={styles.usedButton} onPress={handleMarkUsed}>
          <Text style={styles.usedButtonText}>Mark as Used</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.archiveButton} onPress={handleArchive}>
          <Text style={styles.archiveButtonText}>Archive</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.deleteButton} onPress={handleDelete}>
          <Text style={styles.deleteButtonText}>Delete</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    paddingTop: 56,
    paddingHorizontal: 20,
    paddingBottom: 8,
    backgroundColor: '#FFFFFF',
  },
  backButton: {
    paddingVertical: 8,
  },
  backText: {
    fontSize: 16,
    color: '#4F46E5',
    fontWeight: '500',
  },
  loadingText: {
    textAlign: 'center',
    marginTop: 100,
    fontSize: 16,
    color: '#9CA3AF',
  },
  card: {
    backgroundColor: '#FFFFFF',
    margin: 16,
    borderRadius: 14,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 3,
    overflow: 'hidden',
  },
  urgencyBar: {
    height: 4,
    borderRadius: 2,
    marginBottom: 16,
  },
  storeName: {
    fontSize: 24,
    fontWeight: '800',
    color: '#1F2937',
    marginBottom: 6,
  },
  discount: {
    fontSize: 18,
    color: '#374151',
    lineHeight: 26,
    marginBottom: 12,
  },
  metaRow: {
    marginBottom: 20,
  },
  expiryBadge: {
    fontSize: 14,
    fontWeight: '600',
  },
  codeSection: {
    marginBottom: 16,
  },
  codeLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6B7280',
    textTransform: 'uppercase',
    marginBottom: 6,
  },
  codeBox: {
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  codeValue: {
    fontSize: 20,
    fontWeight: '700',
    color: '#4F46E5',
    fontFamily: 'monospace',
    letterSpacing: 2,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
  },
  detailLabel: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '500',
  },
  detailValue: {
    fontSize: 14,
    color: '#1F2937',
    fontWeight: '500',
    flex: 1,
    textAlign: 'right',
    marginLeft: 16,
  },
  warningBox: {
    backgroundColor: '#FEF3C7',
    padding: 12,
    borderRadius: 8,
    marginTop: 12,
  },
  warningText: {
    fontSize: 13,
    color: '#92400E',
    lineHeight: 18,
  },
  notesSection: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
  },
  notesHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  editText: {
    fontSize: 14,
    color: '#4F46E5',
    fontWeight: '500',
  },
  notesText: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
  },
  notesInput: {
    backgroundColor: '#F9FAFB',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: '#1F2937',
    minHeight: 80,
    textAlignVertical: 'top',
  },
  saveNotesButton: {
    marginTop: 8,
    alignSelf: 'flex-end',
    backgroundColor: '#4F46E5',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  saveNotesText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '600',
  },
  actions: {
    paddingHorizontal: 16,
    paddingBottom: 40,
    gap: 10,
  },
  usedButton: {
    backgroundColor: '#4F46E5',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
  },
  usedButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  archiveButton: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#D1D5DB',
  },
  archiveButtonText: {
    color: '#374151',
    fontSize: 16,
    fontWeight: '600',
  },
  deleteButton: {
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
  },
  deleteButtonText: {
    color: '#EF4444',
    fontSize: 15,
    fontWeight: '500',
  },
});
