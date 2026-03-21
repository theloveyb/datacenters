import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';
import { useRouter } from 'expo-router';
import { extractFromImage, extractFromText, buildManualCoupon } from '../../src/services/extractionService';
import { insertCoupon } from '../../src/db/couponRepository';
import { scheduleExpiryReminder } from '../../src/services/notificationService';
import { ExtractionResult } from '../../src/types/coupon';

type CaptureMode = 'photo' | 'text' | 'manual';

export default function CaptureScreen() {
  const router = useRouter();
  const [mode, setMode] = useState<CaptureMode>('photo');
  const [loading, setLoading] = useState(false);
  const [pastedText, setPastedText] = useState('');

  // Manual entry fields
  const [manualStore, setManualStore] = useState('');
  const [manualDiscount, setManualDiscount] = useState('');
  const [manualCode, setManualCode] = useState('');
  const [manualExpiry, setManualExpiry] = useState('');
  const [manualCategories, setManualCategories] = useState('');

  const handlePhotoCapture = async () => {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Permission needed', 'Camera access is required to photograph coupons.');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      quality: 0.8,
      base64: true,
    });

    if (result.canceled || !result.assets[0]) return;

    setLoading(true);
    try {
      const base64 = result.assets[0].base64 || '';
      const extraction = await extractFromImage(base64);
      await saveCoupons(extraction.coupons, 'image', result.assets[0].uri);
    } catch (error) {
      Alert.alert('Extraction failed', 'Could not extract coupon data from the photo. Try manual entry.');
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoFromGallery = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Permission needed', 'Photo library access is required.');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      quality: 0.8,
      base64: true,
    });

    if (result.canceled || !result.assets[0]) return;

    setLoading(true);
    try {
      const base64 = result.assets[0].base64 || '';
      const extraction = await extractFromImage(base64);
      await saveCoupons(extraction.coupons, 'image', result.assets[0].uri);
    } catch (error) {
      Alert.alert('Extraction failed', 'Could not extract coupon data. Try manual entry.');
    } finally {
      setLoading(false);
    }
  };

  const handleTextExtraction = async () => {
    if (!pastedText.trim()) {
      Alert.alert('Empty input', 'Please paste or type coupon text first.');
      return;
    }

    setLoading(true);
    try {
      const extraction = await extractFromText(pastedText);
      await saveCoupons(extraction.coupons, 'email', null, pastedText);
    } catch (error) {
      Alert.alert('Extraction failed', 'Could not extract coupon data from text. Try manual entry.');
    } finally {
      setLoading(false);
    }
  };

  const handleManualEntry = async () => {
    if (!manualStore.trim() || !manualDiscount.trim()) {
      Alert.alert('Required fields', 'Store name and discount description are required.');
      return;
    }

    const extraction = buildManualCoupon({
      storeName: manualStore.trim(),
      discountDescription: manualDiscount.trim(),
      couponCode: manualCode.trim() || undefined,
      expirationDate: manualExpiry.trim() ? new Date(manualExpiry.trim()).toISOString() : undefined,
      productCategories: manualCategories
        .split(',')
        .map((c) => c.trim())
        .filter(Boolean),
    });

    await saveCoupons([extraction], 'manual');
  };

  const saveCoupons = async (
    results: ExtractionResult[],
    sourceType: 'image' | 'email' | 'manual',
    sourceUri?: string | null,
    sourceText?: string | null
  ) => {
    if (results.length === 0) {
      Alert.alert('No coupons found', 'Could not identify any coupons. Try manual entry.');
      return;
    }

    let savedCount = 0;
    for (const result of results) {
      if (!result.storeName || !result.discountDescription) continue;

      const coupon = await insertCoupon({
        sourceType,
        rawSourceUri: sourceUri || null,
        rawSourceText: sourceText || null,
        storeName: result.storeName,
        storeId: null,
        discountDescription: result.discountDescription,
        discountType: result.discountType || 'other',
        discountValue: result.discountValue,
        minimumPurchase: result.minimumPurchase,
        expirationDate: result.expirationDate,
        expirationDisplayText: result.expirationDisplayText,
        dateConfidence: result.dateConfidence,
        productCategories: result.productCategories || ['any'],
        couponCode: result.couponCode,
        status: 'active',
        extractionConfidence: result.extractionConfidence,
        notes: result.conditions,
      });

      await scheduleExpiryReminder(coupon);
      savedCount++;
    }

    const message =
      savedCount === 1
        ? `Saved 1 coupon for ${results[0].storeName}.`
        : `Saved ${savedCount} coupons.`;

    Alert.alert('Coupon saved', message, [
      { text: 'Add Another', style: 'cancel' },
      { text: 'View Vault', onPress: () => router.push('/(tabs)/') },
    ]);

    // Reset fields
    setPastedText('');
    setManualStore('');
    setManualDiscount('');
    setManualCode('');
    setManualExpiry('');
    setManualCategories('');
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.headerSection}>
          <Text style={styles.title}>Add Coupon</Text>
          <Text style={styles.subtitle}>Photo, paste, or type it in</Text>
        </View>

        {/* Mode Selector */}
        <View style={styles.modeSelector}>
          {(['photo', 'text', 'manual'] as CaptureMode[]).map((m) => (
            <TouchableOpacity
              key={m}
              style={[styles.modeTab, mode === m && styles.modeTabActive]}
              onPress={() => setMode(m)}
            >
              <Text style={[styles.modeTabText, mode === m && styles.modeTabTextActive]}>
                {m === 'photo' ? 'Photo' : m === 'text' ? 'Paste Text' : 'Manual'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {loading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#4F46E5" />
            <Text style={styles.loadingText}>Extracting coupon details...</Text>
          </View>
        )}

        {!loading && mode === 'photo' && (
          <View style={styles.section}>
            <Text style={styles.sectionText}>
              Take a photo of a coupon or select one from your gallery. The AI will extract the
              details automatically.
            </Text>
            <TouchableOpacity style={styles.primaryButton} onPress={handlePhotoCapture}>
              <Text style={styles.primaryButtonText}>Take Photo</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.secondaryButton} onPress={handlePhotoFromGallery}>
              <Text style={styles.secondaryButtonText}>Choose from Gallery</Text>
            </TouchableOpacity>
          </View>
        )}

        {!loading && mode === 'text' && (
          <View style={styles.section}>
            <Text style={styles.sectionText}>
              Paste the email, promo text, or coupon code below. Include as much context as possible
              for better extraction.
            </Text>
            <TextInput
              style={styles.textArea}
              multiline
              numberOfLines={8}
              placeholder="Paste coupon text, email content, or promo code here..."
              placeholderTextColor="#9CA3AF"
              value={pastedText}
              onChangeText={setPastedText}
              textAlignVertical="top"
            />
            <TouchableOpacity style={styles.primaryButton} onPress={handleTextExtraction}>
              <Text style={styles.primaryButtonText}>Extract Coupon</Text>
            </TouchableOpacity>
          </View>
        )}

        {!loading && mode === 'manual' && (
          <View style={styles.section}>
            <Text style={styles.label}>Store Name *</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g., Target, Amazon"
              placeholderTextColor="#9CA3AF"
              value={manualStore}
              onChangeText={setManualStore}
            />

            <Text style={styles.label}>Discount Description *</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g., $5 off $25 purchase"
              placeholderTextColor="#9CA3AF"
              value={manualDiscount}
              onChangeText={setManualDiscount}
            />

            <Text style={styles.label}>Coupon Code</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g., SAVE20"
              placeholderTextColor="#9CA3AF"
              value={manualCode}
              onChangeText={setManualCode}
              autoCapitalize="characters"
            />

            <Text style={styles.label}>Expiration Date</Text>
            <TextInput
              style={styles.input}
              placeholder="YYYY-MM-DD"
              placeholderTextColor="#9CA3AF"
              value={manualExpiry}
              onChangeText={setManualExpiry}
            />

            <Text style={styles.label}>Product Categories</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g., groceries, laundry, any (comma-separated)"
              placeholderTextColor="#9CA3AF"
              value={manualCategories}
              onChangeText={setManualCategories}
            />

            <TouchableOpacity style={styles.primaryButton} onPress={handleManualEntry}>
              <Text style={styles.primaryButtonText}>Save Coupon</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  scroll: {
    flexGrow: 1,
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
  modeSelector: {
    flexDirection: 'row',
    padding: 6,
    margin: 16,
    backgroundColor: '#E5E7EB',
    borderRadius: 10,
  },
  modeTab: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 8,
  },
  modeTabActive: {
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 1,
  },
  modeTabText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6B7280',
  },
  modeTabTextActive: {
    color: '#4F46E5',
    fontWeight: '600',
  },
  section: {
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  sectionText: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
    marginBottom: 20,
  },
  loadingContainer: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 15,
    color: '#4F46E5',
    fontWeight: '500',
  },
  primaryButton: {
    backgroundColor: '#4F46E5',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 12,
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  secondaryButton: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#D1D5DB',
  },
  secondaryButtonText: {
    color: '#374151',
    fontSize: 16,
    fontWeight: '600',
  },
  textArea: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 10,
    padding: 14,
    fontSize: 15,
    color: '#1F2937',
    minHeight: 160,
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 6,
    marginTop: 12,
  },
  input: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 11,
    fontSize: 15,
    color: '#1F2937',
  },
});
