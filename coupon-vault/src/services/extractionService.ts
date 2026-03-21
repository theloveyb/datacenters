import { ExtractionResult, ExtractionResponse } from '../types/coupon';

const EXTRACTION_API_URL = process.env.EXPO_PUBLIC_EXTRACTION_API_URL || 'http://localhost:3001/extract';

const EXTRACTION_PROMPT = `You are extracting coupon information from user-provided content.
Extract the following fields for each coupon found. If a field cannot be determined, return null — do not guess.

Fields to extract:
- store_name: The retailer or brand offering the discount.
- discount_description: A concise human-readable summary of the offer (e.g., "$5 off $25 purchase").
- discount_type: One of ["fixed_amount", "percentage", "bogo", "free_item", "other"].
- discount_value: The numeric discount value if applicable (just the number, e.g., 5 for $5 off, 20 for 20% off).
- minimum_purchase: Minimum spend required as a number, if stated.
- expiration_date: In ISO 8601 format (YYYY-MM-DDTHH:mm:ss.sssZ). If only a relative date is given (e.g., "valid this week"), compute based on today's date: {{current_date}}. If ambiguous, return your best estimate.
- expiration_display_text: The original text describing expiration, if it was ambiguous or informal.
- date_confidence: "high" if the date is explicitly stated, "medium" if inferred from context, "low" if guessing.
- product_categories: Array of product types or specific items this coupon applies to. Use ["any"] for store-wide coupons.
- coupon_code: The alphanumeric code to enter at checkout, if present.
- conditions: Any restrictions, limits, or fine print as a single string.
- extraction_confidence: Your overall confidence in this extraction from 0.0 to 1.0.

If the input contains multiple distinct coupon offers, return one object per offer.

Return valid JSON only in this format:
{ "coupons": [ { ...fields... } ] }`;

export async function extractFromImage(imageBase64: string): Promise<ExtractionResponse> {
  const currentDate = new Date().toISOString().split('T')[0];
  const prompt = EXTRACTION_PROMPT.replace('{{current_date}}', currentDate);

  try {
    const response = await fetch(EXTRACTION_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'image',
        content: imageBase64,
        prompt,
      }),
    });

    if (!response.ok) {
      throw new Error(`Extraction API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Image extraction failed:', error);
    return { coupons: [] };
  }
}

export async function extractFromText(text: string): Promise<ExtractionResponse> {
  const currentDate = new Date().toISOString().split('T')[0];
  const prompt = EXTRACTION_PROMPT.replace('{{current_date}}', currentDate);

  try {
    const response = await fetch(EXTRACTION_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'text',
        content: text,
        prompt,
      }),
    });

    if (!response.ok) {
      throw new Error(`Extraction API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Text extraction failed:', error);
    return { coupons: [] };
  }
}

export function buildManualCoupon(fields: {
  storeName: string;
  discountDescription: string;
  discountType?: ExtractionResult['discountType'];
  discountValue?: number;
  expirationDate?: string;
  couponCode?: string;
  productCategories?: string[];
}): ExtractionResult {
  return {
    storeName: fields.storeName,
    discountDescription: fields.discountDescription,
    discountType: fields.discountType || 'other',
    discountValue: fields.discountValue || null,
    minimumPurchase: null,
    expirationDate: fields.expirationDate || null,
    expirationDisplayText: null,
    dateConfidence: 'high',
    productCategories: fields.productCategories || ['any'],
    couponCode: fields.couponCode || null,
    conditions: null,
    extractionConfidence: 1.0,
  };
}
