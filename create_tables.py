import psycopg2

pg_conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="pos_db",
    user="postgres",
    password="postgres123"
)
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

CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    payment_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER
);

CREATE TABLE IF NOT EXISTS inventory_logs (
    id SERIAL PRIMARY KEY,
    product_id INTEGER,
    action VARCHAR(50),
    quantity NUMERIC(12,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER
);

CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    position VARCHAR(100),
    salary NUMERIC(12,2),
    hire_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER,
    check_in TIMESTAMP,
    check_out TIMESTAMP,
    date DATE
);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    message TEXT,
    type VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS shop_settings (
    id SERIAL PRIMARY KEY,
    shop_name VARCHAR(255),
    address TEXT,
    phone VARCHAR(20),
    logo_path VARCHAR(255),
    receipt_footer TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS firms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    total_debt NUMERIC(12,2) DEFAULT 0,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS firm_debts (
    id SERIAL PRIMARY KEY,
    firm_id INTEGER,
    firm_name VARCHAR(255),
    amount NUMERIC(12,2),
    description TEXT,
    debt_type VARCHAR(50),
    is_paid BOOLEAN DEFAULT FALSE,
    paid_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stock_purchases (
    id SERIAL PRIMARY KEY,
    product_id INTEGER,
    product_name VARCHAR(255),
    quantity NUMERIC(12,3),
    unit_cost NUMERIC(12,2),
    total_cost NUMERIC(12,2),
    dollar_cost NUMERIC(12,2),
    dollar_price NUMERIC(12,2),
    exchange_rate NUMERIC(12,4),
    payment_type VARCHAR(20),
    purchase_date DATE,
    due_date DATE,
    is_paid BOOLEAN DEFAULT FALSE,
    paid_date DATE,
    remaining_debt NUMERIC(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    firm_id INTEGER
);

CREATE TABLE IF NOT EXISTS cash_incomes (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(12,2),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER
);
""")

pg_conn.commit()
pg_conn.close()

print("✅ BARCHA JADVALLAR YARATILDI!")