export type DiscountType = 'fixed_amount' | 'percentage' | 'bogo' | 'free_item' | 'other';

export type CouponStatus = 'active' | 'used' | 'expired' | 'archived';

export type SourceType = 'image' | 'email' | 'manual';

export type DateConfidence = 'high' | 'medium' | 'low';

export interface Coupon {
  id: string;
  sourceType: SourceType;
  rawSourceUri: string | null;
  rawSourceText: string | null;
  storeName: string;
  storeId: string | null;
  discountDescription: string;
  discountType: DiscountType;
  discountValue: number | null;
  minimumPurchase: number | null;
  expirationDate: string | null; // ISO 8601
  expirationDisplayText: string | null; // for ambiguous dates like "end of March"
  dateConfidence: DateConfidence;
  productCategories: string[];
  couponCode: string | null;
  status: CouponStatus;
  extractionConfidence: number; // 0.0 - 1.0
  notes: string | null;
  createdAt: string; // ISO 8601
  updatedAt: string; // ISO 8601
}

export interface Store {
  id: string;
  name: string;
  normalizedName: string;
  category: string | null;
  latitude: number | null;
  longitude: number | null;
  address: string | null;
}

export interface ShoppingListItem {
  id: string;
  description: string;
  isChecked: boolean;
  matchedCouponIds: string[];
  createdAt: string;
}

export interface ExtractionResult {
  storeName: string | null;
  discountDescription: string | null;
  discountType: DiscountType | null;
  discountValue: number | null;
  minimumPurchase: number | null;
  expirationDate: string | null;
  expirationDisplayText: string | null;
  dateConfidence: DateConfidence;
  productCategories: string[];
  couponCode: string | null;
  conditions: string | null;
  extractionConfidence: number;
}

export interface ExtractionResponse {
  coupons: ExtractionResult[];
  rawText?: string;
}
