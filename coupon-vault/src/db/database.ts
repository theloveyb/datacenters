import * as SQLite from 'expo-sqlite';

let db: SQLite.SQLiteDatabase | null = null;

export async function getDatabase(): Promise<SQLite.SQLiteDatabase> {
  if (db) return db;
  db = await SQLite.openDatabaseAsync('couponvault.db');
  await initializeDatabase(db);
  return db;
}

async function initializeDatabase(database: SQLite.SQLiteDatabase): Promise<void> {
  await database.execAsync(`
    PRAGMA journal_mode = WAL;
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS stores (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      normalized_name TEXT NOT NULL,
      category TEXT,
      latitude REAL,
      longitude REAL,
      address TEXT
    );

    CREATE TABLE IF NOT EXISTS coupons (
      id TEXT PRIMARY KEY,
      source_type TEXT NOT NULL CHECK(source_type IN ('image', 'email', 'manual')),
      raw_source_uri TEXT,
      raw_source_text TEXT,
      store_name TEXT NOT NULL,
      store_id TEXT REFERENCES stores(id),
      discount_description TEXT NOT NULL,
      discount_type TEXT NOT NULL CHECK(discount_type IN ('fixed_amount', 'percentage', 'bogo', 'free_item', 'other')),
      discount_value REAL,
      minimum_purchase REAL,
      expiration_date TEXT,
      expiration_display_text TEXT,
      date_confidence TEXT NOT NULL DEFAULT 'high' CHECK(date_confidence IN ('high', 'medium', 'low')),
      product_categories TEXT NOT NULL DEFAULT '[]',
      coupon_code TEXT,
      status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'used', 'expired', 'archived')),
      extraction_confidence REAL NOT NULL DEFAULT 1.0,
      notes TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS shopping_list_items (
      id TEXT PRIMARY KEY,
      description TEXT NOT NULL,
      is_checked INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_coupons_status ON coupons(status);
    CREATE INDEX IF NOT EXISTS idx_coupons_expiration ON coupons(expiration_date);
    CREATE INDEX IF NOT EXISTS idx_coupons_store ON coupons(store_name);
    CREATE INDEX IF NOT EXISTS idx_stores_normalized ON stores(normalized_name);
  `);
}
