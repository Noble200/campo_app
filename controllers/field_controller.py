# controllers/field_controller.py
from models.field import Field
from config.firebase_config import get_firestore_db
import datetime

class FieldController:
    def __init__(self):
        self.db = get_firestore_db()
        self.collection = 'fields'
    
    def get_all(self):
        """Obtiene todos los campos"""
        fields = []
        docs = self.db.collection(self.collection).stream()
        
        for doc in docs:
            field = Field.from_dict(doc.id, doc.to_dict())
            fields.append(field)
        
        return fields
    
    def get_by_id(self, field_id):
        """Obtiene un campo por su ID"""
        doc = self.db.collection(self.collection).document(field_id).get()
        if doc.exists:
            return Field.from_dict(doc.id, doc.to_dict())
        return None
    
    def create(self, field):
        """Crea un nuevo campo"""
        if not field.name or not field.location:
            return {"success": False, "error": "Nombre y ubicación son obligatorios"}
        
        try:
            doc_ref = self.db.collection(self.collection).document()
            field.id = doc_ref.id
            doc_ref.set(field.to_dict())
            
            # Registrar en log de auditoría
            self._log_action("create", field.id, field.to_dict())
            
            return {"success": True, "id": field.id}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update(self, field_id, data):
        """Actualiza un campo existente"""
        try:
            doc_ref = self.db.collection(self.collection).document(field_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return {"success": False, "error": "Campo no encontrado"}
            
            # Actualizar solo los campos proporcionados
            update_data = {}
            if "name" in data and data["name"]:
                update_data["name"] = data["name"]
            if "location" in data:
                update_data["location"] = data["location"]
            if "size" in data:
                update_data["size"] = data["size"]
            if "crop_type" in data:
                update_data["crop_type"] = data["crop_type"]
            if "status" in data:
                update_data["status"] = data["status"]
            if "risk_level" in data:
                update_data["risk_level"] = data["risk_level"]
            if "pests" in data:
                update_data["pests"] = data["pests"]
            if "workers" in data:
                update_data["workers"] = data["workers"]
            
            update_data["updated_at"] = datetime.datetime.now()
            
            doc_ref.update(update_data)
            
            # Registrar en log de auditoría
            self._log_action("update", field_id, update_data)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete(self, field_id):
        """Elimina un campo"""
        try:
            doc_ref = self.db.collection(self.collection).document(field_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return {"success": False, "error": "Campo no encontrado"}
            
            # Verificar si hay operaciones pendientes asociadas
            fumigation_docs = self.db.collection('fumigations').where("field_id", "==", field_id).limit(1).stream()
            
            if any(fumigation_docs):
                return {"success": False, "error": "No se puede eliminar el campo porque tiene fumigaciones programadas"}
            
            # Guardar datos para log antes de eliminar
            old_data = doc.to_dict()
            
            # Eliminar documento
            doc_ref.delete()
            
            # Registrar en log de auditoría
            self._log_action("delete", field_id, old_data)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _log_action(self, action, field_id, data):
        """Registra acciones en el log de auditoría"""
        log_data = {
            "collection": self.collection,
            "document_id": field_id,
            "action": action,
            "data": data,
            "timestamp": datetime.datetime.now(),
            "user_id": "current_user_id"  # Esto debe ser reemplazado con el ID del usuario actual
        }
        
        self.db.collection('audit_logs').add(log_data)