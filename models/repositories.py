# models/repositories.py - TO'LIQ TUZATILGAN

import sqlite3 
import bcrypt
from database.database import Database
from models.models import User, Product, Sale, SaleItem, Expense
from datetime import datetime, timedelta


class UserRepository:
    def __init__(self):
        self.db = Database()
    
    def authenticate(self, username, password):
        query = "SELECT * FROM users WHERE username = ?"
        user_data = self.db.execute_query_one(query, (username,))
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash'].encode('utf-8')):
            return User(
                id=user_data['id'],
                username=user_data['username'],
                role=user_data['role'],
                created_at=user_data['created_at']
            )
        return None
    
    def get_all_users(self):
        query = "SELECT * FROM users ORDER BY id"
        return self.db.execute_query(query)
    
    def create_user(self, username, password, role):
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        query = "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)"
        return self.db.execute_query(query, (username, password_hash, role))


class ProductRepository:
    def __init__(self):
        self.db = Database()
    
    def get_all(self):
        return self.db.execute_query("SELECT * FROM products WHERE is_active = 1 ORDER BY name")
    
    def get_all_products(self):
        return self.get_all()
    
    def get_by_id(self, product_id):
        return self.db.execute_query_one("SELECT * FROM products WHERE id = ?", (product_id,))
    
    def get_product_by_id(self, product_id):
        return self.get_by_id(product_id)
    
    def get_product_by_name(self, name):
        return self.db.execute_query("SELECT * FROM products WHERE name LIKE ? AND is_active = 1", (f'%{name}%',))
    
    def create(self, product):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO products (
                    name, category, cost_price, sell_price, 
                    quantity, unit, min_quantity, note,
                    supplier, barcode, image_path,
                    dollar_cost, dollar_price, exchange_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            if hasattr(product, '__dict__'):
                cursor.execute(query, (
                    product.name if hasattr(product, 'name') else '',
                    product.category if hasattr(product, 'category') else '',
                    product.cost_price if hasattr(product, 'cost_price') else 0,
                    product.sell_price if hasattr(product, 'sell_price') else 0,
                    product.quantity if hasattr(product, 'quantity') else 0,
                    product.unit if hasattr(product, 'unit') else 'dona',
                    product.min_quantity if hasattr(product, 'min_quantity') else 5,
                    product.note if hasattr(product, 'note') else '',
                    product.supplier if hasattr(product, 'supplier') else '',
                    product.barcode if hasattr(product, 'barcode') else '',
                    product.image_path if hasattr(product, 'image_path') else '',
                    product.dollar_cost if hasattr(product, 'dollar_cost') else 0,
                    product.dollar_price if hasattr(product, 'dollar_price') else 0,
                    product.exchange_rate if hasattr(product, 'exchange_rate') else 0
                ))
            else:
                cursor.execute(query, (
                    product.get('name', ''),
                    product.get('category', ''),
                    product.get('cost_price', 0),
                    product.get('sell_price', 0),
                    product.get('quantity', 0),
                    product.get('unit', 'dona'),
                    product.get('min_quantity', 5),
                    product.get('note', ''),
                    product.get('supplier', ''),
                    product.get('barcode', ''),
                    product.get('image_path', ''),
                    product.get('dollar_cost', 0),
                    product.get('dollar_price', 0),
                    product.get('exchange_rate', 0)
                ))
            
            conn.commit()
            product_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            new_product = cursor.fetchone()
            conn.close()
            
            if new_product:
                return dict(new_product)
            return None
            
        except Exception as e:
            print(f"❌ Error creating product: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return None
    
    def update(self, product):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                UPDATE products 
                SET name=?, category=?, cost_price=?, sell_price=?, 
                    quantity=?, unit=?, min_quantity=?, note=?,
                    supplier=?, barcode=?, image_path=?,
                    dollar_cost=?, dollar_price=?, exchange_rate=?
                WHERE id=?
            """
            
            if hasattr(product, '__dict__'):
                cursor.execute(query, (
                    product.name if hasattr(product, 'name') else '',
                    product.category if hasattr(product, 'category') else '',
                    product.cost_price if hasattr(product, 'cost_price') else 0,
                    product.sell_price if hasattr(product, 'sell_price') else 0,
                    product.quantity if hasattr(product, 'quantity') else 0,
                    product.unit if hasattr(product, 'unit') else 'dona',
                    product.min_quantity if hasattr(product, 'min_quantity') else 5,
                    product.note if hasattr(product, 'note') else '',
                    product.supplier if hasattr(product, 'supplier') else '',
                    product.barcode if hasattr(product, 'barcode') else '',
                    product.image_path if hasattr(product, 'image_path') else '',
                    product.dollar_cost if hasattr(product, 'dollar_cost') else 0,
                    product.dollar_price if hasattr(product, 'dollar_price') else 0,
                    product.exchange_rate if hasattr(product, 'exchange_rate') else 0,
                    product.id if hasattr(product, 'id') else 0
                ))
            else:
                cursor.execute(query, (
                    product.get('name', ''),
                    product.get('category', ''),
                    product.get('cost_price', 0),
                    product.get('sell_price', 0),
                    product.get('quantity', 0),
                    product.get('unit', 'dona'),
                    product.get('min_quantity', 5),
                    product.get('note', ''),
                    product.get('supplier', ''),
                    product.get('barcode', ''),
                    product.get('image_path', ''),
                    product.get('dollar_cost', 0),
                    product.get('dollar_price', 0),
                    product.get('exchange_rate', 0),
                    product.get('id', 0)
                ))
            
            conn.commit()
            conn.close()
            
            return self.get_product_by_id(product.id if hasattr(product, 'id') else product.get('id', 0))
            
        except Exception as e:
            print(f"❌ Error updating product: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return None
    
    def delete(self, product_id):
        query = "UPDATE products SET is_active = 0 WHERE id = ?"
        return self.db.execute_query(query, (product_id,))
    
    def restore(self, product_id):
        query = "UPDATE products SET is_active = 1 WHERE id = ?"
        return self.db.execute_query(query, (product_id,))
    
    def update_stock(self, product_id, quantity_change):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
            result = cursor.fetchone()
            
            if result:
                new_quantity = result['quantity'] + quantity_change
                new_quantity = round(new_quantity, 3)
                if abs(new_quantity) < 0.001:
                    new_quantity = 0
                cursor.execute(
                    "UPDATE products SET quantity = ? WHERE id = ?",
                    (new_quantity, product_id)
                )
                conn.commit()
                conn.close()
                return True
            
            conn.close()
            return False
            
        except Exception as e:
            print(f"❌ Error updating stock: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False


class PurchaseRepository:
    def __init__(self):
        self.db = Database()
    
    def create_purchase(self, purchase_data):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            product_id = purchase_data.get('product_id')
            product_name = purchase_data.get('product_name', '')
            quantity = float(purchase_data.get('quantity', 0))
            unit_cost = float(purchase_data.get('unit_cost', 0))
            total_cost = float(purchase_data.get('total_cost', 0))
            payment_type = purchase_data.get('payment_type', 'Naxt')
            purchase_date = purchase_data.get('purchase_date')
            due_date = purchase_data.get('due_date')
            dollar_cost = purchase_data.get('dollar_cost', 0)
            dollar_price = purchase_data.get('dollar_price', 0)
            exchange_rate = purchase_data.get('exchange_rate', 0)
            firm_id = purchase_data.get('firm_id')

            query = """
                INSERT INTO stock_purchases (
                    product_id, product_name, quantity, unit_cost, total_cost,
                    payment_type, purchase_date, due_date,
                    dollar_cost, dollar_price, exchange_rate, firm_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                product_id, product_name, quantity, unit_cost, total_cost,
                payment_type, purchase_date, due_date,
                dollar_cost, dollar_price, exchange_rate, firm_id
            ))

            conn.commit()
            purchase_id = cursor.lastrowid
            conn.close()
            
            return purchase_id
            
        except Exception as e:
            print(f"❌ Error creating purchase: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return None
    
    def get_all_purchases(self, product_id=None):
        try:
            if product_id:
                query = "SELECT * FROM stock_purchases WHERE product_id = ? ORDER BY created_at DESC"
                return self.db.execute_query(query, (product_id,))
            else:
                query = "SELECT * FROM stock_purchases ORDER BY created_at DESC"
                return self.db.execute_query(query)
        except Exception as e:
            print(f"❌ Error getting purchases: {e}")
            return []
    
    def get_purchase_by_id(self, purchase_id):
        try:
            query = "SELECT * FROM stock_purchases WHERE id = ?"
            return self.db.execute_query_one(query, (purchase_id,))
        except Exception as e:
            print(f"❌ Error getting purchase: {e}")
            return None
    
    def update_payment_status(self, purchase_id, is_paid):
        try:
            query = "UPDATE stock_purchases SET is_paid = ? WHERE id = ?"
            return self.db.execute_update(query, (1 if is_paid else 0, purchase_id))
        except Exception as e:
            print(f"❌ Error updating payment status: {e}")
            return -1
    
    def update_purchase(self, purchase_id, update_data):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            allowed_fields = [
                'payment_type', 'car_number', 'car_model', 'phone_number',
                'current_km', 'next_km', 'oil_change_date', 'next_oil_change_date',
                'customer_name', 'customer_phone', 'discount', 'discount_amount', 'bonus_amount',
                'is_debt', 'debt_paid', 'extra_charge',
                'cash_amount', 'card_amount'
            ]
            
            fields = []
            values = []
            
            for key, value in update_data.items():
                if key in allowed_fields:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return False
            
            values.append(purchase_id)
            query = f"UPDATE stock_purchases SET {', '.join(fields)} WHERE id = ?"
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error updating purchase: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def delete_purchase(self, purchase_id):
        try:
            query = "DELETE FROM stock_purchases WHERE id = ?"
            return self.db.execute_query(query, (purchase_id,))
        except Exception as e:
            print(f"❌ Error deleting purchase: {e}")
            return False
    
    def get_total_debt(self):
        try:
            query = """
                SELECT COALESCE(SUM(total_cost), 0) as total 
                FROM stock_purchases 
                WHERE payment_type = 'Nasiya' AND is_paid = 0
            """
            result = self.db.execute_query_one(query)
            return result['total'] if result else 0.0
        except Exception as e:
            print(f"❌ Error getting total debt: {e}")
            return 0.0
    
    def get_total_debt_usd(self):
        try:
            query = """
                SELECT COALESCE(SUM(dollar_cost * quantity), 0) as total 
                FROM stock_purchases 
                WHERE payment_type = 'Nasiya' AND is_paid = 0
            """
            result = self.db.execute_query_one(query)
            return result['total'] if result else 0.0
        except Exception as e:
            print(f"❌ Error getting total debt usd: {e}")
            return 0.0
    
    def get_purchases_by_date(self, start_date, end_date):
        try:
            query = """
                SELECT * FROM stock_purchases 
                WHERE DATE(purchase_date) BETWEEN DATE(?) AND DATE(?)
                ORDER BY purchase_date DESC
            """
            return self.db.execute_query(query, (start_date, end_date))
        except Exception as e:
            print(f"❌ Error getting purchases by date: {e}")
            return []
    
    def get_all_purchases_with_debts(self):
        try:
            query = """
                SELECT * FROM stock_purchases 
                WHERE payment_type = 'Nasiya' AND is_paid = 0
                ORDER BY due_date ASC
            """
            return self.db.execute_query(query)
        except Exception as e:
            print(f"❌ Error getting debts: {e}")
            return []
    
    def get_debt_notifications(self, days=7):
        try:
            today = datetime.now().date()
            end_date = today + timedelta(days=days)
            
            query = """
                SELECT * FROM stock_purchases 
                WHERE payment_type = 'Nasiya' 
                AND is_paid = 0 
                AND DATE(due_date) <= DATE(?)
                AND DATE(due_date) >= DATE(?)
                ORDER BY due_date ASC
            """
            return self.db.execute_query(query, (
                end_date.strftime('%Y-%m-%d'), 
                today.strftime('%Y-%m-%d')
            ))
        except Exception as e:
            print(f"❌ Error getting debt notifications: {e}")
            return []
    
    def get_debts_by_due_date(self, due_date):
        try:
            query = """
                SELECT * FROM stock_purchases 
                WHERE payment_type = 'Nasiya' 
                AND is_paid = 0 
                AND DATE(due_date) = DATE(?)
                ORDER BY due_date ASC
            """
            return self.db.execute_query(query, (due_date,))
        except Exception as e:
            print(f"❌ Error getting debts by due date: {e}")
            return []
    
    def _ensure_debt_payments_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debt_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_id INTEGER NOT NULL,
                paid_amount REAL NOT NULL DEFAULT 0,
                cash_amount REAL NOT NULL DEFAULT 0,
                card_amount REAL NOT NULL DEFAULT 0,
                payment_type TEXT DEFAULT 'Naxt',
                paid_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (purchase_id) REFERENCES stock_purchases(id)
            )
        """)

    def mark_as_partially_paid(self, purchase_id, paid_amount, paid_date, cash_amount=0, card_amount=0):
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            self._ensure_debt_payments_table(cursor)

            purchase = self.get_purchase_by_id(purchase_id)
            if not purchase:
                conn.close()
                return {'success': False, 'message': 'Qarz topilmadi!'}
            
            if purchase.get('is_paid', 0) == 1:
                conn.close()
                return {'success': False, 'message': 'Bu qarz allaqachon to\'langan!'}
            
            current_debt = purchase.get('total_cost', 0)
            
            if paid_amount <= 0:
                conn.close()
                return {'success': False, 'message': 'To\'lov miqdori 0 dan katta bo\'lishi kerak!'}
            
            if paid_amount > current_debt:
                conn.close()
                return {'success': False, 'message': f'To\'lov miqdori qarzdan katta! Qarz: {current_debt:,.0f} so\'m'}

            cash_amount = float(cash_amount or 0)
            card_amount = float(card_amount or 0)

            if cash_amount > 0 or card_amount > 0:
                if round(cash_amount + card_amount) != round(paid_amount):
                    conn.close()
                    return {
                        'success': False,
                        'message': f'Naqd ({cash_amount:,.0f}) + Plastik ({card_amount:,.0f}) '
                                    f'to\'lov summasiga ({paid_amount:,.0f}) teng emas!'
                    }
            else:
                cash_amount = paid_amount
                card_amount = 0

            if cash_amount > 0 and card_amount > 0:
                payment_type = 'Naxt+Plastik'
            elif card_amount > 0:
                payment_type = 'Plastik'
            else:
                payment_type = 'Naxt'
            
            remaining_debt = current_debt - paid_amount
            
            if remaining_debt <= 0:
                cursor.execute(
                    """UPDATE stock_purchases 
                       SET is_paid = 1, 
                           paid_date = ?,
                           remaining_debt = 0 
                       WHERE id = ?""",
                    (paid_date, purchase_id)
                )
            else:
                cursor.execute(
                    """UPDATE stock_purchases 
                       SET total_cost = ?,
                           remaining_debt = ?,
                           paid_date = ? 
                       WHERE id = ?""",
                    (remaining_debt, remaining_debt, paid_date, purchase_id)
                )

            cursor.execute(
                """INSERT INTO debt_payments 
                   (purchase_id, paid_amount, cash_amount, card_amount, payment_type, paid_date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (purchase_id, paid_amount, cash_amount, card_amount, payment_type, paid_date)
            )
            conn.commit()
            conn.close()

            firm_id = purchase.get('firm_id')
            if firm_id:
                try:
                    from models.repositories import FirmRepository
                    firm_repo = FirmRepository()
                    firm_repo.reduce_debt(firm_id, paid_amount)
                    print(f"🏢 Firma qarzidan ayirildi: {paid_amount:,.0f} so'm (firm_id={firm_id})")
                except Exception as e:
                    print(f"❌ Firma qarzini kamaytirishda xatolik: {e}")

            status = "✅ Qarz to'liq to'landi!" if remaining_debt <= 0 else f"⚠️ Qolgan qarz: {remaining_debt:,.0f} so'm"
            
            return {
                'success': True,
                'message': f"{status}\nTo'langan: {paid_amount:,.0f} so'm\n"
                           f"Naxt: {cash_amount:,.0f} so'm | Plastik: {card_amount:,.0f} so'm\n"
                           f"Qolgan qarz: {remaining_debt:,.0f} so'm",
                'remaining_debt': remaining_debt,
                'paid_amount': paid_amount,
                'cash_amount': cash_amount,
                'card_amount': card_amount,
                'payment_type': payment_type
            }
            
        except Exception as e:
            print(f"❌ Error marking as partially paid: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return {'success': False, 'message': str(e)}

    def get_payment_history(self, purchase_id):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            self._ensure_debt_payments_table(cursor)
            conn.commit()
            conn.close()

            query = """
                SELECT * FROM debt_payments 
                WHERE purchase_id = ? 
                ORDER BY created_at DESC
            """
            return self.db.execute_query(query, (purchase_id,))
        except Exception as e:
            print(f"❌ Error getting payment history: {e}")
            return []

    def get_all_payment_history(self, start_date=None, end_date=None):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            self._ensure_debt_payments_table(cursor)
            conn.commit()
            conn.close()

            if start_date and end_date:
                query = """
                    SELECT * FROM debt_payments 
                    WHERE DATE(paid_date) BETWEEN DATE(?) AND DATE(?)
                    ORDER BY paid_date DESC
                """
                return self.db.execute_query(query, (start_date, end_date))
            else:
                query = "SELECT * FROM debt_payments ORDER BY paid_date DESC"
                return self.db.execute_query(query)
        except Exception as e:
            print(f"❌ Error getting all payment history: {e}")
            return []
    
    def mark_as_paid_with_date(self, purchase_id, paid_date):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            purchase = self.get_purchase_by_id(purchase_id)
            if not purchase:
                return {'success': False, 'message': 'Qarz topilmadi!'}
            
            if purchase.get('is_paid', 0) == 1:
                return {'success': False, 'message': 'Bu qarz allaqachon to\'langan!'}
            
            debt_amount = purchase.get('total_cost', 0)
            
            cursor.execute(
                "UPDATE stock_purchases SET is_paid = 1, paid_date = ?, remaining_debt = 0 WHERE id = ?",
                (paid_date, purchase_id)
            )
            
            conn.commit()
            conn.close()
            
            from controllers.sale_controller import SaleController
            sale_controller = SaleController()
            
            sales = sale_controller.get_sales_by_date(paid_date)
            
            if sales:
                sale_id = sales[0]['id']
                current_total = sales[0]['total_amount']
                new_total = current_total - debt_amount
                
                if new_total < 0:
                    new_total = 0
                
                sale_controller.update_sale_amount(sale_id, new_total)
                
                print(f"💰 Savdodan yechib olindi: {debt_amount:,.0f} so'm")
                print(f"📊 Eski savdo: {current_total:,.0f} so'm")
                print(f"📊 Yangi savdo: {new_total:,.0f} so'm")
            else:
                print(f"⚠️ {paid_date} kuni savdo yo'q! Faqat qarz yangilandi.")
            
            return {
                'success': True,
                'message': f"✅ Qarz to'landi! {debt_amount:,.0f} so'm yechib olindi.",
                'debt_amount': debt_amount
            }
            
        except Exception as e:
            print(f"❌ Error marking as paid: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return {'success': False, 'message': str(e)}


class SaleRepository:
    def __init__(self):
        self.db = Database()
    
    def get_all(self):
        return self.db.execute_query("SELECT * FROM sales ORDER BY created_at DESC")
    
    def get_sales_with_items(self, start_date=None, end_date=None):
        try:
            query = """
                SELECT s.*, u.username 
                FROM sales s
                LEFT JOIN users u ON s.user_id = u.id
            """
            params = []
            if start_date and end_date:
                query += " WHERE DATE(s.created_at) BETWEEN DATE(?) AND DATE(?)"
                params = [start_date, end_date]
            query += " ORDER BY s.created_at DESC"
            
            sales_data = self.db.execute_query(query, params if params else None)
            sales = []
            
            for sale_row in sales_data:
                items_query = """
                    SELECT si.*, p.name as product_name 
                    FROM sale_items si
                    JOIN products p ON si.product_id = p.id
                    WHERE si.sale_id = ?
                """
                items_data = self.db.execute_query(items_query, (sale_row['id'],))
                items = []
                for item in items_data:
                    items.append(SaleItem(
                        id=item['id'],
                        sale_id=item['sale_id'],
                        product_id=item['product_id'],
                        quantity=item['quantity'],
                        sell_price=item['sell_price'],
                        cost_price=item['cost_price'],
                        subtotal=item['subtotal'],
                        product_name=item['product_name']
                    ))
                
                created_at = sale_row['created_at']
                if created_at and isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    except:
                        created_at = datetime.now()
                
                sale = Sale(
                    id=sale_row['id'],
                    total_amount=sale_row['total_amount'],
                    total_profit=sale_row['total_profit'],
                    discount=sale_row['discount'],
                    created_at=created_at,
                    user_id=sale_row['user_id'],
                    car_number=sale_row.get('car_number', ''),
                    car_model=sale_row.get('car_model', ''),
                    phone_number=sale_row.get('phone_number', ''),
                    current_km=sale_row.get('current_km', 0),
                    next_km=sale_row.get('next_km', 0),
                    oil_change_date=sale_row.get('oil_change_date', ''),
                    next_oil_change_date=sale_row.get('next_oil_change_date', ''),
                    notification_date=sale_row.get('notification_date', ''),
                    is_notified=sale_row.get('is_notified', 0),
                    payment_type=sale_row.get('payment_type', 'Naxt'),
                    bonus_amount=sale_row.get('bonus_amount', 0),
                    discount_amount=sale_row.get('discount_amount', 0),
                    cash_amount=sale_row.get('cash_amount', 0),
                    card_amount=sale_row.get('card_amount', 0),
                    extra_charge=sale_row.get('extra_charge', 0),
                    is_debt=sale_row.get('is_debt', 0),
                    debt_paid=sale_row.get('debt_paid', 0),
                    customer_name=sale_row.get('customer_name', ''),
                    customer_phone=sale_row.get('customer_phone', ''),
                    items=items
                )
                sales.append(sale)
            
            return sales
        except Exception as e:
            print(f"Error in get_sales_with_items: {e}")
            return []
    
    def create_sale(self, sale, items):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            discount_amount = 0
            if hasattr(sale, 'discount_amount') and sale.discount_amount:
                discount_amount = sale.discount_amount
            elif hasattr(sale, 'discount') and sale.discount:
                discount_amount = sale.discount
            
            cursor.execute(
                """INSERT INTO sales 
                   (total_amount, total_profit, discount, user_id, 
                    car_number, car_model, phone_number, current_km, next_km, 
                    oil_change_date, next_oil_change_date, notification_date, is_notified,
                    payment_type, bonus_amount, discount_amount, cash_amount, card_amount,
                    extra_charge, is_debt, debt_paid, customer_name, customer_phone) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (sale.total_amount, sale.total_profit, 
                 discount_amount,
                 sale.user_id,
                 sale.car_number, sale.car_model, sale.phone_number, 
                 sale.current_km, sale.next_km,
                 sale.oil_change_date, sale.next_oil_change_date,
                 sale.notification_date if hasattr(sale, 'notification_date') else '',
                 sale.is_notified if hasattr(sale, 'is_notified') else 0,
                 sale.payment_type if hasattr(sale, 'payment_type') else 'Naxt',
                 sale.bonus_amount if hasattr(sale, 'bonus_amount') else 0,
                 discount_amount,
                 sale.cash_amount if hasattr(sale, 'cash_amount') else 0,
                 sale.card_amount if hasattr(sale, 'card_amount') else 0,
                 sale.extra_charge if hasattr(sale, 'extra_charge') else 0,
                 sale.is_debt if hasattr(sale, 'is_debt') else 0,
                 sale.debt_paid if hasattr(sale, 'debt_paid') else 0,
                 sale.customer_name if hasattr(sale, 'customer_name') else '',
                 sale.customer_phone if hasattr(sale, 'customer_phone') else ''
                )
            )
            sale_id = cursor.lastrowid
            
            for item in items:
                cursor.execute(
                    "INSERT INTO sale_items (sale_id, product_id, quantity, sell_price, cost_price, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
                    (sale_id, item.product_id, item.quantity, item.sell_price, item.cost_price, item.subtotal)
                )
                cursor.execute("SELECT quantity FROM products WHERE id = ?", (item.product_id,))
                current_qty_row = cursor.fetchone()
                current_qty = current_qty_row['quantity'] if current_qty_row else 0
                new_qty = round(current_qty - item.quantity, 3)
                if abs(new_qty) < 0.001:
                    new_qty = 0
                cursor.execute(
                    "UPDATE products SET quantity = ? WHERE id = ?",
                    (new_qty, item.product_id)
                )
                cursor.execute(
                    "INSERT INTO inventory_logs (product_id, action, quantity) VALUES (?, ?, ?)",
                    (item.product_id, 'sotildi', -item.quantity)
                )
            
            conn.commit()
            conn.close()
            return sale_id
        except Exception as e:
            print(f"❌ Error creating sale: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return None
    
    def get_total_sales(self, start_date=None, end_date=None):
        try:
            query = "SELECT COALESCE(SUM(total_amount), 0) as total FROM sales"
            params = []
            if start_date and end_date:
                query += " WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)"
                params = [start_date, end_date]
            result = self.db.execute_query_one(query, params if params else None)
            return result['total'] if result and result['total'] else 0.0
        except Exception as e:
            print(f"Error in get_total_sales: {e}")
            return 0.0
    
    def get_total_profit(self, start_date=None, end_date=None):
        try:
            query = """SELECT COALESCE(SUM(total_profit), 0) as total FROM sales
                       WHERE NOT (payment_type = 'Nasiya' AND debt_paid = 0)"""
            params = []
            if start_date and end_date:
                query += " AND DATE(created_at) BETWEEN DATE(?) AND DATE(?)"
                params = [start_date, end_date]
            result = self.db.execute_query_one(query, params if params else None)
            return result['total'] if result and result['total'] else 0.0
        except Exception as e:
            print(f"Error in get_total_profit: {e}")
            return 0.0

    def get_upcoming_notifications(self, days=3):
        try:
            today = datetime.now().date()
            start_date = today
            end_date = today + timedelta(days=days)
            
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            query = """
                SELECT s.*, u.username 
                FROM sales s
                LEFT JOIN users u ON s.user_id = u.id
                WHERE DATE(s.next_oil_change_date) BETWEEN DATE(?) AND DATE(?)
                AND s.is_notified = 0
                ORDER BY s.next_oil_change_date ASC, s.created_at ASC
            """
            
            sales_data = self.db.execute_query(query, (start_date_str, end_date_str))
            sales = []
            
            for sale_row in sales_data:
                items_query = """
                    SELECT si.*, p.name as product_name 
                    FROM sale_items si
                    JOIN products p ON si.product_id = p.id
                    WHERE si.sale_id = ?
                """
                items_data = self.db.execute_query(items_query, (sale_row['id'],))
                items = []
                for item in items_data:
                    items.append(SaleItem(
                        id=item['id'],
                        sale_id=item['sale_id'],
                        product_id=item['product_id'],
                        quantity=item['quantity'],
                        sell_price=item['sell_price'],
                        cost_price=item['cost_price'],
                        subtotal=item['subtotal'],
                        product_name=item['product_name']
                    ))
                
                created_at = sale_row['created_at']
                if created_at and isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    except:
                        created_at = datetime.now()
                
                sale = Sale(
                    id=sale_row['id'],
                    total_amount=sale_row['total_amount'],
                    total_profit=sale_row['total_profit'],
                    discount=sale_row['discount'],
                    created_at=created_at,
                    user_id=sale_row['user_id'],
                    car_number=sale_row.get('car_number', ''),
                    car_model=sale_row.get('car_model', ''),
                    phone_number=sale_row.get('phone_number', ''),
                    current_km=sale_row.get('current_km', 0),
                    next_km=sale_row.get('next_km', 0),
                    oil_change_date=sale_row.get('oil_change_date', ''),
                    next_oil_change_date=sale_row.get('next_oil_change_date', ''),
                    notification_date=sale_row.get('notification_date', ''),
                    is_notified=sale_row.get('is_notified', 0),
                    payment_type=sale_row.get('payment_type', 'Naxt'),
                    bonus_amount=sale_row.get('bonus_amount', 0),
                    discount_amount=sale_row.get('discount_amount', 0),
                    cash_amount=sale_row.get('cash_amount', 0),
                    card_amount=sale_row.get('card_amount', 0),
                    extra_charge=sale_row.get('extra_charge', 0),
                    is_debt=sale_row.get('is_debt', 0),
                    debt_paid=sale_row.get('debt_paid', 0),
                    customer_name=sale_row.get('customer_name', ''),
                    customer_phone=sale_row.get('customer_phone', ''),
                    items=items
                )
                sales.append(sale)
            
            return sales
        except Exception as e:
            print(f"Error in get_upcoming_notifications: {e}")
            return []

    def mark_as_notified(self, sale_id):
        try:
            query = "UPDATE sales SET is_notified = 1 WHERE id = ?"
            self.db.execute_query(query, (sale_id,))
            return True
        except Exception as e:
            print(f"Error in mark_as_notified: {e}")
            return False

    def update_payment_type(self, sale_id, new_payment_type, customer_name="", customer_phone=""):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            is_debt = 1 if new_payment_type == 'Nasiya' else 0
            
            query = """
                UPDATE sales 
                SET payment_type = ?, is_debt = ?,
                    customer_name = ?, customer_phone = ?
                WHERE id = ?
            """
            cursor.execute(query, (new_payment_type, is_debt, customer_name, customer_phone, sale_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error updating payment type: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False

    def update_sale(self, sale_id, update_data):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            allowed_fields = [
                'payment_type', 'car_number', 'car_model', 'phone_number',
                'current_km', 'next_km', 'oil_change_date', 'next_oil_change_date',
                'customer_name', 'customer_phone', 'discount', 'discount_amount', 'bonus_amount',
                'is_debt', 'debt_paid', 'extra_charge'
            ]
            
            fields = []
            values = []
            
            for key, value in update_data.items():
                if key in allowed_fields:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return False
            
            values.append(sale_id)
            query = f"UPDATE sales SET {', '.join(fields)} WHERE id = ?"
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error updating sale: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def get_sales_by_date(self, date_str):
        try:
            query = """
                SELECT * FROM sales 
                WHERE DATE(created_at) = DATE(?)
                ORDER BY created_at DESC
            """
            return self.db.execute_query(query, (date_str,))
        except Exception as e:
            print(f"❌ Error getting sales by date: {e}")
            return []
    
    def update_sale_amount(self, sale_id, new_amount):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE sales SET total_amount = ? WHERE id = ?",
                (new_amount, sale_id)
            )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error updating sale amount: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def get_cash_card_balance(self, date_str):
        def _safe_sum(query, params):
            try:
                row = self.db.execute_query_one(query, params)
                return (row['cash'] if row else 0.0) or 0.0, (row['card'] if row else 0.0) or 0.0
            except Exception:
                return 0.0, 0.0

        total_cash, total_card = _safe_sum(
            """SELECT COALESCE(SUM(cash_amount), 0) as cash,
                      COALESCE(SUM(card_amount), 0) as card
               FROM sales WHERE DATE(created_at) = DATE(?)""",
            (date_str,)
        )
        paid_cash, paid_card = _safe_sum(
            """SELECT COALESCE(SUM(cash_amount), 0) as cash,
                      COALESCE(SUM(card_amount), 0) as card
               FROM debt_payments WHERE DATE(paid_date) = DATE(?)""",
            (date_str,)
        )
        firm_paid_cash, firm_paid_card = _safe_sum(
            """SELECT COALESCE(SUM(cash_amount), 0) as cash,
                      COALESCE(SUM(card_amount), 0) as card
               FROM firm_debt_payments WHERE DATE(paid_date) = DATE(?)""",
            (date_str,)
        )

        available_cash = max(0.0, total_cash - paid_cash - firm_paid_cash)
        available_card = max(0.0, total_card - paid_card - firm_paid_card)

        return {
            'total_cash': total_cash,
            'total_card': total_card,
            'available_cash': available_cash,
            'available_card': available_card
        }

    def reduce_sale_by_payment(self, sale_id, total_delta, cash_delta, card_delta):
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT total_amount, cash_amount, card_amount FROM sales WHERE id = ?",
                (sale_id,)
            )
            row = cursor.fetchone()
            if not row:
                conn.close()
                return False

            new_total = max(0, (row['total_amount'] or 0) - total_delta)
            new_cash = max(0, (row['cash_amount'] or 0) - cash_delta)
            new_card = max(0, (row['card_amount'] or 0) - card_delta)

            cursor.execute(
                "UPDATE sales SET total_amount = ?, cash_amount = ?, card_amount = ? WHERE id = ?",
                (new_total, new_cash, new_card, sale_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error reducing sale by payment: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False


class ExpenseRepository:
    def __init__(self):
        self.db = Database()
    
    def get_all(self, start_date=None, end_date=None):
        query = "SELECT * FROM expenses"
        params = []
        if start_date and end_date:
            query += " WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)"
            params = [start_date, end_date]
        query += " ORDER BY created_at DESC"
        return self.db.execute_query(query, params if params else None)
    
    def get_all_expenses(self, start_date=None, end_date=None):
        return self.get_all(start_date, end_date)
    
    def get_total(self, start_date=None, end_date=None):
        query = "SELECT COALESCE(SUM(amount), 0) as total FROM expenses"
        params = []
        if start_date and end_date:
            query += " WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)"
            params = [start_date, end_date]
        result = self.db.execute_query_one(query, params if params else None)
        return result['total'] if result else 0.0
    
    def get_total_expenses(self, start_date=None, end_date=None):
        return self.get_total(start_date, end_date)
    
    def create_expense(self, expense):
        query = """
            INSERT INTO expenses (name, amount, category, description, payment_type, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            return self.db.execute_query(query, (
                expense.name, expense.amount, expense.category,
                expense.description,
                getattr(expense, 'payment_type', 'Naxt') or 'Naxt',
                expense.user_id
            ))
        except sqlite3.OperationalError as e:
            if "no column named payment_type" in str(e):
                print("⚠️ expenses jadvalida payment_type ustuni yo'q, qo'shilmoqda...")
                try:
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("ALTER TABLE expenses ADD COLUMN payment_type TEXT DEFAULT 'Naxt'")
                    conn.commit()
                    conn.close()
                    print("✅ payment_type ustuni qo'shildi!")
                    return self.create_expense(expense)
                except Exception as e2:
                    print(f"❌ payment_type qo'shishda xatolik: {e2}")
                    return None
            else:
                print(f"❌ Error creating expense: {e}")
                return None
    
    def delete_expense(self, expense_id):
        query = "DELETE FROM expenses WHERE id = ?"
        return self.db.execute_query(query, (expense_id,))
    
    def get_expenses_by_category(self, start_date=None, end_date=None):
        query = """
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM expenses
        """
        params = []
        if start_date and end_date:
            query += " WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)"
            params = [start_date, end_date]
        query += " GROUP BY category ORDER BY total DESC"
        return self.db.execute_query(query, params if params else None)


class EmployeeRepository:
    def __init__(self):
        self.db = Database()
    
    def get_all_employees(self):
        query = "SELECT * FROM employees WHERE is_active = 1 ORDER BY full_name"
        return self.db.execute_query(query)
    
    def get_employee_by_id(self, employee_id):
        query = "SELECT * FROM employees WHERE id = ?"
        return self.db.execute_query_one(query, (employee_id,))
    
    def create_employee(self, employee):
        query = """
            INSERT INTO employees (full_name, phone, position, salary, hire_date)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (
            employee.full_name, employee.phone, employee.position,
            employee.salary, employee.hire_date
        ))
    
    def update_employee(self, employee):
        query = """
            UPDATE employees 
            SET full_name=?, phone=?, position=?, salary=?, hire_date=?, is_active=?
            WHERE id=?
        """
        return self.db.execute_query(query, (
            employee.full_name, employee.phone, employee.position,
            employee.salary, employee.hire_date, employee.is_active, employee.id
        ))
    
    def delete_employee(self, employee_id):
        query = "UPDATE employees SET is_active = 0 WHERE id = ?"
        return self.db.execute_query(query, (employee_id,))
    
    def get_attendance(self, employee_id, date):
        query = "SELECT * FROM attendance WHERE employee_id = ? AND date = ?"
        return self.db.execute_query_one(query, (employee_id, date))
    
    def check_in(self, employee_id, date, time):
        query = "INSERT INTO attendance (employee_id, check_in, date) VALUES (?, ?, ?)"
        return self.db.execute_query(query, (employee_id, time, date))
    
    def check_out(self, employee_id, date, time):
        query = "UPDATE attendance SET check_out = ? WHERE employee_id = ? AND date = ?"
        return self.db.execute_query(query, (time, employee_id, date))


class BackupRepository:
    def __init__(self):
        self.db = Database()
    
    def save_backup_record(self, backup):
        query = """
            INSERT INTO backup_history (backup_date, file_name, file_size, created_by)
            VALUES (?, ?, ?, ?)
        """
        return self.db.execute_query(query, (
            backup.backup_date, backup.file_name, backup.file_size, backup.created_by
        ))
    
    def get_backup_history(self, limit=20):
        query = "SELECT * FROM backup_history ORDER BY id DESC LIMIT ?"
        return self.db.execute_query(query, (limit,))


class NotificationRepository:
    def __init__(self):
        self.db = Database()
    
    def get_all_notifications(self, user_id=None):
        try:
            query = "SELECT * FROM notifications"
            params = []
            if user_id:
                query += " WHERE user_id = ? OR user_id IS NULL"
                params = [user_id]
            query += " ORDER BY created_at DESC LIMIT 50"
            return self.db.execute_query(query, params if params else None)
        except Exception as e:
            print(f"❌ Error getting notifications: {e}")
            return []
    
    def create_notification(self, notification):
        try:
            if isinstance(notification, dict):
                title = notification.get('title', '')
                message = notification.get('message', '')
                type_name = notification.get('type', 'Eslatma')
                user_id = notification.get('user_id', None)
            else:
                title = getattr(notification, 'title', '')
                message = getattr(notification, 'message', '')
                type_name = getattr(notification, 'type', 'Eslatma')
                user_id = getattr(notification, 'user_id', None)
            
            query = """
                INSERT INTO notifications (title, message, type, user_id, is_read, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            return self.db.execute_query(query, (
                title,
                message,
                type_name,
                user_id,
                0,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
        except Exception as e:
            print(f"❌ Error creating notification: {e}")
            return None
    
    def mark_as_read(self, notification_id):
        try:
            query = "UPDATE notifications SET is_read = 1 WHERE id = ?"
            self.db.execute_query(query, (notification_id,))
            return True
        except Exception as e:
            print(f"❌ Error marking as read: {e}")
            return False
    
    def mark_all_as_read(self, user_id=None):
        try:
            if user_id:
                query = "UPDATE notifications SET is_read = 1 WHERE user_id = ? OR user_id IS NULL"
                self.db.execute_query(query, (user_id,))
            else:
                query = "UPDATE notifications SET is_read = 1"
                self.db.execute_query(query)
            return True
        except Exception as e:
            print(f"❌ Error marking all as read: {e}")
            return False
    
    def get_unread_count(self, user_id=None):
        try:
            query = "SELECT COUNT(*) as count FROM notifications WHERE is_read = 0"
            params = []
            if user_id:
                query += " AND (user_id = ? OR user_id IS NULL)"
                params = [user_id]
            result = self.db.execute_query_one(query, params if params else None)
            return result['count'] if result else 0
        except Exception as e:
            print(f"❌ Error getting unread count: {e}")
            return 0
    
    def delete_notification(self, notification_id):
        try:
            query = "DELETE FROM notifications WHERE id = ?"
            self.db.execute_query(query, (notification_id,))
            return True
        except Exception as e:
            print(f"❌ Error deleting notification: {e}")
            return False
    
    def delete_all_notifications(self, user_id=None):
        try:
            if user_id:
                query = "DELETE FROM notifications WHERE user_id = ? OR user_id IS NULL"
                self.db.execute_query(query, (user_id,))
            else:
                query = "DELETE FROM notifications"
                self.db.execute_query(query)
            return True
        except Exception as e:
            print(f"❌ Error deleting all notifications: {e}")
            return False
    
    def get_notification_by_id(self, notification_id):
        try:
            query = "SELECT * FROM notifications WHERE id = ?"
            return self.db.execute_query_one(query, (notification_id,))
        except Exception as e:
            print(f"❌ Error getting notification: {e}")
            return None


class ShopSettingsRepository:
    def __init__(self):
        self.db = Database()
    
    def get_settings(self):
        query = "SELECT * FROM shop_settings LIMIT 1"
        return self.db.execute_query_one(query)
    
    def update_settings(self, settings):
        if isinstance(settings, dict):
            shop_name = settings.get('shop_name', '')
            address = settings.get('address', '')
            phone = settings.get('phone', '')
            logo_path = settings.get('logo_path', '')
            receipt_footer = settings.get('receipt_footer', '')
            settings_id = settings.get('id')
        else:
            shop_name = getattr(settings, 'shop_name', '')
            address = getattr(settings, 'address', '')
            phone = getattr(settings, 'phone', '')
            logo_path = getattr(settings, 'logo_path', '')
            receipt_footer = getattr(settings, 'receipt_footer', '')
            settings_id = getattr(settings, 'id', None)
        
        if settings_id:
            query = """
                UPDATE shop_settings 
                SET shop_name=?, address=?, phone=?, logo_path=?, receipt_footer=?
                WHERE id=?
            """
            return self.db.execute_query(query, (shop_name, address, phone, logo_path, receipt_footer, settings_id))
        else:
            query = """
                INSERT INTO shop_settings (shop_name, address, phone, logo_path, receipt_footer)
                VALUES (?, ?, ?, ?, ?)
            """
            return self.db.execute_query(query, (shop_name, address, phone, logo_path, receipt_footer))


class SettingRepository:
    def __init__(self):
        self.db = Database()
    
    def get(self, key):
        try:
            result = self.db.execute_query_one("SELECT * FROM settings WHERE key = ?", (key,))
            return result['value'] if result else None
        except:
            return None
    
    def set(self, key, value):
        return self.db.execute_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    
    def get_all(self):
        return self.db.execute_query("SELECT * FROM settings")


class IncomeRepository:
    def __init__(self):
        self.db = Database()
    
    def create_income(self, amount, note="", user_id=None):
        query = """INSERT INTO cash_incomes (amount, note, user_id) VALUES (?, ?, ?)"""
        return self.db.execute_insert(query, (amount, note, user_id))
    
    def get_by_date(self, date_str):
        query = "SELECT * FROM cash_incomes WHERE DATE(created_at) = DATE(?) ORDER BY created_at DESC"
        return self.db.execute_query(query, (date_str,))
    
    def get_by_date_range(self, start_date, end_date):
        query = """SELECT * FROM cash_incomes 
                   WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?) 
                   ORDER BY created_at DESC"""
        return self.db.execute_query(query, (start_date, end_date))
    
    def delete(self, income_id):
        return self.db.execute_query("DELETE FROM cash_incomes WHERE id = ?", (income_id,))


# ============================================================
# FIRM REPOSITORY
# ============================================================
class FirmRepository:
    def __init__(self):
        self.db = Database()
    
    def get_all(self):
        return self.db.execute_query("SELECT * FROM firms ORDER BY name")
    
    def get_by_id(self, firm_id):
        return self.db.execute_query_one("SELECT * FROM firms WHERE id = ?", (firm_id,))
    
    def get_by_name(self, name):
        return self.db.execute_query("SELECT * FROM firms WHERE name LIKE ?", (f'%{name}%',))
    
    def create(self, firm_data):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO firms (name, phone, address, total_debt, note)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                firm_data.get('name', ''),
                firm_data.get('phone', ''),
                firm_data.get('address', ''),
                firm_data.get('total_debt', 0),
                firm_data.get('note', '')
            ))
            conn.commit()
            firm_id = cursor.lastrowid
            conn.close()
            return firm_id
        except Exception as e:
            print(f"❌ Error creating firm: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return None
    
    def update(self, firm_data):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = """
                UPDATE firms 
                SET name=?, phone=?, address=?, total_debt=?, note=?
                WHERE id=?
            """
            cursor.execute(query, (
                firm_data.get('name', ''),
                firm_data.get('phone', ''),
                firm_data.get('address', ''),
                firm_data.get('total_debt', 0),
                firm_data.get('note', ''),
                firm_data.get('id', 0)
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error updating firm: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def delete(self, firm_id):
        try:
            return self.db.execute_query("DELETE FROM firms WHERE id = ?", (firm_id,))
        except Exception as e:
            print(f"❌ Error deleting firm: {e}")
            return False
    
    def add_debt(self, firm_id, amount):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT total_debt FROM firms WHERE id = ?", (firm_id,))
            result = cursor.fetchone()
            if result:
                new_debt = result['total_debt'] + amount
                cursor.execute("UPDATE firms SET total_debt = ? WHERE id = ?", (new_debt, firm_id))
                conn.commit()
                conn.close()
                return True
            conn.close()
            return False
        except Exception as e:
            print(f"❌ Error adding debt: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def reduce_debt(self, firm_id, amount):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT total_debt FROM firms WHERE id = ?", (firm_id,))
            result = cursor.fetchone()
            if result:
                new_debt = max(0, result['total_debt'] - amount)
                cursor.execute("UPDATE firms SET total_debt = ? WHERE id = ?", (new_debt, firm_id))
                conn.commit()
                conn.close()
                return True
            conn.close()
            return False
        except Exception as e:
            print(f"❌ Error reducing debt: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def get_total_debt(self):
        try:
            result = self.db.execute_query_one("SELECT COALESCE(SUM(total_debt), 0) as total FROM firms")
            return result['total'] if result else 0.0
        except Exception as e:
            print(f"❌ Error getting total debt: {e}")
            return 0.0


# ============================================================
# FIRM DEBT REPOSITORY - TO'LIQ YANGILANGAN
# ============================================================
class FirmDebtRepository:
    def __init__(self):
        self.db = Database()
    
    def _ensure_payments_table(self, cursor):
        """firm_debt_payments jadvalini yaratish"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS firm_debt_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debt_id INTEGER NOT NULL,
                paid_amount REAL NOT NULL DEFAULT 0,
                cash_amount REAL NOT NULL DEFAULT 0,
                card_amount REAL NOT NULL DEFAULT 0,
                payment_type TEXT DEFAULT 'Naxt',
                paid_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debt_id) REFERENCES firm_debts(id)
            )
        """)
    
    def create(self, firm_id, amount, description="", debt_type="qarz", firm_name=""):
        """Yangi qarz yoki to'lov yozish - firma nomi bilan"""
        try:
            if not firm_name:
                check_query = "SELECT name FROM firms WHERE id = ?"
                firm_data = self.db.execute_query_one(check_query, (firm_id,))
                if firm_data:
                    firm_name = firm_data.get('name', '')
                else:
                    print(f"❌ Firma ID {firm_id} topilmadi!")
                    return None
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA foreign_keys = OFF")
            
            query = """
                INSERT INTO firm_debts (firm_id, firm_name, amount, description, debt_type)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (firm_id, firm_name, amount, description, debt_type))
            
            cursor.execute("PRAGMA foreign_keys = ON")
            
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            
            return last_id
            
        except sqlite3.OperationalError as e:
            if "no column named firm_name" in str(e):
                print("⚠️ firm_name ustuni mavjud emas, qo'shilmoqda...")
                try:
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("ALTER TABLE firm_debts ADD COLUMN firm_name TEXT")
                    conn.commit()
                    conn.close()
                    print("✅ firm_name ustuni qo'shildi!")
                    return self.create(firm_id, amount, description, debt_type, firm_name)
                except Exception as e2:
                    print(f"❌ firm_name qo'shishda xatolik: {e2}")
                    return None
            else:
                print(f"❌ Error creating firm debt: {e}")
                return None
        except Exception as e:
            print(f"❌ Error creating firm debt: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return None
    
    def get_by_firm(self, firm_id):
        try:
            query = "SELECT * FROM firm_debts WHERE firm_id = ? ORDER BY created_at DESC"
            return self.db.execute_query(query, (firm_id,))
        except Exception as e:
            print(f"❌ Error getting firm debts: {e}")
            return []
    
    def get_all(self):
        try:
            query = "SELECT * FROM firm_debts ORDER BY created_at DESC"
            return self.db.execute_query(query)
        except Exception as e:
            print(f"❌ Error getting all firm debts: {e}")
            return []
    
    def get_total_debt(self, firm_id):
        try:
            query = """
                SELECT COALESCE(SUM(CASE WHEN debt_type = 'qarz' THEN amount ELSE -amount END), 0) as total
                FROM firm_debts
                WHERE firm_id = ?
            """
            result = self.db.execute_query_one(query, (firm_id,))
            return result['total'] if result else 0.0
        except Exception as e:
            print(f"❌ Error getting total debt: {e}")
            return 0.0
    
    def delete(self, debt_id):
        try:
            return self.db.execute_query("DELETE FROM firm_debts WHERE id = ?", (debt_id,))
        except Exception as e:
            print(f"❌ Error deleting debt: {e}")
            return False
    
    def get_debt_by_id(self, debt_id):
        """Qarz ID bo'yicha olish"""
        try:
            query = "SELECT * FROM firm_debts WHERE id = ?"
            return self.db.execute_query_one(query, (debt_id,))
        except Exception as e:
            print(f"❌ Error getting debt by id: {e}")
            return None
    
    def pay_debt(self, debt_id, paid_amount, paid_date=None, cash_amount=0, card_amount=0):
        """
        Qarzni to'lash (Naxt + Plastik)
        """
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            self._ensure_payments_table(cursor)
            
            debt = self.get_debt_by_id(debt_id)
            if not debt:
                conn.close()
                return {'success': False, 'message': 'Qarz topilmadi!'}
            
            current_debt = debt.get('amount', 0)
            
            if current_debt <= 0:
                conn.close()
                return {'success': False, 'message': 'Bu qarz allaqachon to\'langan!'}
            
            if not paid_date:
                paid_date = datetime.now().strftime('%Y-%m-%d')
            
            if paid_amount <= 0:
                conn.close()
                return {'success': False, 'message': 'To\'lov miqdori 0 dan katta bo\'lishi kerak!'}
            
            if paid_amount > current_debt:
                conn.close()
                return {
                    'success': False, 
                    'message': f'To\'lov miqdori qarzdan katta! Qarz: {current_debt:,.0f} so\'m'
                }
            
            cash_amount = float(cash_amount or 0)
            card_amount = float(card_amount or 0)
            
            if cash_amount == 0 and card_amount == 0:
                cash_amount = paid_amount
            
            if cash_amount > 0 or card_amount > 0:
                if round(cash_amount + card_amount, 2) != round(paid_amount, 2):
                    conn.close()
                    return {
                        'success': False,
                        'message': f'Naqd ({cash_amount:,.0f}) + Plastik ({card_amount:,.0f}) '
                                   f'to\'lov summasiga ({paid_amount:,.0f}) teng emas!'
                    }
            
            if cash_amount > 0 and card_amount > 0:
                payment_type = 'Naxt+Plastik'
            elif card_amount > 0:
                payment_type = 'Plastik'
            else:
                payment_type = 'Naxt'
            
            remaining_debt = current_debt - paid_amount
            
            if remaining_debt <= 0:
                cursor.execute(
                    """UPDATE firm_debts 
                       SET amount = 0, is_paid = 1, paid_date = ?
                       WHERE id = ?""",
                    (paid_date, debt_id)
                )
            else:
                cursor.execute(
                    """UPDATE firm_debts 
                       SET amount = ?, is_paid = 0, paid_date = ?
                       WHERE id = ?""",
                    (remaining_debt, paid_date, debt_id)
                )
            
            cursor.execute(
                """INSERT INTO firm_debt_payments 
                   (debt_id, paid_amount, cash_amount, card_amount, payment_type, paid_date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (debt_id, paid_amount, cash_amount, card_amount, payment_type, paid_date)
            )
            
            firm_id = debt.get('firm_id')
            if firm_id:
                from models.repositories import FirmRepository
                firm_repo = FirmRepository()
                firm_repo.reduce_debt(firm_id, paid_amount)
            
            conn.commit()
            conn.close()
            
            status = "✅ Qarz to'liq to'landi!" if remaining_debt <= 0 else f"⚠️ Qolgan qarz: {remaining_debt:,.0f} so'm"
            
            return {
                'success': True,
                'message': f"{status}\n"
                           f"To'langan: {paid_amount:,.0f} so'm\n"
                           f"Naxt: {cash_amount:,.0f} so'm | Plastik: {card_amount:,.0f} so'm\n"
                           f"Qolgan qarz: {remaining_debt:,.0f} so'm",
                'remaining_debt': remaining_debt,
                'paid_amount': paid_amount,
                'cash_amount': cash_amount,
                'card_amount': card_amount,
                'payment_type': payment_type,
                'debt_id': debt_id,
                'firm_id': firm_id
            }
            
        except Exception as e:
            print(f"❌ Error paying debt: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return {'success': False, 'message': str(e)}
    
    def get_payment_history(self, debt_id):
        """Bir qarz uchun to'lov tarixi"""
        try:
            query = """
                SELECT * FROM firm_debt_payments 
                WHERE debt_id = ? 
                ORDER BY created_at DESC
            """
            return self.db.execute_query(query, (debt_id,))
        except Exception as e:
            print(f"❌ Error getting payment history: {e}")
            return []
    
    def get_all_payment_history(self, start_date=None, end_date=None):
        """Barcha firm qarz to'lovlari tarixi"""
        try:
            if start_date and end_date:
                query = """
                    SELECT * FROM firm_debt_payments 
                    WHERE DATE(paid_date) BETWEEN DATE(?) AND DATE(?)
                    ORDER BY paid_date DESC
                """
                return self.db.execute_query(query, (start_date, end_date))
            else:
                query = "SELECT * FROM firm_debt_payments ORDER BY paid_date DESC"
                return self.db.execute_query(query)
        except Exception as e:
            print(f"❌ Error getting all payment history: {e}")
            return []
    
    def get_payment_summary(self, firm_id=None, start_date=None, end_date=None):
        """To'lovlar summasi (Naxt va Plastik bo'yicha)"""
        try:
            query = """
                SELECT 
                    COALESCE(SUM(cash_amount), 0) as total_cash,
                    COALESCE(SUM(card_amount), 0) as total_card,
                    COALESCE(SUM(paid_amount), 0) as total_paid,
                    COUNT(*) as payment_count
                FROM firm_debt_payments
                WHERE 1=1
            """
            params = []
            
            if firm_id:
                query += " AND debt_id IN (SELECT id FROM firm_debts WHERE firm_id = ?)"
                params.append(firm_id)
            
            if start_date and end_date:
                query += " AND DATE(paid_date) BETWEEN DATE(?) AND DATE(?)"
                params.extend([start_date, end_date])
            
            result = self.db.execute_query_one(query, params if params else None)
            return {
                'total_cash': result['total_cash'] if result else 0,
                'total_card': result['total_card'] if result else 0,
                'total_paid': result['total_paid'] if result else 0,
                'payment_count': result['payment_count'] if result else 0
            }
        except Exception as e:
            print(f"❌ Error getting payment summary: {e}")
            return {'total_cash': 0, 'total_card': 0, 'total_paid': 0, 'payment_count': 0}


# ============================================================
# CATEGORY REPOSITORY - YANGI QO'SHILDI
# ============================================================
class CategoryRepository:
    def __init__(self):
        self.db = Database()
    
    def get_all(self):
        """Barcha kategoriyalarni olish"""
        try:
            query = "SELECT * FROM categories ORDER BY name"
            return self.db.execute_query(query)
        except Exception as e:
            print(f"❌ Error getting categories: {e}")
            return []
    
    def get_by_id(self, category_id):
        """Kategoriyani ID bo'yicha olish"""
        try:
            query = "SELECT * FROM categories WHERE id = ?"
            return self.db.execute_query_one(query, (category_id,))
        except Exception as e:
            print(f"❌ Error getting category: {e}")
            return None
    
    def create(self, name, parent_id=None, icon=None, color=None):
        """Yangi kategoriya yaratish"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO categories (name, parent_id, icon, color)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, (name, parent_id, icon, color))
            conn.commit()
            category_id = cursor.lastrowid
            conn.close()
            return category_id
        except Exception as e:
            print(f"❌ Error creating category: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return None
    
    def update(self, category_id, name, parent_id=None, icon=None, color=None):
        """Kategoriyani yangilash"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = """
                UPDATE categories 
                SET name=?, parent_id=?, icon=?, color=?
                WHERE id=?
            """
            cursor.execute(query, (name, parent_id, icon, color, category_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error updating category: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def delete(self, category_id):
        """Kategoriyani o'chirish - ichidagi mahsulotlar kategoriyasiz qoladi"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Mahsulotlarni kategoriyasiz qilish
            cursor.execute(
                "UPDATE products SET category_id = NULL WHERE category_id = ?",
                (category_id,)
            )
            # Kategoriyani o'chirish
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error deleting category: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def get_products_by_category(self, category_id):
        """Kategoriyadagi barcha mahsulotlarni olish"""
        try:
            query = "SELECT * FROM products WHERE category_id = ? AND is_active = 1 ORDER BY name"
            return self.db.execute_query(query, (category_id,))
        except Exception as e:
            print(f"❌ Error getting products by category: {e}")
            return []
    
    def assign_products(self, product_ids: list, category_id):
        """Mahsulotlarni kategoriyaga biriktirish"""
        try:
            if not product_ids:
                return True
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            placeholders = ','.join('?' * len(product_ids))
            query = f"UPDATE products SET category_id = ? WHERE id IN ({placeholders})"
            cursor.execute(query, (category_id, *product_ids))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error assigning products to category: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def get_parent_categories(self):
        """Asosiy kategoriyalarni olish (parent_id = NULL)"""
        try:
            query = "SELECT * FROM categories WHERE parent_id IS NULL ORDER BY name"
            return self.db.execute_query(query)
        except Exception as e:
            print(f"❌ Error getting parent categories: {e}")
            return []
    
    def get_subcategories(self, parent_id):
        """Ost kategoriyalarni olish"""
        try:
            query = "SELECT * FROM categories WHERE parent_id = ? ORDER BY name"
            return self.db.execute_query(query, (parent_id,))
        except Exception as e:
            print(f"❌ Error getting subcategories: {e}")
            return []
    
    def get_category_tree(self):
        """Kategoriyalar daraxtini olish"""
        try:
            all_categories = self.get_all()
            if not all_categories:
                return []
            
            # Kategoriyalarni id bo'yicha guruhlash
            categories_dict = {cat['id']: dict(cat, children=[]) for cat in all_categories}
            
            # Daraxtni shakllantirish
            tree = []
            for cat in all_categories:
                if cat['parent_id'] is None:
                    tree.append(categories_dict[cat['id']])
                elif cat['parent_id'] in categories_dict:
                    categories_dict[cat['parent_id']]['children'].append(categories_dict[cat['id']])
            
            return tree
        except Exception as e:
            print(f"❌ Error getting category tree: {e}")
            return []
    
    def get_category_count(self):
        """Kategoriyalar soni"""
        try:
            result = self.db.execute_query_one("SELECT COUNT(*) as count FROM categories")
            return result['count'] if result else 0
        except Exception as e:
            print(f"❌ Error getting category count: {e}")
            return 0