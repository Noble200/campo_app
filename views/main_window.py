# views/main_window.py
import customtkinter as ctk
from views.auth.login_frame import LoginFrame
from views.dashboard_frame import DashboardFrame

class MainWindow(ctk.CTkFrame):
    def __init__(self, master, auth_controller):
        super().__init__(master)
        self.master = master
        self.auth_controller = auth_controller
        
        # Contenedor principal
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True)
        
        # Estado inicial - mostrar login si no está autenticado
        if self.auth_controller.is_authenticated():
            self.show_dashboard()
        else:
            self.show_login()
    
    def show_login(self):
        # Limpiar contenido actual
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Mostrar pantalla de login
        login_frame = LoginFrame(self.content_frame, self.auth_controller, self.on_login_success)
        login_frame.pack(fill="both", expand=True)
    
    def show_dashboard(self):
        # Limpiar contenido actual
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
        # Mostrar dashboard
        try:
            # Verificar si el usuario es fumigador
            current_user = self.auth_controller.get_current_user() or {}
            is_fumigator = current_user.get('role') == 'fumigator'
            
            if is_fumigator:
                # Mostrar solo la vista de fumigador sin el dashboard completo
                from views.fumigator_view import FumigatorDashboardView
                fumigator_view = FumigatorDashboardView(self.content_frame, self.auth_controller)
                fumigator_view.pack(fill="both", expand=True)
            else:
                # Para otros usuarios, mostrar el dashboard normal
                dashboard = DashboardFrame(self.content_frame, self.auth_controller, self.on_logout)
                dashboard.pack(fill="both", expand=True)
        except Exception as e:
            # Mostrar mensaje de error en la interfaz
            error_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Error al cargar panel: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=50)
    
    def on_login_success(self):
        self.show_dashboard()
    
    def on_logout(self):
        self.auth_controller.logout()
        self.show_login()
