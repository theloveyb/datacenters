import { getDatabase } from './database';
import { Coupon, CouponStatus } from '../types/coupon';
import { generateId } from '../utils/id';

function rowToCoupon(row: unknown): Coupon {
  const r = row as Record<string, unknown>;
  return {
    id: r.id as string,
    sourceType: r.source_type as Coupon['sourceType'],
    rawSourceUri: r.raw_source_uri as string | null,
    rawSourceText: r.raw_source_text as string | null,
    storeName: r.store_name as string,
    storeId: r.store_id as string | null,
    discountDescription: r.discount_description as string,
    discountType: r.discount_type as Coupon['discountType'],
    discountValue: r.discount_value as number | null,
    minimumPurchase: r.minimum_purchase as number | null,
    expirationDate: r.expiration_date as string | null,
    expirationDisplayText: r.expiration_display_text as string | null,
    dateConfidence: r.date_confidence as Coupon['dateConfidence'],
    productCategories: JSON.parse((r.product_categories as string) || '[]'),
    couponCode: r.coupon_code as string | null,
    status: r.status as CouponStatus,
    extractionConfidence: r.extraction_confidence as number,
    notes: r.notes as string | null,
    createdAt: r.created_at as string,
    updatedAt: r.updated_at as string,
  };
}

export async function getAllActiveCoupons(): Promise<Coupon[]> {
  const db = await getDatabase();
  // Auto-expire coupons past their expiration date
  const now = new Date().toISOString();
  await db.runAsync(
    `UPDATE coupons SET status = 'expired', updated_at = ? WHERE status = 'active' AND expiration_date IS NOT NULL AND expiration_date < ?`,
    [now, now]
  );
  const rows = await db.getAllAsync(
    `SELECT * FROM coupons WHERE status = 'active' ORDER BY expiration_date ASC NULLS LAST`
  );
  return rows.map(rowToCoupon);
}

export async function getCouponsByStore(storeName: string): Promise<Coupon[]> {
  const db = await getDatabase();
  const rows = await db.getAllAsync(
    `SELECT * FROM coupons WHERE status = 'active' AND LOWER(store_name) = LOWER(?) ORDER BY expiration_date ASC`,
    [storeName]
  );
  return rows.map(rowToCoupon);
}

export async function getCouponById(id: string): Promise<Coupon | null> {
  const db = await getDatabase();
  const row = await db.getFirstAsync(`SELECT * FROM coupons WHERE id = ?`, [id]);
  return row ? rowToCoupon(row) : null;
}

export async function insertCoupon(coupon: Omit<Coupon, 'id' | 'createdAt' | 'updatedAt'>): Promise<Coupon> {
  const db = await getDatabase();
  const id = generateId();
  const now = new Date().toISOString();

  await db.runAsync(
    `INSERT INTO coupons (id, source_type, raw_source_uri, raw_source_text, store_name, store_id,
      discount_description, discount_type, discount_value, minimum_purchase,
      expiration_date, expiration_display_text, date_confidence, product_categories,
      coupon_code, status, extraction_confidence, notes, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      id, coupon.sourceType, coupon.rawSourceUri, coupon.rawSourceText,
      coupon.storeName, coupon.storeId, coupon.discountDescription, coupon.discountType,
      coupon.discountValue, coupon.minimumPurchase, coupon.expirationDate,
      coupon.expirationDisplayText, coupon.dateConfidence,
      JSON.stringify(coupon.productCategories), coupon.couponCode, coupon.status,
      coupon.extractionConfidence, coupon.notes, now, now,
    ]
  );

  return { ...coupon, id, createdAt: now, updatedAt: now };
}

export async function updateCouponStatus(id: string, status: CouponStatus): Promise<void> {
  const db = await getDatabase();
  const now = new Date().toISOString();
  await db.runAsync(
    `UPDATE coupons SET status = ?, updated_at = ? WHERE id = ?`,
    [status, now, id]
  );
}

export async function updateCoupon(id: string, fields: Partial<Coupon>): Promise<void> {
  const db = await getDatabase();
  const now = new Date().toISOString();
  const setClauses: string[] = ['updated_at = ?'];
  const values: (string | number | null)[] = [now];

  const fieldMap: Record<string, string> = {
    storeName: 'store_name',
    discountDescription: 'discount_description',
    discountType: 'discount_type',
    discountValue: 'discount_value',
    minimumPurchase: 'minimum_purchase',
    expirationDate: 'expiration_date',
    expirationDisplayText: 'expiration_display_text',
    dateConfidence: 'date_confidence',
    couponCode: 'coupon_code',
    status: 'status',
    notes: 'notes',
  };

  for (const [key, column] of Object.entries(fieldMap)) {
    if (key in fields) {
      setClauses.push(`${column} = ?`);
      values.push((fields as Record<string, string | number | null>)[key]);
    }
  }

  if ('productCategories' in fields) {
    setClauses.push('product_categories = ?');
    values.push(JSON.stringify(fields.productCategories));
  }

  values.push(id);
  await db.runAsync(
    `UPDATE coupons SET ${setClauses.join(', ')} WHERE id = ?`,
    values
  );
}

export async function deleteCoupon(id: string): Promise<void> {
  const db = await getDatabase();
  await db.runAsync(`DELETE FROM coupons WHERE id = ?`, [id]);
}

export async function getExpiringCoupons(withinDays: number): Promise<Coupon[]> {
  const db = await getDatabase();
  const now = new Date();
  const future = new Date(now.getTime() + withinDays * 24 * 60 * 60 * 1000);
  const rows = await db.getAllAsync(
    `SELECT * FROM coupons WHERE status = 'active' AND expiration_date IS NOT NULL
     AND expiration_date BETWEEN ? AND ? ORDER BY expiration_date ASC`,
    [now.toISOString(), future.toISOString()]
  );
  return rows.map(rowToCoupon);
}

export async function findMatchingCoupons(itemDescription: string): Promise<Coupon[]> {
  const db = await getDatabase();
  const term = `%${itemDescription.toLowerCase()}%`;
  const rows = await db.getAllAsync(
    `SELECT * FROM coupons WHERE status = 'active' AND LOWER(product_categories) LIKE ?`,
    [term]
  );
  return rows.map(rowToCoupon);
}
