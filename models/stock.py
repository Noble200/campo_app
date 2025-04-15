# models/stock.py
import datetime
from config.firebase_config import get_firestore_db

class Stock:
    def __init__(self, id=None, product_name=None, quantity=None, unit=None, warehouse_id=None, 
                 status="received", category=None, purchase_date=None, expiry_date=None):
        self.id = id
        self.product_name = product_name
        self.quantity = quantity
        self.unit = unit  # kg, ton, g, lb, etc.
        self.warehouse_id = warehouse_id
        self.status = status  # "purchased" (comprado pero no recibido), "received" (recibido en almacén)
        self.category = category  # categoría del producto (fertilizante, pesticida, semilla, etc.)
        self.purchase_date = purchase_date or datetime.datetime.now()
        self.expiry_date = expiry_date
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
    
    def to_dict(self):
        return {
            "product_name": self.product_name,
            "quantity": self.quantity,
            "unit": self.unit,
            "warehouse_id": self.warehouse_id,
            "status": self.status,
            "category": self.category,
            "purchase_date": self.purchase_date,
            "expiry_date": self.expiry_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def from_dict(id, data):
        stock = Stock(
            id=id,
            product_name=data.get("product_name"),
            quantity=data.get("quantity"),
            unit=data.get("unit"),
            warehouse_id=data.get("warehouse_id"),
            status=data.get("status", "received"),
            category=data.get("category"),
            purchase_date=data.get("purchase_date"),
            expiry_date=data.get("expiry_date")
        )
        stock.created_at = data.get("created_at")
        stock.updated_at = data.get("updated_at")
        return stock