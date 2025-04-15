# models/fumigation.py
import datetime
from config.firebase_config import get_firestore_db

class Fumigation:
    def __init__(self, id=None, field_id=None, applicator_id=None, products=None, date=None, 
                 status="scheduled", notes=None, dosage=None):
        self.id = id
        self.field_id = field_id  # ID del campo a fumigar
        self.applicator_id = applicator_id  # ID del usuario aplicador
        self.products = products or []  # Lista de IDs de productos a utilizar
        self.date = date or datetime.datetime.now()  # Fecha programada
        self.status = status  # Estado: scheduled, in_progress, completed, cancelled
        self.notes = notes  # Notas adicionales
        self.dosage = dosage or {}  # Diccionario de dosis por producto: {product_id: cantidad}
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        self.started_at = None  # Fecha de inicio real
        self.completed_at = None  # Fecha de finalización real
    
    def to_dict(self):
        return {
            "field_id": self.field_id,
            "applicator_id": self.applicator_id,
            "products": self.products,
            "date": self.date,
            "status": self.status,
            "notes": self.notes,
            "dosage": self.dosage,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }
    
    @staticmethod
    def from_dict(id, data):
        fumigation = Fumigation(
            id=id,
            field_id=data.get("field_id"),
            applicator_id=data.get("applicator_id"),
            products=data.get("products", []),
            date=data.get("date"),
            status=data.get("status", "scheduled"),
            notes=data.get("notes"),
            dosage=data.get("dosage", {})
        )
        fumigation.created_at = data.get("created_at")
        fumigation.updated_at = data.get("updated_at")
        fumigation.started_at = data.get("started_at")
        fumigation.completed_at = data.get("completed_at")
        return fumigation