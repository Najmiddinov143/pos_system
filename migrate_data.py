import sqlite3
import psycopg2

# SQLite ulanish
sqlite_conn = sqlite3.connect('database/pos.db')
sqlite_conn.row_factory = sqlite3.Row
sqlite_cursor = sqlite_conn.cursor()

# PostgreSQL ulanish
pg_conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="pos_db",
    user="postgres",
    password="postgres123"
)
pg_cursor = pg_conn.cursor()

print("🚀 MA'LUMOTLAR KO'CHIRILMOQDA...")

# 1. Jadvallar ro'yxatini olish
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row['name'] for row in sqlite_cursor.fetchall()]
print(f"📋 SQLite da jadvallar: {tables}")

# 2. USERS (username conflict ni oldini olish)
print("👤 Users...")
try:
    sqlite_cursor.execute("SELECT id, username, password_hash, role, created_at FROM users")
    users = sqlite_cursor.fetchall()
    count = 0
    for u in users:
        try:
            pg_cursor.execute("""
                INSERT INTO users (id, username, password_hash, role, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (username) DO UPDATE SET 
                    password_hash = EXCLUDED.password_hash,
                    role = EXCLUDED.role
            """, (u['id'], u['username'], u['password_hash'], u['role'], u['created_at']))
            count += 1
        except Exception as e:
            print(f"⚠️ User {u['username']} o'tkazib yuborildi: {e}")
    print(f"✅ {count} ta user ko'chirildi")
except Exception as e:
    print(f"⚠️ Users: {e}")

