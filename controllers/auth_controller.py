# controllers/auth_controller.py
from config.firebase_config import get_firestore_db
import datetime
import hashlib
import uuid

class AuthController:
    def __init__(self):
        self.db = get_firestore_db()
        self.current_user = None
        
        # Crear usuario administrador si no existe
        self._ensure_admin_exists()
    
    def _ensure_admin_exists(self):
        """Asegura que exista un usuario administrador en el sistema"""
        admin_query = self.db.collection('users').where("role", "==", "admin").limit(1).stream()
        
        if not any(admin_query):
            # Crear usuario administrador
            admin_id = str(uuid.uuid4())
            admin_pass = "admin123"  # Contraseña inicial que debería cambiarse
            
            # Crear hash de la contraseña
            password_hash = self._hash_password(admin_pass)
            
            # Guardar en la base de datos
            self.db.collection('users').document(admin_id).set({
                "username": "admin",
                "password_hash": password_hash,
                "role": "admin",
                "permissions": ["*"],  # Todos los permisos
                "created_at": datetime.datetime.now(),
                "created_by": "system"
            })
            
            print("Usuario administrador creado. Username: admin, Password: admin123")
    
    def _hash_password(self, password):
        """Crea un hash de la contraseña usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username, password):
        try:
            # Buscar usuario por nombre de usuario
            users_ref = self.db.collection('users')
            query = users_ref.where("username", "==", username).limit(1).stream()
            
            user_docs = list(query)
            if not user_docs:
                return {"success": False, "error": "Usuario no encontrado"}
            
            user_doc = user_docs[0]
            user_data = user_doc.to_dict()
            
            # Verificar contraseña
            password_hash = self._hash_password(password)
            if password_hash != user_data.get("password_hash"):
                return {"success": False, "error": "Contraseña incorrecta"}
            
            # Actualizar último login
            user_ref = users_ref.document(user_doc.id)
            user_ref.update({"last_login": datetime.datetime.now()})
            
            # Establecer usuario actual
            self.current_user = {
                "localId": user_doc.id,
                "id": user_doc.id,
                "username": user_data.get("username"),
                "role": user_data.get("role"),
                "permissions": user_data.get("permissions", [])
            }
            
            return {
                "success": True,
                "user_data": user_data,
                "user_id": user_doc.id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def register(self, username, password, role="basic", permissions=None, created_by=None):
        try:
            # Verificar si el usuario actual tiene permiso para crear usuarios
            if created_by is not None and not self.has_permission("create_user"):
                return {"success": False, "error": "No tienes permiso para crear usuarios"}
            
            # Verificar si el nombre de usuario ya existe
            existing_query = self.db.collection('users').where("username", "==", username).limit(1).stream()
            if any(existing_query):
                return {"success": False, "error": "El nombre de usuario ya existe"}
            
            # Crear hash de la contraseña
            password_hash = self._hash_password(password)
            
            # ID único para el nuevo usuario
            user_id = str(uuid.uuid4())
            
            # Datos del usuario
            user_data = {
                "username": username,
                "password_hash": password_hash,
                "role": role,
                "permissions": permissions or [],
                "created_at": datetime.datetime.now(),
                "created_by": created_by or "system",
                "last_login": None
            }
            
            # Guardar en la base de datos
            self.db.collection('users').document(user_id).set(user_data)
            
            return {
                "success": True,
                "user_id": user_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def logout(self):
        self.current_user = None
        return {"success": True}
    
    def get_current_user(self):
        if not self.current_user:
            return None
      
        # Crear una copia para no modificar el original
        user_data = dict(self.current_user)

        # Asegurar que tiene todas las propiedades necesarias
        if "localId" not in user_data:
            user_data["localId"] = user_data.get("id", "")
    
        if "id" not in user_data:
            user_data["id"] = user_data.get("localId", "")
    
        if "username" not in user_data:
            user_data["username"] = ""
    
        if "role" not in user_data:
            user_data["role"] = "basic"
    
        if "permissions" not in user_data:
            user_data["permissions"] = []
    
        return user_data
    
    def is_authenticated(self):
        return self.current_user is not None
    
    def has_permission(self, permission):
        if not self.is_authenticated():
            return False
        
        # Si el usuario es administrador o tiene el permiso "*", tiene todos los permisos
        if self.current_user["role"] == "admin" or "*" in self.current_user["permissions"]:
            return True
        
        # Verificar si el usuario tiene el permiso específico
        return permission in self.current_user["permissions"]
    
    def grant_permission(self, user_id, permission):
        """Otorga un permiso específico a un usuario"""
        if not self.has_permission("manage_permissions"):
            return {"success": False, "error": "No tienes permiso para gestionar permisos"}
        
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"success": False, "error": "Usuario no encontrado"}
            
            user_data = user_doc.to_dict()
            permissions = user_data.get("permissions", [])
            
            if permission not in permissions:
                permissions.append(permission)
                user_ref.update({"permissions": permissions})
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def revoke_permission(self, user_id, permission):
        """Revoca un permiso específico de un usuario"""
        if not self.has_permission("manage_permissions"):
            return {"success": False, "error": "No tienes permiso para gestionar permisos"}
        
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"success": False, "error": "Usuario no encontrado"}
            
            user_data = user_doc.to_dict()
            permissions = user_data.get("permissions", [])
            
            if permission in permissions:
                permissions.remove(permission)
                user_ref.update({"permissions": permissions})
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def change_password(self, user_id, current_password, new_password):
        """Cambia la contraseña de un usuario"""
        try:
            # Verificar si es el usuario actual o si tiene permiso para cambiar contraseñas
            if self.current_user["id"] != user_id and not self.has_permission("manage_users"):
                return {"success": False, "error": "No tienes permiso para cambiar esta contraseña"}
            
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"success": False, "error": "Usuario no encontrado"}
            
            user_data = user_doc.to_dict()
            
            # Si es el usuario actual, verificar contraseña actual
            if self.current_user["id"] == user_id:
                current_hash = self._hash_password(current_password)
                if current_hash != user_data.get("password_hash"):
                    return {"success": False, "error": "Contraseña actual incorrecta"}
            
            # Actualizar contraseña
            new_hash = self._hash_password(new_password)
            user_ref.update({"password_hash": new_hash})
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}