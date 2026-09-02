import os
import psycopg2

# Railway da DATABASE_URL dan ulanish
database_url = os.environ.get("DATABASE_URL")

if not database_url:
    # Agar DATABASE_URL bo'lmasa, localhost ga ulanish
    database_url = f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres123')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'pos_db')}"

print(f"🔍 Ulanish: {database_url[:30]}...")

pg_conn = psycopg2.connect(dsn=database_url)
pg_cursor = pg_conn.cursor()

print("🚀 JADVALLAR YARATILMOQDA...")

pg_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'cashier',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    cost_price NUMERIC(12,2) DEFAULT 0,
    sell_price NUMERIC(12,2) DEFAULT 0,
    quantity NUMERIC(12,3) DEFAULT 0,
    unit VARCHAR(20),
    min_quantity NUMERIC(12,3) DEFAULT 0,
    note TEXT,
    image_path VARCHAR(255),
    barcode VARCHAR(50),
    supplier VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    dollar_cost NUMERIC(12,2),
    dollar_price NUMERIC(12,2),
    exchange_rate NUMERIC(12,4),
    category_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    total_amount NUMERIC(12,2) DEFAULT 0,
    total_profit NUMERIC(12,2) DEFAULT 0,
    discount NUMERIC(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    car_number VARCHAR(50),
    car_model VARCHAR(100),
    phone_number VARCHAR(20),
    current_km INTEGER,
    next_km INTEGER,
    oil_change_date DATE,
    next_oil_change_date DATE,
    notification_date DATE,
    is_notified BOOLEAN DEFAULT FALSE,
    payment_type VARCHAR(20),
    bonus_amount NUMERIC(12,2) DEFAULT 0,
    discount_amount NUMERIC(12,2) DEFAULT 0,
    cash_amount NUMERIC(12,2) DEFAULT 0,
    card_amount NUMERIC(12,2) DEFAULT 0,
    extra_charge NUMERIC(12,2) DEFAULT 0,
    is_debt BOOLEAN DEFAULT FALSE,
    debt_paid BOOLEAN DEFAULT FALSE,
    customer_name VARCHAR(255),
    customer_phone VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS sale_items (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER,
    product_id INTEGER,
    quantity NUMERIC(12,3) NOT NULL,
    sell_price NUMERIC(12,2) NOT NULL,
    cost_price NUMERIC(12,2) NOT NULL,
    subtotal NUMERIC(12,2) NOT NULL
);
""")

pg_conn.commit()
pg_conn.close()

print("✅ BARCHA JADVALLAR YARATILDI!")
