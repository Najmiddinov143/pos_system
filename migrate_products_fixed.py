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

print("🚀 MAHSULOTLAR KO'CHIRILMOQDA...")

# Mahsulotlarni o'qish
sqlite_cursor.execute("SELECT * FROM products")
products = sqlite_cursor.fetchall()
print(f"📦 {len(products)} ta mahsulot topildi!")

count = 0
for p in products:
    try:
        # SQLite dagi ustunlar ro'yxati
        columns = [desc[0] for desc in sqlite_cursor.description]
        
        # PostgreSQL ga INSERT
        pg_cursor.execute("""
            INSERT INTO products (
                id, name, category, cost_price, sell_price, quantity,
                unit, min_quantity, note, image_path, barcode, supplier,
                is_active, dollar_cost, dollar_price, exchange_rate,
                category_id, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            p['id'], p['name'], p.get('category'), p.get('cost_price', 0), p.get('sell_price', 0),
            p.get('quantity', 0), p.get('unit'), p.get('min_quantity', 0), p.get('note'),
            p.get('image_path'), p.get('barcode'), p.get('supplier'), p.get('is_active', 1),
            p.get('dollar_cost'), p.get('dollar_price'), p.get('exchange_rate'),
            p.get('category_id'), p.get('created_at')
        ))
        count += 1
    except Exception as e:
        print(f"⚠️ Mahsulot {p.get('name', 'N/A')} o'tkazib yuborildi: {e}")

pg_conn.commit()
sqlite_conn.close()
pg_conn.close()

print(f"✅ {count} ta mahsulot PostgreSQL ga ko'chirildi!")
