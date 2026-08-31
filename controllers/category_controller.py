# controllers/category_controller.py

import sqlite3
    

class CategoryController:
    def __init__(self, db_path="database/pos.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._ensure_schema()

    def _ensure_schema(self):
        """Jadval/ustun mavjudligini tekshiradi, bo'lmasa yaratadi (xavfsiz, IF NOT EXISTS)."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                icon TEXT DEFAULT '📁',
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in self.cursor.fetchall()]
        if "category_id" not in columns:
            self.cursor.execute(
                "ALTER TABLE products ADD COLUMN category_id INTEGER REFERENCES categories(id)"
            )
        self.conn.commit()

    # ---------- CRUD ----------

    def get_all(self):
        """Barcha kategoriyalarni qaytaradi (dict ro'yxati)."""
        self.cursor.execute("SELECT * FROM categories ORDER BY name")
        return [dict(row) for row in self.cursor.fetchall()]

    def create(self, name, icon="📁", color=None):
        """Yangi kategoriya (papka) yaratadi. Muvaffaqiyatli bo'lsa yangi ID qaytaradi."""
        name = (name or "").strip()
        if not name:
            return None
        try:
            self.cursor.execute(
                "INSERT INTO categories (name, icon, color) VALUES (?, ?, ?)",
                (name, icon, color),
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Bunday nomli kategoriya allaqachon mavjud
            return None

    def rename(self, category_id, new_name):
        try:
            self.cursor.execute(
                "UPDATE categories SET name = ? WHERE id = ?", (new_name.strip(), category_id)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete(self, category_id):
        """Kategoriyani o'chiradi. Ichidagi mahsulotlar 'kategoriyasiz' bo'lib qoladi (o'chmaydi)."""
        self.cursor.execute(
            "UPDATE products SET category_id = NULL WHERE category_id = ?", (category_id,)
        )
        self.cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        self.conn.commit()
        return True

    # ---------- Mahsulot <-> Kategoriya bog'lash ----------

    def assign_products(self, product_ids, category_id):
        """Bir yoki bir nechta mahsulotni berilgan kategoriyaga biriktiradi."""
        if not product_ids:
            return False
        placeholders = ",".join("?" * len(product_ids))
        self.cursor.execute(
            f"UPDATE products SET category_id = ? WHERE id IN ({placeholders})",
            (category_id, *product_ids),
        )
        self.conn.commit()
        return True

    def get_products_by_category(self, category_id):
        """category_id=None bo'lsa — hali papkaga tushmagan mahsulotlarni qaytaradi.
        MUHIM: faqat is_active = 1 (ya'ni o'chirilmagan) mahsulotlar qaytariladi.
        Aks holda o'chirilgan (soft-delete qilingan) mahsulotlar kategoriya
        ro'yxatida abadiy ko'rinib qolib ketaveradi."""
        if category_id is None:
            self.cursor.execute(
                "SELECT * FROM products WHERE category_id IS NULL AND is_active = 1"
            )
        else:
            self.cursor.execute(
                "SELECT * FROM products WHERE category_id = ? AND is_active = 1",
                (category_id,),
            )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_category_product_count(self, category_id):
        self.cursor.execute(
            "SELECT COUNT(*) as cnt FROM products WHERE category_id = ? AND is_active = 1",
            (category_id,),
        )
        row = self.cursor.fetchone()
        return row["cnt"] if row else 0

    def close(self):
        self.conn.close()