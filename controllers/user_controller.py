# controllers/user_controller.py
from config.firebase_config import get_firestore_db
import datetime
import hashlib
import uuid

class UserController:
    def __init__(self, auth_controller):
        self.db = get_firestore_db()
        self.auth_controller = auth_controller
        self.collection = 'users'
    
    def get_all(self, include_admins=False):
        """
        Obtiene todos los usuarios.
        Si include_admins es False, solo retorna usuarios que no son admin.
        Solo los administradores pueden ver a otros administradores.
        """
        current_user = self.auth_controller.get_current_user()
        is_admin = current_user and current_user.get('role') == 'admin'
        
        users = []
        docs = self.db.collection(self.collection).stream()
        
        for doc in docs:
            user_data = doc.to_dict()
            
            # Si no es admin y el usuario es admin, saltamos
            if not is_admin and user_data.get('role') == 'admin':
                continue
                
            # Si no queremos incluir admins y el usuario es admin, saltamos
            if not include_admins and user_data.get('role') == 'admin':
                continue
                
            user = {
                "id": doc.id,
                "username": user_data.get("username"),
                "role": user_data.get("role"),
                "permissions": user_data.get("permissions", []),
                "created_at": user_data.get("created_at"),
                "created_by": user_data.get("created_by"),
                "last_login": user_data.get("last_login")
            }
            users.append(user)
        
        return users
    
    def get_by_id(self, user_id):
        """Obtiene un usuario por su ID"""
        if not user_id:
            return {
                "id": "",
                "username": "",
                "role": "",
                "permissions": [],
                "created_at": None,
                "created_by": "",
                "last_login": None
            }
        
        current_user = self.auth_controller.get_current_user()
        is_admin = current_user and current_user.get('role') == 'admin'
    
        doc = self.db.collection(self.collection).document(user_id).get()
        if not doc.exists:
            return {
                "id": "",
                "username": "",
                "role": "",
                "permissions": [],
                "created_at": None,
                "created_by": "",
                "last_login": None
            }
        
        user_data = doc.to_dict()
        
        # Si no es admin y el usuario solicitado es admin, no permitir
        if not is_admin and user_data.get('role') == 'admin':
            return {
                "id": "",
                "username": "",
                "role": "",
                "permissions": [],
                "created_at": None,
                "created_by": "",
                "last_login": None
            }
        
        return {
            "id": doc.id,
            "username": user_data.get("username", ""),
            "role": user_data.get("role", ""),
            "permissions": user_data.get("permissions", []),
            "created_at": user_data.get("created_at"),
            "created_by": user_data.get("created_by", ""),
            "last_login": user_data.get("last_login")
        }
    
    def create(self, username, password, role="basic", permissions=None):
        """Crea un nuevo usuario"""
        # Verificar permiso
        if not self.auth_controller.has_permission("create_user"):
            return {"success": False, "error": "No tienes permiso para crear usuarios"}
        
        # Verificar que tenga al menos un permiso
        if not permissions or len(permissions) == 0:
            return {"success": False, "error": "El usuario debe tener como mínimo un permiso"}
        
        # Verificar si el nombre de usuario ya existe
        existing_query = self.db.collection(self.collection).where("username", "==", username).limit(1).stream()
        if any(existing_query):
            return {"success": False, "error": "El nombre de usuario ya existe"}
        
        # Solo administradores pueden crear administradores
        current_user = self.auth_controller.get_current_user()
        is_admin = current_user and current_user.get('role') == 'admin'
        
        if role == "admin" and not is_admin:
            return {"success": False, "error": "Solo administradores pueden crear otros administradores"}
        
        try:
            # Crear hash de la contraseña
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # ID único para el nuevo usuario
            user_id = str(uuid.uuid4())
            
            # Datos del usuario
            user_data = {
                "username": username,
                "password_hash": password_hash,
                "role": role,
                "permissions": permissions or [],
                "created_at": datetime.datetime.now(),
                "created_by": current_user.get('id') if current_user else "system",
                "last_login": None
            }
            
            # Guardar en la base de datos
            self.db.collection(self.collection).document(user_id).set(user_data)
            
            return {
                "success": True,
                "user_id": user_id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update(self, user_id, data):
        """Actualiza un usuario existente"""
        # Verificar permiso
        if not self.auth_controller.has_permission("manage_users"):
            return {"success": False, "error": "No tienes permiso para gestionar usuarios"}
        
        # Verificar que tenga al menos un permiso
        if "permissions" in data and (not data["permissions"] or len(data["permissions"]) == 0):
            return {"success": False, "error": "El usuario debe tener como mínimo un permiso"}
        
        current_user = self.auth_controller.get_current_user()
        is_admin = current_user and current_user.get('role') == 'admin'
        
        try:
            user_ref = self.db.collection(self.collection).document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"success": False, "error": "Usuario no encontrado"}
            
            user_data = user_doc.to_dict()
            
            # Si no es admin y el usuario es admin, no permitir
            if not is_admin and user_data.get("role") == "admin":
                return {"success": False, "error": "No tienes permiso para modificar administradores"}
            
            # Si quiere cambiar a admin y no es admin, no permitir
            if "role" in data and data["role"] == "admin" and not is_admin:
                return {"success": False, "error": "Solo administradores pueden crear otros administradores"}
            
            # Preparar datos a actualizar
            update_data = {}
            if "username" in data and data["username"]:
                # Verificar si el nombre de usuario ya existe
                if data["username"] != user_data.get("username"):
                    existing_query = self.db.collection(self.collection).where("username", "==", data["username"]).limit(1).stream()
                    if any(existing_query):
                        return {"success": False, "error": "El nombre de usuario ya existe"}
                update_data["username"] = data["username"]
            
            if "role" in data:
                update_data["role"] = data["role"]
            
            if "permissions" in data:
                update_data["permissions"] = data["permissions"]
            
            update_data["updated_at"] = datetime.datetime.now()
            
            # Actualizar en la base de datos
            user_ref.update(update_data)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def change_password(self, user_id, new_password):
        """Cambia la contraseña de un usuario (función administrativa)"""
        # Verificar permiso
        if not self.auth_controller.has_permission("manage_users"):
            return {"success": False, "error": "No tienes permiso para gestionar usuarios"}
        
        current_user = self.auth_controller.get_current_user()
        is_admin = current_user and current_user.get('role') == 'admin'
        
        try:
            user_ref = self.db.collection(self.collection).document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"success": False, "error": "Usuario no encontrado"}
            
            user_data = user_doc.to_dict()
            
            # Si no es admin y el usuario es admin, no permitir
            if not is_admin and user_data.get("role") == "admin":
                return {"success": False, "error": "No tienes permiso para modificar administradores"}
            
            # Crear hash de la contraseña
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            
            # Actualizar en la base de datos
            user_ref.update({
                "password_hash": password_hash,
                "updated_at": datetime.datetime.now()
            })
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete(self, user_id):
        """Elimina un usuario"""
        # Verificar permiso
        if not self.auth_controller.has_permission("manage_users"):
            return {"success": False, "error": "No tienes permiso para gestionar usuarios"}
        
        current_user = self.auth_controller.get_current_user()
        is_admin = current_user and current_user.get('role') == 'admin'
        current_user_id = current_user.get('id')
        
        try:
            # No permitir eliminarse a sí mismo
            if user_id == current_user_id:
                return {"success": False, "error": "No puedes eliminar tu propio usuario"}
            
            user_ref = self.db.collection(self.collection).document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"success": False, "error": "Usuario no encontrado"}
            
            user_data = user_doc.to_dict()
            
            # Si no es admin y el usuario es admin, no permitir
            if not is_admin and user_data.get("role") == "admin":
                return {"success": False, "error": "No tienes permiso para eliminar administradores"}
            
            # Eliminar usuario
            user_ref.delete()
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}