# models/user.py
import datetime

class User:
    def __init__(self, id=None, username=None, password_hash=None, role=None, permissions=None, created_by=None):
        self.id = id  # ID en Firebase
        self.username = username  # ID de usuario para login
        self.password_hash = password_hash  # Almacenaremos el hash, no la contraseña
        self.role = role or "basic"  # "admin", "manager", "basic", etc.
        self.permissions = permissions or []  # Lista de permisos específicos
        self.created_by = created_by  # Usuario que creó esta cuenta
        self.created_at = datetime.datetime.now()
        self.last_login = None
    
    def to_dict(self):
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "role": self.role,
            "permissions": self.permissions,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "last_login": self.last_login
        }
    
    @staticmethod
    def from_dict(id, data):
        user = User(
            id=id,
            username=data.get("username"),
            password_hash=data.get("password_hash"),
            role=data.get("role"),
            permissions=data.get("permissions", []),
            created_by=data.get("created_by")
        )
        user.created_at = data.get("created_at")
        user.last_login = data.get("last_login")
        return user