# config/firebase_config.py
import os
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Firebase Admin SDK (para Firestore)
def initialize_firebase_admin():
    try:
        # Verificar si ya está inicializado
        firebase_admin.get_app()
    except ValueError:
        # Si no está inicializado, inicializar con credenciales
        cred = credentials.Certificate({
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
        })
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

# Configuración de Pyrebase (para autenticación)
def get_pyrebase_config():
    config = {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID")
    }
    return config

# Inicializar Pyrebase
def initialize_pyrebase():
    config = get_pyrebase_config()
    return pyrebase.initialize_app(config)

# Obtener instancia de Firestore
def get_firestore_db():
    return initialize_firebase_admin()

# Obtener instancia de autenticación de Firebase
def get_auth():
    firebase = initialize_pyrebase()
    return firebase.auth()