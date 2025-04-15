# views/dashboard_frame.py
import customtkinter as ctk
from datetime import datetime

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, auth_controller, on_logout):
        super().__init__(master)
        self.master = master
        self.auth_controller = auth_controller
        self.on_logout = on_logout
        
        # Crear layout de la aplicación
        self.create_layout()
        
        # Mostrar panel principal por defecto
        
    
    def create_layout(self):
        # Configurar grid
        self.grid_columnconfigure(1, weight=1)  # Columna de contenido
        self.grid_rowconfigure(0, weight=0)  # Fila de cabecera
        self.grid_rowconfigure(1, weight=1)  # Fila de contenido
        
        # Barra superior
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#EEEEEE", "#333333"))
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # Configurar grid del header
        self.header_frame.grid_columnconfigure(0, weight=0)  # Logo
        self.header_frame.grid_columnconfigure(1, weight=1)  # Título
        self.header_frame.grid_columnconfigure(2, weight=0)  # Usuario
        
        # Título de la aplicación
        self.app_title = ctk.CTkLabel(
            self.header_frame, 
            text="Sistema de Gestión Agrícola", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.app_title.grid(row=0, column=1, padx=20, pady=10, sticky="w")
        
        # Información de usuario y botón de cierre de sesión
        self.user_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.user_frame.grid(row=0, column=2, padx=20, pady=10, sticky="e")
        
        # Obtener información del usuario actual
        user = self.auth_controller.get_current_user()
        if user:
            try:
                # Obtener el ID del usuario, con fallback
                user_id = user.get('id')
                
                # Si no hay ID del usuario, usamos un valor por defecto
                if not user_id:
                    self.user_name_label = ctk.CTkLabel(
                        self.user_frame, 
                        text="Usuario",
                        font=ctk.CTkFont(size=14)
                    )
                    self.user_name_label.pack(side="left", padx=(0, 10))
                else:
                    # Obtener datos del usuario
                    user_doc = self.auth_controller.db.collection('users').document(user_id).get()
                    
                    if user_doc.exists:
                        user_data = user_doc.to_dict()
                        user_name = user_data.get('username', 'Usuario')
                        user_role = user_data.get('role', 'básico')
                        
                        self.user_name_label = ctk.CTkLabel(
                            self.user_frame, 
                            text=f"{user_name} ({user_role})",
                            font=ctk.CTkFont(size=14)
                        )
                        self.user_name_label.pack(side="left", padx=(0, 10))
                    else:
                        # Si no existe el documento
                        self.user_name_label = ctk.CTkLabel(
                            self.user_frame, 
                            text="Usuario",
                            font=ctk.CTkFont(size=14)
                        )
                        self.user_name_label.pack(side="left", padx=(0, 10))
            except Exception as e:
                print(f"Error al obtener datos del usuario: {str(e)}")
                # Fallback en caso de error
                self.user_name_label = ctk.CTkLabel(
                    self.user_frame, 
                    text="Usuario",
                    font=ctk.CTkFont(size=14)
                )
                self.user_name_label.pack(side="left", padx=(0, 10))
        else:
            # Si no hay usuario, mostrar etiqueta genérica
            self.user_name_label = ctk.CTkLabel(
                self.user_frame, 
                text="Usuario no identificado",
                font=ctk.CTkFont(size=14)
            )
            self.user_name_label.pack(side="left", padx=(0, 10))
        
        # Botón de cerrar sesión
        self.logout_button = ctk.CTkButton(
            self.user_frame, 
            text="Cerrar Sesión",
            width=120,
            height=30,
            command=self.on_logout
        )
        self.logout_button.pack(side="left")
        
        # Barra lateral
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsw")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)  # Espacio flexible al final
        
        # Fecha actual
        current_date = datetime.now().strftime("%d/%m/%Y")
        self.date_label = ctk.CTkLabel(
            self.sidebar_frame,
            text=f"Fecha: {current_date}",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.date_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Opciones del menú
        self.menu_options = [
            {"text": "Panel Principal", "command": self.show_main_dashboard},
            {"text": "Campos", "command": self.show_fields},
            {"text": "Almacenes", "command": self.show_warehouses},
            {"text": "Inventario", "command": self.show_stock},
            {"text": "Fumigación", "command": self.show_fumigation},
            {"text": "Reportes", "command": self.show_reports},
            {"text": "Usuarios", "command": self.show_users},
            {"text": "Estadísticas", "command": self.show_statistics},
        ]
        
        # Crear botones del menú
        self.menu_buttons = []
        for i, option in enumerate(self.menu_options):
            button = ctk.CTkButton(
                self.sidebar_frame,
                text=option["text"],
                fg_color="transparent",
                text_color=("gray10", "#DCE4EE"),
                anchor="w",
                command=option["command"],
                height=40
            )
            button.grid(row=i+1, column=0, padx=10, pady=5, sticky="ew")
            self.menu_buttons.append(button)
        
        # Contenedor principal para el contenido
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
    
    def show_main_dashboard(self):
        try:
            # Limpiar contenido actual
            for widget in self.content_frame.winfo_children():
                widget.destroy()

            # Verificar si el usuario es fumigador
            current_user = self.auth_controller.get_current_user()
            if current_user and current_user.get('role') == 'fumigator':
                self.show_fumigator_dashboard()
                return

        
            # Configurar grid del contenido
            self.content_frame.grid_columnconfigure((0, 1, 2), weight=1)
        except Exception as e:
            print(f"Error en show_main_dashboard: {str(e)}")
    
    def show_fumigator_dashboard(self):
        try:
            # Limpiar contenido actual
            for widget in self.content_frame.winfo_children():
                widget.destroy()

            # Crear y mostrar la vista de fumigador
            from views.fumigator_view import FumigatorDashboardView
            fumigator_frame = FumigatorDashboardView(self.content_frame, self.auth_controller)
            fumigator_frame.pack(fill="both", expand=True)
        except Exception as e:
            print(f"Error al mostrar panel de fumigador: {str(e)}")
            error_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Error al cargar el panel de fumigador: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=50)
            self.content_frame.grid_rowconfigure(0, weight=0)
            self.content_frame.grid_rowconfigure(1, weight=0)
            self.content_frame.grid_rowconfigure(2, weight=1)
            
            # Título
            title_label = ctk.CTkLabel(
                self.content_frame,
                text="Panel Principal",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=20, sticky="w")
            
            # Tarjetas de resumen
            self.create_summary_card(0, 0, "Campos Registrados", "0", "green")
            self.create_summary_card(0, 1, "Almacenes", "0", "blue")
            self.create_summary_card(0, 2, "Productos en Stock", "0", "purple")
            
            # Gráfico o informe reciente
            chart_frame = ctk.CTkFrame(self.content_frame)
            chart_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
            
            chart_title = ctk.CTkLabel(
                chart_frame,
                text="Actividad Reciente",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            chart_title.pack(anchor="w", padx=15, pady=15)
            
            # Placeholder para gráfico (a implementar con matplotlib)
            chart_placeholder = ctk.CTkLabel(
                chart_frame,
                text="Aquí irá un gráfico de actividad",
                font=ctk.CTkFont(size=14)
            )
            chart_placeholder.pack(expand=True)
            
            # Panel de alertas o notificaciones
            alerts_frame = ctk.CTkFrame(self.content_frame)
            alerts_frame.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")
            
            alerts_title = ctk.CTkLabel(
                alerts_frame,
                text="Alertas",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            alerts_title.pack(anchor="w", padx=15, pady=15)
            
            # Ejemplo de alertas
            self.create_alert(alerts_frame, "Bienvenido al sistema", "low")
            self.create_alert(alerts_frame, "Configure sus campos y almacenes", "medium")
            self.create_alert(alerts_frame, "Para ayuda contacte al administrador", "high")
        except Exception as e:
            # Manejo de errores
            print(f"Error en show_main_dashboard: {str(e)}")
            error_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Error al cargar el panel principal: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=50)
    
    def create_summary_card(self, row, column, title, value, color):
        try:
            # Colores según el tema
            colors = {
                "green": ("#E5F5E5", "#1F5B1F"),
                "blue": ("#E5F0FF", "#1F3D7A"),
                "purple": ("#F0E5FF", "#5F1F7A"),
                "orange": ("#FFF2E5", "#7A4B1F")
            }
            
            # Crear tarjeta
            card = ctk.CTkFrame(self.content_frame)
            card.grid(row=row+1, column=column, padx=10, pady=10, sticky="nsew")
            
            # Título de la tarjeta
            card_title = ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=14)
            )
            card_title.pack(anchor="w", padx=15, pady=(15, 5))
            
            # Valor
            card_value = ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=28, weight="bold")
            )
            card_value.pack(anchor="w", padx=15, pady=(5, 15))
        except Exception as e:
            print(f"Error en create_summary_card: {str(e)}")
    
    def create_alert(self, parent, message, priority):
        try:
            # Colores según prioridad
            colors = {
                "high": "#FF5252",
                "medium": "#FFB74D",
                "low": "#4CAF50"
            }
            
            alert_frame = ctk.CTkFrame(parent)
            alert_frame.pack(fill="x", padx=15, pady=5)
            
            # Indicador de prioridad
            priority_indicator = ctk.CTkFrame(alert_frame, width=5, fg_color=colors[priority])
            priority_indicator.pack(side="left", fill="y")
            
            # Mensaje
            alert_message = ctk.CTkLabel(
                alert_frame,
                text=message,
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            alert_message.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        except Exception as e:
            print(f"Error en create_alert: {str(e)}")
    
    def show_fields(self):
        try:
            # Limpiar contenido actual
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            # Crear y mostrar la vista de campos
            from views.field_frames import FieldManagementFrame
            fields_frame = FieldManagementFrame(self.content_frame, self.auth_controller)
            fields_frame.pack(fill="both", expand=True)
        except Exception as e:
            print(f"Error al mostrar campos: {str(e)}")
            error_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Error al cargar la gestión de campos: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=50)
    
    def show_warehouses(self):
        try:
            # Limpiar contenido actual
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            # Crear y mostrar la vista de almacenes
            from views.warehouse_frames import WarehouseManagementFrame
            warehouses_frame = WarehouseManagementFrame(self.content_frame, self.auth_controller)
            warehouses_frame.pack(fill="both", expand=True)
        except Exception as e:
            print(f"Error al mostrar almacenes: {str(e)}")
            error_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Error al cargar la gestión de almacenes: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=50)
    
    def show_stock(self):
        try:
            # Limpiar contenido actual
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            # Verificar si tiene permiso para gestionar inventario
            if not self.auth_controller.has_permission("manage_stock"):
                self.show_placeholder("Gestión de Inventario")
                return
            
            # Crear y mostrar la vista de inventario
            from views.stock_frames import StockManagementFrame
            stock_frame = StockManagementFrame(self.content_frame, self.auth_controller)
            stock_frame.pack(fill="both", expand=True)
        except Exception as e:
            print(f"Error al mostrar inventario: {str(e)}")
            error_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Error al cargar la gestión de inventario: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=50)
        
    def show_fumigation(self):
        try:
            # Verificar si es fumigador
            current_user = self.auth_controller.get_current_user()
            if current_user and current_user.get('role') == 'fumigator':
                # Para fumigadores, mostrar el panel principal que ya tiene las fumigaciones
                self.show_main_dashboard()
                return
            
            # Para otros usuarios, mostrar la vista normal de fumigación
            # Limpiar contenido actual
            for widget in self.content_frame.winfo_children():
                widget.destroy()
        
            # Crear y mostrar la vista de fumigación
            from views.fumigation_frames import FumigationManagementFrame
            fumigation_frame = FumigationManagementFrame(self.content_frame, self.auth_controller)
            fumigation_frame.pack(fill="both", expand=True)
        except Exception as e:
            print(f"Error al mostrar fumigaciones: {str(e)}")
            error_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Error al cargar la gestión de fumigaciones: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=50)
        
    
    def show_reports(self):
        # Aquí irá la implementación de la vista de reportes
        self.show_placeholder("Generación de Reportes")
    
    def show_users(self):
        try:
            # Limpiar contenido actual
            for widget in self.content_frame.winfo_children():
                widget.destroy()
        
            # Verificar si tiene permiso para ver la gestión de usuarios
            has_user_permissions = (
                self.auth_controller.has_permission("manage_users") or 
                self.auth_controller.has_permission("create_user")
            )
        
            # También permitir acceso a roles específicos incluso sin permisos
            current_user = self.auth_controller.get_current_user() or {}
            is_admin = current_user.get('role') == 'admin'
            is_manager = current_user.get('role') == 'manager'
        
            if has_user_permissions or is_admin or is_manager:
                # Crear y mostrar la vista de usuarios
                from views.user_management_frames import UserManagementFrame
                users_frame = UserManagementFrame(self.content_frame, self.auth_controller)
                users_frame.pack(fill="both", expand=True)
            else:
                # Mostrar mensaje si no tiene permiso
                self.show_placeholder("Gestión de Usuarios - Acceso Restringido")
        except Exception as e:
            print(f"Error al mostrar usuarios: {str(e)}")
            error_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Error al cargar la gestión de usuarios: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=50)
    
    def show_statistics(self):
        # Aquí irá la implementación de la vista de estadísticas
        self.show_placeholder("Estadísticas y Análisis")
    
    def show_placeholder(self, title):
        try:
            # Limpiar contenido actual
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            # Mostrar título
            title_label = ctk.CTkLabel(
                self.content_frame,
                text=title,
                font=ctk.CTkFont(size=20, weight="bold")
            )
            title_label.pack(padx=20, pady=20, anchor="w")
            
            # Mostrar mensaje de próximamente
            message = ctk.CTkLabel(
                self.content_frame,
                text="Esta sección está en desarrollo.",
                font=ctk.CTkFont(size=16)
            )
            message.pack(expand=True)
        except Exception as e:
            print(f"Error en show_placeholder: {str(e)}")
            error_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Error al mostrar contenido: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=50)
