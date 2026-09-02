-- Jadvallarni o'chirib qayta yaratish (agar mavjud bo'lsa)
DROP TABLE IF EXISTS sale_items CASCADE;
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS expenses CASCADE;
DROP TABLE IF EXISTS inventory_logs CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS shop_settings CASCADE;
DROP TABLE IF EXISTS firms CASCADE;
DROP TABLE IF EXISTS firm_debts CASCADE;
DROP TABLE IF EXISTS stock_purchases CASCADE;
DROP TABLE IF EXISTS cash_incomes CASCADE;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'cashier',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    parent_id INTEGER,
    icon VARCHAR(50),
    color VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
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

CREATE TABLE sales (
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

CREATE TABLE sale_items (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER,
    product_id INTEGER,
    quantity NUMERIC(12,3) NOT NULL,
    sell_price NUMERIC(12,2) NOT NULL,
    cost_price NUMERIC(12,2) NOT NULL,
    subtotal NUMERIC(12,2) NOT NULL
);

CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    payment_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER
);

CREATE TABLE inventory_logs (
    id SERIAL PRIMARY KEY,
    product_id INTEGER,
    action VARCHAR(50),
    quantity NUMERIC(12,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    position VARCHAR(100),
    salary NUMERIC(12,2),
    hire_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER,
    check_in TIMESTAMP,
    check_out TIMESTAMP,
    date DATE
);

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    message TEXT,
    type VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE shop_settings (
    id SERIAL PRIMARY KEY,
    shop_name VARCHAR(255),
    address TEXT,
    phone VARCHAR(20),
    logo_path VARCHAR(255),
    receipt_footer TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE firms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    total_debt NUMERIC(12,2) DEFAULT 0,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE firm_debts (
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

CREATE TABLE stock_purchases (
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

CREATE TABLE cash_incomes (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(12,2),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER
);
