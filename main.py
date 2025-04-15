# main.py
import os
import customtkinter as ctk
from views.main_window import MainWindow
from config.app_config import set_appearance_mode, set_default_color_theme
from controllers.auth_controller import AuthController

def main():
    # Configurar apariencia de la aplicación
    set_appearance_mode("System")  # "System", "Dark" o "Light"
    set_default_color_theme("blue")  # Tema de color predeterminado
    
    # Inicializar la aplicación
    app = ctk.CTk()
    app.title("Sistema de Gestión Agrícola")
    app.geometry("1200x700")
    
    # Inicializar controlador de autenticación
    auth_controller = AuthController()
    
    # Inicializar ventana principal
    main_window = MainWindow(app, auth_controller)
    main_window.pack(fill="both", expand=True)
    
    # Iniciar bucle principal
    app.mainloop()

if __name__ == "__main__":
    main()