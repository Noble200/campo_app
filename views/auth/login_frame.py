# views/auth/login_frame.py
import customtkinter as ctk
from PIL import Image, ImageTk
import os

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, auth_controller, on_login_success):
        super().__init__(master)
        self.master = master
        self.auth_controller = auth_controller
        self.on_login_success = on_login_success
        
        # Configurar grid para centrar contenido
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Frame central para login
        self.login_container = ctk.CTkFrame(self, corner_radius=10)
        self.login_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Configurar grid del contenedor
        self.login_container.grid_columnconfigure(0, weight=1)
        self.login_container.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=0)
        self.login_container.grid_rowconfigure(6, weight=1)
        
        # Logo o título
        self.title_label = ctk.CTkLabel(
            self.login_container, 
            text="Sistema de Gestión Agrícola", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(40, 20))
        
        # Campos de formulario
        self.username_entry = ctk.CTkEntry(self.login_container, placeholder_text="Nombre de usuario", width=300)
        self.username_entry.grid(row=1, column=0, padx=30, pady=(15, 5))
        
        self.password_entry = ctk.CTkEntry(self.login_container, placeholder_text="Contraseña", show="*", width=300)
        self.password_entry.grid(row=2, column=0, padx=30, pady=(15, 5))
        
        # Mensaje de error
        self.error_label = ctk.CTkLabel(self.login_container, text="", text_color="red")
        self.error_label.grid(row=3, column=0, padx=30, pady=(5, 5))
        
        # Botón de inicio de sesión
        self.login_button = ctk.CTkButton(
            self.login_container, 
            text="Iniciar Sesión", 
            command=self.handle_login,
            width=300
        )
        self.login_button.grid(row=4, column=0, padx=30, pady=(15, 5))
        
        # Mensaje informativo
        self.info_label = ctk.CTkLabel(
            self.login_container,
            text="Si es primera vez, consulte con administrador",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.info_label.grid(row=5, column=0, padx=30, pady=(5, 20))
    
    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.error_label.configure(text="Por favor, complete todos los campos")
            return
        
        result = self.auth_controller.login(username, password)
        if result["success"]:
            self.error_label.configure(text="")
            self.on_login_success()
        else:
            self.error_label.configure(text=result.get("error", "Credenciales incorrectas"))