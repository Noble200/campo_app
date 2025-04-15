# config/app_config.py
import customtkinter as ctk

def set_appearance_mode(mode):
    """
    Configura el modo de apariencia de la aplicación.
    
    Args:
        mode (str): "System", "Dark" o "Light"
    """
    ctk.set_appearance_mode(mode)

def set_default_color_theme(theme):
    """
    Configura el tema de color predeterminado.
    
    Args:
        theme (str): Nombre del tema, por ejemplo "blue"
    """
    ctk.set_default_color_theme(theme)