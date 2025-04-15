# models/warehouse.py
import datetime
from config.firebase_config import get_firestore_db

class Warehouse:
    def __init__(self, id=None, name=None, location=None, capacity=None, description=None):
        self.id = id
        self.name = name
        self.location = location
        self.capacity = capacity
        self.description = description
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
    
    def to_dict(self):
        return {
            "name": self.name,
            "location": self.location,
            "capacity": self.capacity,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def from_dict(id, data):
        warehouse = Warehouse(
            id=id,
            name=data.get("name"),
            location=data.get("location"),
            capacity=data.get("capacity"),
            description=data.get("description")
        )
        warehouse.created_at = data.get("created_at")
        warehouse.updated_at = data.get("updated_at")
        return warehouse