# 3. CATEGORIES (agar mavjud bo'lsa)
print("📂 Categories...")
try:
    sqlite_cursor.execute("SELECT id, name, parent_id, icon, color, created_at FROM categories")
    categories = sqlite_cursor.fetchall()
    for c in categories:
        pg_cursor.execute("""
            INSERT INTO categories (id, name, parent_id, icon, color, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (c['id'], c['name'], c['parent_id'], c['icon'], c['color'], c['created_at']))
    print(f"✅ {len(categories)} ta kategoriya ko'chirildi")
except Exception as e:
    print(f"⚠️ Categories jadvali mavjud emas: {e}")

# 4. PRODUCTS (ENG MUHIM!)
print("📦 Mahsulotlar...")
try:
    sqlite_cursor.execute("""
        SELECT id, name, category, cost_price, sell_price, quantity, unit, 
               min_quantity, note, image_path, barcode, supplier, is_active,
               dollar_cost, dollar_price, exchange_rate, category_id, created_at
        FROM products
    """)
    products = sqlite_cursor.fetchall()
    count = 0
    for p in products:
        try:
            pg_cursor.execute("""
                INSERT INTO products (
                    id, name, category, cost_price, sell_price, quantity, unit,
                    min_quantity, note, image_path, barcode, supplier, is_active,
                    dollar_cost, dollar_price, exchange_rate, category_id, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    cost_price = EXCLUDED.cost_price,
                    sell_price = EXCLUDED.sell_price,
                    quantity = EXCLUDED.quantity,
                    category = EXCLUDED.category
            """, (
                p['id'], p['name'], p['category'], p['cost_price'], p['sell_price'],
                p['quantity'], p['unit'], p['min_quantity'], p['note'], p['image_path'],
                p['barcode'], p['supplier'], p['is_active'], p['dollar_cost'],
                p['dollar_price'], p['exchange_rate'], p['category_id'], p['created_at']
            ))
            count += 1
        except Exception as e:
            print(f"⚠️ Mahsulot {p['name']} o'tkazib yuborildi: {e}")
    print(f"✅ {count} ta mahsulot ko'chirildi!")
except Exception as e:
    print(f"⚠️ Products: {e}")

# 5. SALES
print("📋 Savdolar...")
try:
    sqlite_cursor.execute("SELECT * FROM sales")
    sales = sqlite_cursor.fetchall()
    for s in sales:
        pg_cursor.execute("""
            INSERT INTO sales (id, total_amount, total_profit, discount, created_at, user_id,
                               car_number, car_model, phone_number, current_km, next_km,
                               oil_change_date, next_oil_change_date, notification_date,
                               is_notified, payment_type, bonus_amount, discount_amount,
                               cash_amount, card_amount, extra_charge, is_debt, debt_paid,
                               customer_name, customer_phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, tuple(s))
    print(f"✅ {len(sales)} ta savdo ko'chirildi")
except Exception as e:
    print(f"⚠️ Sales: {e}")

# 6. SALE ITEMS
print("📋 Savdo itemlar...")
try:
    sqlite_cursor.execute("SELECT * FROM sale_items")
    items = sqlite_cursor.fetchall()
    for item in items:
        pg_cursor.execute("""
            INSERT INTO sale_items (id, sale_id, product_id, quantity, sell_price, cost_price, subtotal)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, tuple(item))
    print(f"✅ {len(items)} ta savdo item ko'chirildi")
except Exception as e:
    print(f"⚠️ Sale items: {e}")

# 7. EXPENSES
print("💰 Xarajatlar...")
try:
    sqlite_cursor.execute("SELECT * FROM expenses")
    expenses = sqlite_cursor.fetchall()
    for e in expenses:
        pg_cursor.execute("""
            INSERT INTO expenses (id, name, amount, category, description, payment_type, created_at, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, tuple(e))
    print(f"✅ {len(expenses)} ta xarajat ko'chirildi")
except Exception as e:
    print(f"⚠️ Expenses: {e}")

# 8. FIRMS
print("🏢 Firmalar...")
try:
    sqlite_cursor.execute("SELECT * FROM firms")
    firms = sqlite_cursor.fetchall()
    for f in firms:
        pg_cursor.execute("""
            INSERT INTO firms (id, name, phone, address, total_debt, note, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, tuple(f))
    print(f"✅ {len(firms)} ta firma ko'chirildi")
except Exception as e:
    print(f"⚠️ Firms: {e}")

# 9. FIRM_DEBTS
print("🏢 Firma qarzlari...")
try:
    sqlite_cursor.execute("SELECT * FROM firm_debts")
    debts = sqlite_cursor.fetchall()
    for d in debts:
        pg_cursor.execute("""
            INSERT INTO firm_debts (id, firm_id, firm_name, amount, description, debt_type, is_paid, paid_date, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, tuple(d))
    print(f"✅ {len(debts)} ta firma qarzi ko'chirildi")
except Exception as e:
    print(f"⚠️ Firm debts: {e}")

# 10. EMPLOYEES
print("👥 Xodimlar...")
try:
    sqlite_cursor.execute("SELECT * FROM employees")
    employees = sqlite_cursor.fetchall()
    for emp in employees:
        pg_cursor.execute("""
            INSERT INTO employees (id, full_name, phone, position, salary, hire_date, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, tuple(emp))
    print(f"✅ {len(employees)} ta xodim ko'chirildi")
except Exception as e:
    print(f"⚠️ Employees: {e}")

# 11. INVENTORY_LOGS
print("📦 Ombor loglari...")
try:
    sqlite_cursor.execute("SELECT * FROM inventory_logs")
    logs = sqlite_cursor.fetchall()
    for log in logs:
        pg_cursor.execute("""
            INSERT INTO inventory_logs (id, product_id, action, quantity, created_at, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, tuple(log))
    print(f"✅ {len(logs)} ta ombor log ko'chirildi")
except Exception as e:
    print(f"⚠️ Inventory logs: {e}")

# 12. NOTIFICATIONS
print("🔔 Bildirishnomalar...")
try:
    sqlite_cursor.execute("SELECT * FROM notifications")
    notifications = sqlite_cursor.fetchall()
    for n in notifications:
        pg_cursor.execute("""
            INSERT INTO notifications (id, title, message, type, is_read, user_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, tuple(n))
    print(f"✅ {len(notifications)} ta bildirishnoma ko'chirildi")
except Exception as e:
    print(f"⚠️ Notifications: {e}")

# 13. SHOP_SETTINGS
print("⚙️ Sozlamalar...")
try:
    sqlite_cursor.execute("SELECT * FROM shop_settings")
    settings = sqlite_cursor.fetchall()
    for s in settings:
        pg_cursor.execute("""
            INSERT INTO shop_settings (id, shop_name, address, phone, logo_path, receipt_footer, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, tuple(s))
    print(f"✅ {len(settings)} ta sozlama ko'chirildi")
except Exception as e:
    print(f"⚠️ Shop settings: {e}")

# 14. STOCK_PURCHASES
print("📦 Xaridlar...")
try:
    sqlite_cursor.execute("SELECT * FROM stock_purchases")
    purchases = sqlite_cursor.fetchall()
    for p in purchases:
        pg_cursor.execute("""
            INSERT INTO stock_purchases (id, product_id, product_name, quantity, unit_cost, total_cost,
                                         dollar_cost, dollar_price, exchange_rate, payment_type,
                                         purchase_date, due_date, is_paid, paid_date, remaining_debt,
                                         created_at, firm_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, tuple(p))
    print(f"✅ {len(purchases)} ta xarid ko'chirildi")
except Exception as e:
    print(f"⚠️ Stock purchases: {e}")

# 15. CASH_INCOMES
print("💰 Kirimlar...")
try:
    sqlite_cursor.execute("SELECT * FROM cash_incomes")
    incomes = sqlite_cursor.fetchall()
    for inc in incomes:
        pg_cursor.execute("""
            INSERT INTO cash_incomes (id, amount, note, created_at, user_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, tuple(inc))
    print(f"✅ {len(incomes)} ta kirim ko'chirildi")
except Exception as e:
    print(f"⚠️ Cash incomes: {e}")

# 16. ATTENDANCE
print("📅 Davomat...")
try:
    sqlite_cursor.execute("SELECT * FROM attendance")
    attendance = sqlite_cursor.fetchall()
    for a in attendance:
        pg_cursor.execute("""
            INSERT INTO attendance (id, employee_id, check_in, check_out, date)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, tuple(a))
    print(f"✅ {len(attendance)} ta davomat ko'chirildi")
except Exception as e:
    print(f"⚠️ Attendance: {e}")

pg_conn.commit()
sqlite_conn.close()
pg_conn.close()

print("\n🎉 BARCHA MA'LUMOTLAR KO'CHIRILDI!")