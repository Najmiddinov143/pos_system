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
sqlite_cursor.execute("""
    SELECT * FROM products
""")
products = sqlite_cursor.fetchall()
print(f"📦 {len(products)} ta mahsulot topildi!")

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
            ON CONFLICT (id) DO NOTHING
        """, (
            p['id'], p['name'], p['category'], p['cost_price'], p['sell_price'],
            p['quantity'], p['unit'], p['min_quantity'], p['note'], p['image_path'],
            p['barcode'], p['supplier'], p['is_active'], p['dollar_cost'],
            p['dollar_price'], p['exchange_rate'], p['category_id'], p['created_at']
        ))
        count += 1
    except Exception as e:
        print(f"⚠️ Mahsulot {p['name']} o'tkazib yuborildi: {e}")

pg_conn.commit()
sqlite_conn.close()
pg_conn.close()

print(f"✅ {count} ta mahsulot PostgreSQL ga ko'chirildi!")
