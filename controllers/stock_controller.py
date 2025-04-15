# controllers/stock_controller.py
from models.stock import Stock
from config.firebase_config import get_firestore_db
import datetime

class StockController:
    def __init__(self):
        self.db = get_firestore_db()
        self.collection = 'stock'
    
    def get_all(self, warehouse_id=None, status=None):
        """Obtiene todos los productos en stock, opcionalmente filtrados por almacén y/o estado"""
        stock_items = []
        query = self.db.collection(self.collection)
        
        # Aplicar filtros si se proporcionan
        if warehouse_id:
            query = query.where("warehouse_id", "==", warehouse_id)
        if status:
            query = query.where("status", "==", status)
            
        docs = query.stream()
        
        for doc in docs:
            stock_item = Stock.from_dict(doc.id, doc.to_dict())
            stock_items.append(stock_item)
        
        return stock_items
    
    def get_by_id(self, stock_id):
        """Obtiene un elemento de stock por su ID"""
        doc = self.db.collection(self.collection).document(stock_id).get()
        if doc.exists:
            return Stock.from_dict(doc.id, doc.to_dict())
        return None
    
    def create(self, stock):
        """Crea un nuevo elemento de stock"""
        if not stock.product_name:
            return {"success": False, "error": "El nombre del producto es obligatorio"}
        
        if not stock.quantity or not isinstance(stock.quantity, (int, float)) or stock.quantity <= 0:
            return {"success": False, "error": "La cantidad debe ser un número mayor que cero"}
        
        if not stock.unit:
            return {"success": False, "error": "La unidad de medida es obligatoria"}
        
        if not stock.warehouse_id and stock.status == "received":
            return {"success": False, "error": "Se requiere un almacén para productos recibidos"}
        
        try:
            # Si tiene warehouse_id, verificar que exista
            if stock.warehouse_id:
                warehouse_doc = self.db.collection('warehouses').document(stock.warehouse_id).get()
                if not warehouse_doc.exists:
                    return {"success": False, "error": "El almacén especificado no existe"}
            
            # Crear el documento en Firestore
            doc_ref = self.db.collection(self.collection).document()
            stock.id = doc_ref.id
            doc_ref.set(stock.to_dict())
            
            # Registrar en log de auditoría
            self._log_action("create", stock.id, stock.to_dict())
            
            return {"success": True, "id": stock.id}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update(self, stock_id, data):
        """Actualiza un elemento de stock existente"""
        try:
            doc_ref = self.db.collection(self.collection).document(stock_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return {"success": False, "error": "Elemento de stock no encontrado"}
            
            # Verificar datos
            if "quantity" in data and (not isinstance(data["quantity"], (int, float)) or data["quantity"] <= 0):
                return {"success": False, "error": "La cantidad debe ser un número mayor que cero"}
            
            # Si cambia de estado a recibido, verificar que tenga almacén
            if "status" in data and data["status"] == "received":
                stock_data = doc.to_dict()
                warehouse_id = data.get("warehouse_id") or stock_data.get("warehouse_id")
                if not warehouse_id:
                    return {"success": False, "error": "Se requiere un almacén para productos recibidos"}
                
                # Verificar que el almacén exista
                warehouse_doc = self.db.collection('warehouses').document(warehouse_id).get()
                if not warehouse_doc.exists:
                    return {"success": False, "error": "El almacén especificado no existe"}
            
            # Actualizar solo los campos proporcionados
            update_data = {}
            fields = ["product_name", "quantity", "unit", "warehouse_id", "status", 
                      "category", "purchase_date", "expiry_date"]
            
            for field in fields:
                if field in data:
                    update_data[field] = data[field]
            
            update_data["updated_at"] = datetime.datetime.now()
            
            # Actualizar en Firestore
            doc_ref.update(update_data)
            
            # Registrar en log de auditoría
            self._log_action("update", stock_id, update_data)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete(self, stock_id):
        """Elimina un elemento de stock"""
        try:
            doc_ref = self.db.collection(self.collection).document(stock_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return {"success": False, "error": "Elemento de stock no encontrado"}
            
            # Guardar datos para log antes de eliminar
            old_data = doc.to_dict()
            
            # Eliminar documento
            doc_ref.delete()
            
            # Registrar en log de auditoría
            self._log_action("delete", stock_id, old_data)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def transfer(self, stock_id, target_warehouse_id, quantity=None):
        """Transfiere stock de un almacén a otro"""
        try:
            # Verificar que el stock exista
            stock_item = self.get_by_id(stock_id)
            if not stock_item:
                return {"success": False, "error": "Elemento de stock no encontrado"}
            
            # Verificar que el stock esté recibido
            if stock_item.status != "received":
                return {"success": False, "error": "Solo se pueden transferir productos recibidos"}
            
            # Verificar que tenga almacén origen
            if not stock_item.warehouse_id:
                return {"success": False, "error": "El producto no está asignado a ningún almacén"}
            
            # Verificar que el almacén destino exista
            target_warehouse = self.db.collection('warehouses').document(target_warehouse_id).get()
            if not target_warehouse.exists:
                return {"success": False, "error": "El almacén de destino no existe"}
            
            # Si no se especifica cantidad, transferir todo
            transfer_quantity = quantity if quantity is not None else stock_item.quantity
            
            # Verificar que la cantidad a transferir sea válida
            if not isinstance(transfer_quantity, (int, float)) or transfer_quantity <= 0:
                return {"success": False, "error": "La cantidad debe ser un número mayor que cero"}
            
            if transfer_quantity > stock_item.quantity:
                return {"success": False, "error": "No hay suficiente stock para transferir"}
            
            # Si se transfiere todo, actualizar el almacén
            if transfer_quantity == stock_item.quantity:
                return self.update(stock_id, {"warehouse_id": target_warehouse_id})
            
            # Si se transfiere parte, crear nuevo stock y reducir el original
            # 1. Reducir cantidad del original
            original_update = self.update(stock_id, {"quantity": stock_item.quantity - transfer_quantity})
            if not original_update["success"]:
                return original_update
            
            # 2. Crear nuevo stock en el almacén destino
            new_stock = Stock(
                product_name=stock_item.product_name,
                quantity=transfer_quantity,
                unit=stock_item.unit,
                warehouse_id=target_warehouse_id,
                status="received",
                category=stock_item.category,
                purchase_date=stock_item.purchase_date,
                expiry_date=stock_item.expiry_date
            )
            
            create_result = self.create(new_stock)
            
            # Registrar la transferencia en el log
            transfer_data = {
                "from_warehouse": stock_item.warehouse_id,
                "to_warehouse": target_warehouse_id,
                "quantity": transfer_quantity,
                "original_stock_id": stock_id,
                "new_stock_id": create_result.get("id") if create_result["success"] else None
            }
            self._log_action("transfer", stock_id, transfer_data)
            
            return create_result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_stock_summary(self, groupby="warehouse"):
        """
        Obtiene un resumen del stock.
        groupby puede ser "warehouse", "product", "category"
        """
        try:
            # Obtener todo el stock recibido
            stock_items = self.get_all(status="received")
            
            if not stock_items:
                return {"success": True, "data": {}}
            
            summary = {}
            
            if groupby == "warehouse":
                # Agrupar por almacén
                for item in stock_items:
                    warehouse_id = item.warehouse_id or "sin_almacen"
                    if warehouse_id not in summary:
                        summary[warehouse_id] = {
                            "total_items": 0,
                            "products": {}
                        }
                    
                    # Incrementar contador de items
                    summary[warehouse_id]["total_items"] += 1
                    
                    # Agregar producto
                    if item.product_name not in summary[warehouse_id]["products"]:
                        summary[warehouse_id]["products"][item.product_name] = {
                            "quantity": 0,
                            "unit": item.unit
                        }
                    
                    # Sumar cantidad
                    summary[warehouse_id]["products"][item.product_name]["quantity"] += item.quantity
            
            elif groupby == "product":
                # Agrupar por producto
                for item in stock_items:
                    if item.product_name not in summary:
                        summary[item.product_name] = {
                            "total_quantity": 0,
                            "unit": item.unit,
                            "warehouses": {}
                        }
                    
                    # Incrementar cantidad total
                    summary[item.product_name]["total_quantity"] += item.quantity
                    
                    # Agregar almacén
                    warehouse_id = item.warehouse_id or "sin_almacen"
                    if warehouse_id not in summary[item.product_name]["warehouses"]:
                        summary[item.product_name]["warehouses"][warehouse_id] = 0
                    
                    # Sumar cantidad en el almacén
                    summary[item.product_name]["warehouses"][warehouse_id] += item.quantity
            
            elif groupby == "category":
                # Agrupar por categoría
                for item in stock_items:
                    category = item.category or "sin_categoria"
                    if category not in summary:
                        summary[category] = {
                            "total_items": 0,
                            "products": {}
                        }
                    
                    # Incrementar contador de items
                    summary[category]["total_items"] += 1
                    
                    # Agregar producto
                    if item.product_name not in summary[category]["products"]:
                        summary[category]["products"][item.product_name] = {
                            "quantity": 0,
                            "unit": item.unit
                        }
                    
                    # Sumar cantidad
                    summary[category]["products"][item.product_name]["quantity"] += item.quantity
            
            return {"success": True, "data": summary}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _log_action(self, action, stock_id, data):
        """Registra acciones en el log de auditoría"""
        try:
            log_data = {
                "collection": self.collection,
                "document_id": stock_id,
                "action": action,
                "data": data,
                "timestamp": datetime.datetime.now(),
                "user_id": "current_user_id"  # Esto debe ser reemplazado con el ID del usuario actual
            }
            
            self.db.collection('audit_logs').add(log_data)
        except Exception as e:
            print(f"Error al registrar en log de auditoría: {str(e)}")