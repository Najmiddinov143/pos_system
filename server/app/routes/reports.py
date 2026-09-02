from fastapi import APIRouter
from datetime import datetime
from ..database import db

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard():
    today = datetime.now().date()
    
    # Bugungi savdo
    today_sales = db.execute_one(
        "SELECT COALESCE(SUM(total_amount), 0) FROM sales WHERE DATE(created_at) = %s",
        (today,)
    )
    
    # Bugungi foyda
    today_profit = db.execute_one(
        "SELECT COALESCE(SUM(total_profit), 0) FROM sales WHERE DATE(created_at) = %s",
        (today,)
    )
    
    # Jami mahsulotlar
    total_products = db.execute_one(
        "SELECT COUNT(*) FROM products"
    )
    
    # Kam qolgan mahsulotlar
    low_stock = db.execute_one(
        "SELECT COUNT(*) FROM products WHERE quantity <= min_quantity"
    )
    
    return {
        "today_sales": today_sales[0] if today_sales else 0,
        "today_profit": today_profit[0] if today_profit else 0,
        "total_products": total_products[0] if total_products else 0,
        "low_stock": low_stock[0] if low_stock else 0,
        "today_balance": today_sales[0] if today_sales else 0,
        "total_expense": 0,
        "bonus_total": 0,
        "net_profit": today_profit[0] if today_profit else 0,
        "cash_sales": today_sales[0] if today_sales else 0,
        "card_sales": 0,
        "debt_sales": 0,
        "total_profit": 0
    }

@router.get("/top-products")
async def get_top_products(date: str = None):
    if not date:
        date = datetime.now().date()
    
    query = """
        SELECT 
            p.name,
            SUM(si.quantity) as quantity,
            SUM(si.subtotal) as total
        FROM sale_items si
        JOIN products p ON si.product_id = p.id
        JOIN sales s ON si.sale_id = s.id
        WHERE DATE(s.created_at) = %s
        GROUP BY p.id, p.name
        ORDER BY quantity DESC
        LIMIT 10
    """
    
    products = db.execute_query(query, (date,))
    
    result = []
    for p in products:
        result.append({
            "name": p[0],
            "quantity": float(p[1]) if p[1] else 0,
            "total": float(p[2]) if p[2] else 0
        })
    
    return result