import { getDatabase } from './database';
import { ShoppingListItem } from '../types/coupon';
import { generateId } from '../utils/id';
import { findMatchingCoupons } from './couponRepository';

function rowToItem(row: unknown): ShoppingListItem {
  const r = row as Record<string, unknown>;
  return {
    id: r.id as string,
    description: r.description as string,
    isChecked: (r.is_checked as number) === 1,
    matchedCouponIds: [],
    createdAt: r.created_at as string,
  };
}

export async function getAllShoppingListItems(): Promise<ShoppingListItem[]> {
  const db = await getDatabase();
  const rows = await db.getAllAsync(
    `SELECT * FROM shopping_list_items ORDER BY is_checked ASC, created_at DESC`
  );
  const items = rows.map(rowToItem);

  // Enrich with coupon matches
  for (const item of items) {
    const matches = await findMatchingCoupons(item.description);
    item.matchedCouponIds = matches.map((c) => c.id);
  }

  return items;
}

export async function addShoppingListItem(description: string): Promise<ShoppingListItem> {
  const db = await getDatabase();
  const id = generateId();
  const now = new Date().toISOString();

  await db.runAsync(
    `INSERT INTO shopping_list_items (id, description, is_checked, created_at) VALUES (?, ?, 0, ?)`,
    [id, description, now]
  );

  const matches = await findMatchingCoupons(description);
  return {
    id,
    description,
    isChecked: false,
    matchedCouponIds: matches.map((c) => c.id),
    createdAt: now,
  };
}

export async function toggleShoppingListItem(id: string): Promise<void> {
  const db = await getDatabase();
  await db.runAsync(
    `UPDATE shopping_list_items SET is_checked = CASE WHEN is_checked = 0 THEN 1 ELSE 0 END WHERE id = ?`,
    [id]
  );
}

export async function removeShoppingListItem(id: string): Promise<void> {
  const db = await getDatabase();
  await db.runAsync(`DELETE FROM shopping_list_items WHERE id = ?`, [id]);
}

export async function clearCheckedItems(): Promise<void> {
  const db = await getDatabase();
  await db.runAsync(`DELETE FROM shopping_list_items WHERE is_checked = 1`);
}
