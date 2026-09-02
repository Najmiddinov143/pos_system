from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database import db

router = APIRouter()

class ProductCreate(BaseModel):
    name: str
    category: Optional[str] = None
    cost_price: float = 0
    sell_price: float = 0
    quantity: float = 0
    unit: Optional[str] = None
    min_quantity: float = 0
    note: Optional[str] = None
    barcode: Optional[str] = None
    supplier: Optional[str] = None

@router.get("/")
async def get_products():
    return db.execute_query("SELECT * FROM products ORDER BY id DESC")

@router.post("/")
async def create_product(product: ProductCreate):
    query = """
        INSERT INTO products 
        (name, category, cost_price, sell_price, quantity, unit, min_quantity, note, barcode, supplier)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    product_id = db.execute_insert(
        query,
        (product.name, product.category, product.cost_price, product.sell_price,
         product.quantity, product.unit, product.min_quantity, product.note,
         product.barcode, product.supplier)
    )
    return {"id": product_id, "message": "Product created"}

@router.put("/{product_id}")
async def update_product(product_id: int, product: ProductCreate):
    query = """
        UPDATE products SET 
        name=%s, category=%s, cost_price=%s, sell_price=%s, quantity=%s,
        unit=%s, min_quantity=%s, note=%s, barcode=%s, supplier=%s
        WHERE id=%s
    """
    db.execute_update(
        query,
        (product.name, product.category, product.cost_price, product.sell_price,
         product.quantity, product.unit, product.min_quantity, product.note,
         product.barcode, product.supplier, product_id)
    )
    return {"message": "Product updated"}

@router.delete("/{product_id}")
async def delete_product(product_id: int):
    db.execute_update("DELETE FROM products WHERE id = %s", (product_id,))
    return {"message": "Product deleted"}