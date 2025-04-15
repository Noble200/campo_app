# models/field.py
import datetime
from config.firebase_config import get_firestore_db

class Field:
    def __init__(self, id=None, name=None, location=None, size=None, crop_type=None, status=None, risk_level=None, pests=None, workers=None):
        self.id = id
        self.name = name
        self.location = location
        self.size = size
        self.crop_type = crop_type
        self.status = status
        self.risk_level = risk_level
        self.pests = pests or []
        self.workers = workers or []
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
    
    def to_dict(self):
        return {
            "name": self.name,
            "location": self.location,
            "size": self.size,
            "crop_type": self.crop_type,
            "status": self.status,
            "risk_level": self.risk_level,
            "pests": self.pests,
            "workers": self.workers,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def from_dict(id, data):
        field = Field(
            id=id,
            name=data.get("name"),
            location=data.get("location"),
            size=data.get("size"),
            crop_type=data.get("crop_type"),
            status=data.get("status"),
            risk_level=data.get("risk_level"),
            pests=data.get("pests", []),
            workers=data.get("workers", [])
        )
        field.created_at = data.get("created_at")
        field.updated_at = data.get("updated_at")
        return field