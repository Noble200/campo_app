# controllers/fumigation_controller.py
from models.fumigation import Fumigation
from config.firebase_config import get_firestore_db
import datetime

class FumigationController:
    def __init__(self):
        self.db = get_firestore_db()
        self.collection = 'fumigations'
    
    def get_all(self, field_id=None, applicator_id=None, status=None):
        """Obtiene todas las fumigaciones, opcionalmente filtradas por campo, aplicador y/o estado"""
        fumigations = []
        query = self.db.collection(self.collection)
        
        # Aplicar filtros si se proporcionan
        if field_id:
            query = query.where("field_id", "==", field_id)
        if applicator_id:
            query = query.where("applicator_id", "==", applicator_id)
        if status:
            query = query.where("status", "==", status)
            
        docs = query.stream()
        
        for doc in docs:
            fumigation = Fumigation.from_dict(doc.id, doc.to_dict())
            fumigations.append(fumigation)
        
        return fumigations
    
    def get_by_id(self, fumigation_id):
        """Obtiene una fumigación por su ID"""
        doc = self.db.collection(self.collection).document(fumigation_id).get()
        if doc.exists:
            return Fumigation.from_dict(doc.id, doc.to_dict())
        return None
    
    def create(self, fumigation):
        """Crea una nueva fumigación"""
        if not fumigation.field_id:
            return {"success": False, "error": "Se requiere un campo para la fumigación"}
        
        if not fumigation.applicator_id:
            return {"success": False, "error": "Se requiere un aplicador para la fumigación"}
        
        if not fumigation.products or len(fumigation.products) == 0:
            return {"success": False, "error": "Se requiere al menos un producto para la fumigación"}
        
        try:
            # Verificar que el campo exista
            field_doc = self.db.collection('fields').document(fumigation.field_id).get()
            if not field_doc.exists:
                return {"success": False, "error": "El campo especificado no existe"}
            
            # Verificar que el aplicador exista
            applicator_doc = self.db.collection('users').document(fumigation.applicator_id).get()
            if not applicator_doc.exists:
                return {"success": False, "error": "El aplicador especificado no existe"}
            
            # Verificar que los productos existan en stock
            for product_id in fumigation.products:
                product_doc = self.db.collection('stock').document(product_id).get()
                if not product_doc.exists:
                    return {"success": False, "error": f"El producto con ID {product_id} no existe en stock"}
                
                # Verificar que el producto esté recibido
                product_data = product_doc.to_dict()
                if product_data.get("status") != "received":
                    return {"success": False, "error": f"El producto con ID {product_id} no está disponible para uso"}
                
                # Verificar que haya cantidad suficiente
                quantity = product_data.get("quantity", 0)
                if quantity <= 0:
                    return {"success": False, "error": f"El producto con ID {product_id} no tiene cantidad suficiente"}
            
            # Crear el documento en Firestore
            doc_ref = self.db.collection(self.collection).document()
            fumigation.id = doc_ref.id
            doc_ref.set(fumigation.to_dict())
            
            # Registrar en log de auditoría
            self._log_action("create", fumigation.id, fumigation.to_dict())
            
            return {"success": True, "id": fumigation.id}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update(self, fumigation_id, data):
        """Actualiza una fumigación existente"""
        try:
            doc_ref = self.db.collection(self.collection).document(fumigation_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return {"success": False, "error": "Fumigación no encontrada"}
            
            # Obtener datos actuales
            current_data = doc.to_dict()
            
            # Verificar si se puede actualizar según el estado
            current_status = current_data.get("status")
            new_status = data.get("status", current_status)
            
            # Si la fumigación está completada o cancelada, solo se puede actualizar si se está cambiando a un estado previo
            if current_status in ["completed", "cancelled"] and new_status in ["completed", "cancelled"] and current_status != new_status:
                return {"success": False, "error": f"No se puede cambiar el estado de '{current_status}' a '{new_status}'"}
            
            # Verificar que el campo exista si se está actualizando
            if "field_id" in data and data["field_id"]:
                field_doc = self.db.collection('fields').document(data["field_id"]).get()
                if not field_doc.exists:
                    return {"success": False, "error": "El campo especificado no existe"}
            
            # Verificar que el aplicador exista si se está actualizando
            if "applicator_id" in data and data["applicator_id"]:
                applicator_doc = self.db.collection('users').document(data["applicator_id"]).get()
                if not applicator_doc.exists:
                    return {"success": False, "error": "El aplicador especificado no existe"}
            
            # Verificar productos si se están actualizando
            if "products" in data and data["products"]:
                for product_id in data["products"]:
                    product_doc = self.db.collection('stock').document(product_id).get()
                    if not product_doc.exists:
                        return {"success": False, "error": f"El producto con ID {product_id} no existe en stock"}
                    
                    # Verificar que el producto esté recibido
                    product_data = product_doc.to_dict()
                    if product_data.get("status") != "received":
                        return {"success": False, "error": f"El producto con ID {product_id} no está disponible para uso"}
                    
                    # Verificar que haya cantidad suficiente
                    quantity = product_data.get("quantity", 0)
                    if quantity <= 0:
                        return {"success": False, "error": f"El producto con ID {product_id} no tiene cantidad suficiente"}
            
            # Actualizar solo los campos proporcionados
            update_data = {}
            if "field_id" in data:
                update_data["field_id"] = data["field_id"]
            if "applicator_id" in data:
                update_data["applicator_id"] = data["applicator_id"]
            if "products" in data:
                update_data["products"] = data["products"]
            if "date" in data:
                update_data["date"] = data["date"]
            if "status" in data:
                update_data["status"] = data["status"]
            if "notes" in data:
                update_data["notes"] = data["notes"]
            if "dosage" in data:
                update_data["dosage"] = data["dosage"]
            
            update_data["updated_at"] = datetime.datetime.now()
            
            # Si se está completando la fumigación, registrar la fecha de finalización
            if new_status == "completed" and current_status != "completed":
                update_data["completed_at"] = datetime.datetime.now()
            
            # Actualizar en Firestore
            doc_ref.update(update_data)
            
            # Registrar en log de auditoría
            self._log_action("update", fumigation_id, update_data)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete(self, fumigation_id):
        """Elimina una fumigación"""
        try:
            doc_ref = self.db.collection(self.collection).document(fumigation_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return {"success": False, "error": "Fumigación no encontrada"}
            
            # Verificar si la fumigación está en curso o programada
            fumigation_data = doc.to_dict()
            status = fumigation_data.get("status")
            
            if status == "in_progress":
                return {"success": False, "error": "No se puede eliminar una fumigación en curso"}
            
            # Guardar datos para log antes de eliminar
            old_data = doc.to_dict()
            
            # Eliminar documento
            doc_ref.delete()
            
            # Registrar en log de auditoría
            self._log_action("delete", fumigation_id, old_data)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def change_status(self, fumigation_id, new_status):
        """Cambia el estado de una fumigación"""
        valid_statuses = ["scheduled", "in_progress", "completed", "cancelled"]
        
        if new_status not in valid_statuses:
            return {"success": False, "error": f"Estado no válido. Debe ser uno de: {', '.join(valid_statuses)}"}
        
        try:
            doc_ref = self.db.collection(self.collection).document(fumigation_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return {"success": False, "error": "Fumigación no encontrada"}
            
            fumigation_data = doc.to_dict()
            current_status = fumigation_data.get("status")
            
            # Validar transiciones de estado
            valid_transitions = {
                "scheduled": ["in_progress", "cancelled"],
                "in_progress": ["completed", "cancelled"],
                "completed": [],  # No se puede cambiar desde completado
                "cancelled": ["scheduled"]  # Solo se puede reactivar
            }
            
            if new_status not in valid_transitions.get(current_status, []):
                return {"success": False, "error": f"No se puede cambiar el estado de '{current_status}' a '{new_status}'"}
            
            # Preparar datos de actualización
            update_data = {
                "status": new_status,
                "updated_at": datetime.datetime.now()
            }
            
            # Si se está completando, registrar la fecha de finalización
            if new_status == "completed":
                update_data["completed_at"] = datetime.datetime.now()
            
            # Si se está iniciando, registrar la fecha de inicio
            if new_status == "in_progress" and current_status == "scheduled":
                update_data["started_at"] = datetime.datetime.now()
            
            # Actualizar en Firestore
            doc_ref.update(update_data)
            
            # Registrar en log de auditoría
            self._log_action("change_status", fumigation_id, {"from": current_status, "to": new_status})
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_scheduled_fumigations(self, days=7):
        """Obtiene las fumigaciones programadas para los próximos días"""
        try:
            # Calcular fecha límite
            today = datetime.datetime.now()
            end_date = today + datetime.timedelta(days=days)
            
            # Obtener fumigaciones programadas
            fumigations = []
            query = self.db.collection(self.collection).where("status", "==", "scheduled")
            docs = query.stream()
            
            for doc in docs:
                fumigation = Fumigation.from_dict(doc.id, doc.to_dict())
                
                # Filtrar por fecha si está dentro del rango
                if fumigation.date and fumigation.date <= end_date:
                    fumigations.append(fumigation)
            
            return fumigations
        except Exception as e:
            print(f"Error al obtener fumigaciones programadas: {str(e)}")
            return []
    
    def get_fumigation_statistics(self):
        """Obtiene estadísticas de fumigaciones"""
        try:
            # Obtener todas las fumigaciones
            fumigations = self.get_all()
            
            if not fumigations:
                return {"success": True, "data": {}}
            
            # Preparar datos de estadísticas
            stats = {
                "total": len(fumigations),
                "by_status": {
                    "scheduled": 0,
                    "in_progress": 0,
                    "completed": 0,
                    "cancelled": 0
                },
                "by_field": {},
                "by_applicator": {},
                "by_month": {}
            }
            
            # Procesar cada fumigación
            for fumigation in fumigations:
                # Contar por estado
                status = fumigation.status or "scheduled"
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                
                # Contar por campo
                if fumigation.field_id:
                    stats["by_field"][fumigation.field_id] = stats["by_field"].get(fumigation.field_id, 0) + 1
                
                # Contar por aplicador
                if fumigation.applicator_id:
                    stats["by_applicator"][fumigation.applicator_id] = stats["by_applicator"].get(fumigation.applicator_id, 0) + 1
                
                # Contar por mes
                if fumigation.date:
                    month_key = fumigation.date.strftime("%Y-%m")
                    stats["by_month"][month_key] = stats["by_month"].get(month_key, 0) + 1
            
            return {"success": True, "data": stats}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _log_action(self, action, fumigation_id, data):
        """Registra acciones en el log de auditoría"""
        try:
            log_data = {
                "collection": self.collection,
                "document_id": fumigation_id,
                "action": action,
                "data": data,
                "timestamp": datetime.datetime.now(),
                "user_id": "current_user_id"  # Esto debe ser reemplazado con el ID del usuario actual
            }
            
            self.db.collection('audit_logs').add(log_data)
        except Exception as e:
            print(f"Error al registrar en log de auditoría: {str(e)}")