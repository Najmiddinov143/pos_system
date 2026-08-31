# controllers/report_controller.py
from models.repositories import ProductRepository, SaleRepository, ExpenseRepository
from datetime import datetime, timedelta

class ReportController:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.sale_repo = SaleRepository()
        self.expense_repo = ExpenseRepository()
    
    def get_dashboard_stats(self):
        try:
            products = self.product_repo.get_all()
            today = datetime.now().date()
            
            # To'lov turlari bo'yicha statistikalar
            conn = self.product_repo.db.get_connection()
            cursor = conn.cursor()
            
            # Payment stats
            payment_stats = cursor.execute('''
                SELECT 
                    COALESCE(SUM(CASE WHEN payment_type = 'Naxt' THEN total_amount ELSE 0 END), 0) as cash,
                    COALESCE(SUM(CASE WHEN payment_type = 'Plastik' THEN total_amount ELSE 0 END), 0) as card,
                    COALESCE(SUM(CASE WHEN payment_type = 'Nasiya' THEN total_amount ELSE 0 END), 0) as debt,
                    COALESCE(SUM(bonus_amount), 0) as bonus_total
                FROM sales WHERE DATE(created_at) = ?
            ''', (today,)).fetchone()
            
            conn.close()
            
            total_profit = self.sale_repo.get_total_profit()
            total_expense = self.expense_repo.get_total()
            
            return {
                'products_count': len(products),
                'total_cost': sum(p['cost_price'] * p['quantity'] for p in products),
                'total_value': sum(p['sell_price'] * p['quantity'] for p in products),
                'today_sales': self.sale_repo.get_total_sales(today, today),
                'today_profit': self.sale_repo.get_total_profit(today, today),
                'total_profit': total_profit,
                'total_expense': total_expense,
                'net_profit': total_profit - total_expense,
                'cash_sales': payment_stats['cash'] if payment_stats else 0,
                'card_sales': payment_stats['card'] if payment_stats else 0,
                'debt_sales': payment_stats['debt'] if payment_stats else 0,
                'bonus_total': payment_stats['bonus_total'] if payment_stats else 0
            }
        except Exception as e:
            print(f"Error in get_dashboard_stats: {e}")
            return {
                'products_count': 0,
                'total_cost': 0,
                'total_value': 0,
                'today_sales': 0,
                'today_profit': 0,
                'total_profit': 0,
                'total_expense': 0,
                'net_profit': 0,
                'cash_sales': 0,
                'card_sales': 0,
                'debt_sales': 0,
                'bonus_total': 0
            }
    
    def get_daily_sales(self, days=7):
        try:
            end = datetime.now().date()
            start = end - timedelta(days=days-1)
            dates, amounts = [], []
            for i in range(days):
                d = start + timedelta(days=i)
                dates.append(d.strftime("%d.%m"))
                amounts.append(self.sale_repo.get_total_sales(d, d))
            return {'dates': dates, 'amounts': amounts}
        except Exception as e:
            print(f"Error in get_daily_sales: {e}")
            return {'dates': [], 'amounts': []}
    
    def get_monthly_sales(self, months=12):
        try:
            end = datetime.now().date()
            start = end.replace(day=1)
            months_list, amounts = [], []
            for i in range(months):
                d = start + timedelta(days=30*i)
                month_start = d.replace(day=1)
                if i == months-1:
                    month_end = end
                else:
                    next_month = month_start + timedelta(days=32)
                    month_end = next_month.replace(day=1) - timedelta(days=1)
                amounts.append(self.sale_repo.get_total_sales(month_start, month_end))
                months_list.append(d.strftime("%b"))
            return {'months': months_list, 'amounts': amounts}
        except Exception as e:
            print(f"Error in get_monthly_sales: {e}")
            return {'months': [], 'amounts': []}
    
    def get_daily_profit(self, days=7):
        try:
            end = datetime.now().date()
            start = end - timedelta(days=days-1)
            data = []
            for i in range(days):
                d = start + timedelta(days=i)
                data.append({
                    'date': d.strftime("%d.%m"),
                    'profit': self.sale_repo.get_total_profit(d, d)
                })
            return data
        except Exception as e:
            print(f"Error in get_daily_profit: {e}")
            return []
    
    def get_daily_cost(self, days=7):
        try:
            end = datetime.now().date()
            start = end - timedelta(days=days-1)
            data = []
            for i in range(days):
                d = start + timedelta(days=i)
                data.append({
                    'date': d.strftime("%d.%m"),
                    'amount': 0  # Xarajatlar uchun
                })
            return data
        except Exception as e:
            print(f"Error in get_daily_cost: {e}")
            return []
    
    def get_top_products(self, limit=10):
        try:
            conn = self.product_repo.db.get_connection()
            cursor = conn.cursor()
            result = cursor.execute('''
                SELECT 
                    p.id,
                    p.name,
                    COALESCE(SUM(si.quantity), 0) as total_quantity,
                    COALESCE(SUM(si.subtotal), 0) as total_amount,
                    COALESCE(SUM(si.subtotal - (si.cost_price * si.quantity)), 0) as total_profit
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                GROUP BY p.id, p.name
                ORDER BY total_quantity DESC
                LIMIT ?
            ''', (limit,)).fetchall()
            conn.close()
            return [dict(row) for row in result] if result else []
        except Exception as e:
            print(f"Error in get_top_products: {e}")
            return []
    
    def get_total_profit(self, start_date=None, end_date=None):
        try:
            return self.sale_repo.get_total_profit(start_date, end_date)
        except Exception as e:
            print(f"Error in get_total_profit: {e}")
            return 0
    
    def get_all_sales(self):
        try:
            return self.sale_repo.get_sales_with_items()
        except Exception as e:
            print(f"Error in get_all_sales: {e}")
            return []
    
    def get_sale_items(self, sale_id):
        try:
            conn = self.product_repo.db.get_connection()
            cursor = conn.cursor()
            result = cursor.execute('''
                SELECT si.*, p.name as product_name, p.unit
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                WHERE si.sale_id = ?
            ''', (sale_id,)).fetchall()
            conn.close()
            return [dict(row) for row in result] if result else []
        except Exception as e:
            print(f"Error in get_sale_items: {e}")
            return []