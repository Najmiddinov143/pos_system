import sys
import os
import sqlite3
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from views.login_window import LoginWindow

# ===== YO'LNI ANIQLASH =====
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_db_path():
    base_path = get_base_path()
    db_path = os.path.join(base_path, "database", "pos.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_path


# ===== MA'LUMOTLAR BAZASINI TEKSHIRISH =====
def check_and_fix_database():
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print("⚠️ Ma'lumotlar bazasi topilmadi! Yangi yaratilmoqda...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'cashier')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                cost_price REAL NOT NULL,
                sell_price REAL NOT NULL,
                quantity REAL NOT NULL DEFAULT 0,
                unit TEXT DEFAULT 'dona',
                min_quantity REAL DEFAULT 5,
                note TEXT,
                image_path TEXT,
                barcode TEXT,
                supplier TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Boshqa jadvallar...
        # (qolgan jadvallarni bu yerga qo'shing)
        
        import bcrypt
        admin_pwd = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                       ('admin', admin_pwd, 'admin'))
        
        conn.commit()
        conn.close()
        print("✅ Ma'lumotlar bazasi yaratildi!")
        return
    
    print("✅ Ma'lumotlar bazasi mavjud!")


def main():
    os.makedirs("database", exist_ok=True)
    os.makedirs("assets/icons", exist_ok=True)
    os.makedirs("assets/product_images", exist_ok=True)
    os.makedirs("assets/sound", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    
    check_and_fix_database()
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName("POS Tizimi")
    app.setOrganizationName("POS System")
    
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()