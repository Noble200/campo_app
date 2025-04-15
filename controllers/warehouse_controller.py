# controllers/warehouse_controller.py
from models.warehouse import Warehouse
from config.firebase_config import get_firestore_db
import datetime

class WarehouseController:
    def __init__(self):
        self.db = get_firestore_db()
        self.collection = 'warehouses'
    
    def get_all(self):
        """Obtiene todos los almacenes"""
        warehouses = []
        docs = self.db.collection(self.collection).stream()
        
        for doc in docs:
            warehouse = Warehouse.from_dict(doc.id, doc.to_dict())
            warehouses.append(warehouse)
        
        return warehouses
    
    def get_by_id(self, warehouse_id):
        """Obtiene un almacén por su ID"""
        doc = self.db.collection(self.collection).document(warehouse_id).get()
        if doc.exists:
            return Warehouse.from_dict(doc.id, doc.to_dict())
        return None
    
    def create(self, warehouse):
        """Crea un nuevo almacén"""
        if not warehouse.name or not warehouse.location:
            return {"success": False, "error": "Nombre y ubicación son obligatorios"}
        
        try:
            doc_ref = self.db.collection(self.collection).document()
            warehouse.id = doc_ref.id
            doc_ref.set(warehouse.to_dict())
            
            # Registrar en log de auditoría
            self._log_action("create", warehouse.id, warehouse.to_dict())
            
            return {"success": True, "id": warehouse.id}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update(self, warehouse_id, data):
        """Actualiza un almacén existente"""
        try:
            doc_ref = self.db.collection(self.collection).document(warehouse_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return {"success": False, "error": "Almacén no encontrado"}
            
            # Actualizar solo los campos proporcionados
            update_data = {}
            if "name" in data and data["name"]:
                update_data["name"] = data["name"]
            if "location" in data:
                update_data["location"] = data["location"]
            if "capacity" in data:
                update_data["capacity"] = data["capacity"]
            if "description" in data:
                update_data["description"] = data["description"]
            
            update_data["updated_at"] = datetime.datetime.now()
            
            doc_ref.update(update_data)
            
            # Registrar en log de auditoría
            self._log_action("update", warehouse_id, update_data)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete(self, warehouse_id):
        """Elimina un almacén"""
        try:
            # Verificar si hay stock asociado
            stock_docs = self.db.collection('stock').where("warehouse_id", "==", warehouse_id).limit(1).stream()
            
            if any(stock_docs):
                return {"success": False, "error": "No se puede eliminar el almacén porque tiene productos asociados"}
            
            doc_ref = self.db.collection(self.collection).document(warehouse_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return {"success": False, "error": "Almacén no encontrado"}
            
            # Guardar datos para log antes de eliminar
            old_data = doc.to_dict()
            
            # Eliminar documento
            doc_ref.delete()
            
            # Registrar en log de auditoría
            self._log_action("delete", warehouse_id, old_data)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _log_action(self, action, warehouse_id, data):
        """Registra acciones en el log de auditoría"""
        log_data = {
            "collection": self.collection,
            "document_id": warehouse_id,
            "action": action,
            "data": data,
            "timestamp": datetime.datetime.now(),
            "user_id": "current_user_id"  # Esto debe ser reemplazado con el ID del usuario actual
        }
        
        self.db.collection('audit_logs').add(log_data)