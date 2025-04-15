# views/fumigation_frames.py
import customtkinter as ctk
from datetime import datetime, timedelta
from controllers.fumigation_controller import FumigationController
from controllers.field_controller import FieldController
from controllers.user_controller import UserController
from controllers.stock_controller import StockController
from models.fumigation import Fumigation

class FumigationManagementFrame(ctk.CTkFrame):
    def __init__(self, master, auth_controller):
        super().__init__(master)
        self.master = master
        self.auth_controller = auth_controller
        self.fumigation_controller = FumigationController()
        self.field_controller = FieldController()
        self.user_controller = UserController(auth_controller)
        self.stock_controller = StockController()
        
        # Obtener información del usuario actual
        self.current_user = self.auth_controller.get_current_user() or {}
        self.is_admin = self.current_user and self.current_user.get('role') == 'admin'
        self.is_fumigator = self.current_user and self.current_user.get('role') == 'fumigator'

        # Lista de fumigaciones
        self.fumigations = []
        
        # Lista de estados disponibles
        self.status_options = ["scheduled", "in_progress", "completed", "cancelled"]
        self.status_labels = {
            "scheduled": "Programada",
            "in_progress": "En Progreso",
            "completed": "Completada",
            "cancelled": "Cancelada"
        }
        
        # Crear interfaz
        self.create_interface()
        
        # Cargar datos
        self.load_fumigations()
    
    def create_interface(self):
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Título
        self.grid_rowconfigure(1, weight=0)  # Botones y filtros
        self.grid_rowconfigure(2, weight=1)  # Tabla
        
        # Título
        if self.is_fumigator:
            title_text = "Mis Tareas de Fumigación"
        else:
            title_text = "Gestión de Fumigaciones"
        
        self.title_label = ctk.CTkLabel(
            self, 
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Frame para controles y filtros
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Botones de acción
        self.action_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.action_frame.pack(side="left", fill="y")
        
        # Botón para agregar fumigación
        if not self.is_fumigator:
            self.add_button = ctk.CTkButton(
                self.action_frame,
                text="+ Programar Fumigación",
                command=self.show_add_fumigation
            )
            self.add_button.pack(side="left", padx=(0, 10))
        
        # Botón para refrescar lista
        self.refresh_button = ctk.CTkButton(
            self.action_frame,
            text="↻ Refrescar",
            command=self.load_fumigations,
            fg_color="#4CAF50"
        )
        self.refresh_button.pack(side="left")
        
        # Frame para filtros
        self.filter_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.filter_frame.pack(side="right", fill="y")
        
        # Filtro por estado
        self.status_filter_var = ctk.StringVar(value="Todos los estados")
        status_options = ["Todos los estados"] + [self.status_labels[status] for status in self.status_options]
        self.status_filter = ctk.CTkOptionMenu(
            self.filter_frame,
            values=status_options,
            variable=self.status_filter_var,
            command=self.filter_fumigations
        )
        self.status_filter.pack(side="left", padx=(0, 10))
        
        # Filtro por aplicador (si es admin)
        if self.is_admin:
            self.applicator_filter_var = ctk.StringVar(value="Todos los aplicadores")
            
            # Obtener lista de usuarios (aplicadores posibles)
            users = self.user_controller.get_all()
            applicator_options = ["Todos los aplicadores"] + [user.get("username", "") for user in users]
            
            self.applicator_filter = ctk.CTkOptionMenu(
                self.filter_frame,
                values=applicator_options,
                variable=self.applicator_filter_var,
                command=self.filter_fumigations
            )
            self.applicator_filter.pack(side="left")
        
        # Frame para la tabla con scroll
        self.table_container = ctk.CTkFrame(self)
        self.table_container.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Configurar grid del contenedor
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(0, weight=1)
        
        # Crear scrollbar
        self.scrollable_frame = ctk.CTkScrollableFrame(self.table_container)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar grid del scrollable frame
        self.scrollable_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.scrollable_frame.grid_columnconfigure(6, weight=0)
        
        # Cabecera de la tabla
        headers = ["Campo", "Aplicador", "Fecha", "Notas", "Productos", "Estado", "Acciones"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.scrollable_frame,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                width=100
            )
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Separador
        separator = ctk.CTkFrame(self.scrollable_frame, height=1, fg_color="gray")
        separator.grid(row=1, column=0, columnspan=7, sticky="ew", padx=5)
    
    def load_fumigations(self):
        """Carga todas las fumigaciones"""
        # Limpiar tabla existente (excepto cabecera y separador)
        for widget in self.scrollable_frame.winfo_children():
            if widget.grid_info()["row"] > 1:  # Solo eliminar filas de datos
                widget.destroy()
        
        # Obtener fumigaciones
        if self.is_admin:
            self.fumigations = self.fumigation_controller.get_all()
        else:
            # Si no es admin, solo mostrar las fumigaciones asignadas a este usuario
            user_id = self.current_user.get('id')
            if user_id:
                self.fumigations = self.fumigation_controller.get_all(applicator_id=user_id)
            else:
                self.fumigations = []  # Si no hay ID de usuario, no mostrar fumigaciones
        
        if not self.fumigations:
            # Mostrar mensaje si no hay fumigaciones
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No hay fumigaciones registradas",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.grid(row=2, column=0, columnspan=7, padx=10, pady=20)
            return
        
        # Ordenar fumigaciones por fecha (más reciente primero)
        self.fumigations.sort(key=lambda x: x.date if x.date else datetime.now(), reverse=True)
        
        # Mostrar fumigaciones en la tabla
        self.display_fumigations(self.fumigations)
    
    def filter_fumigations(self, *args):
        """Filtra las fumigaciones según los criterios seleccionados"""
        # Limpiar tabla existente (excepto cabecera y separador)
        for widget in self.scrollable_frame.winfo_children():
            if widget.grid_info()["row"] > 1:  # Solo eliminar filas de datos
                widget.destroy()
        
        # Obtener valores de filtros
        status_filter = self.status_filter_var.get()
        
        # Si no es "Todos los estados", convertir a valor interno
        status_value = None
        for key, label in self.status_labels.items():
            if label == status_filter:
                status_value = key
                break
        
        # Filtrar por aplicador si es admin
        applicator_filter = None
        if self.is_admin and hasattr(self, 'applicator_filter_var'):
            applicator_name = self.applicator_filter_var.get()
            if applicator_name != "Todos los aplicadores":
                # Buscar ID del aplicador por nombre
                for user in self.user_controller.get_all():
                    if user.get("username") == applicator_name:
                        applicator_filter = user.get("id")
                        break
        
        # Filtrar fumigaciones
        filtered_fumigations = []
        for fumigation in self.fumigations:
            # Filtrar por estado
            if status_value and fumigation.status != status_value:
                continue
            
            # Filtrar por aplicador
            if applicator_filter and fumigation.applicator_id != applicator_filter:
                continue
            
            # Si pasa todos los filtros, incluir
            filtered_fumigations.append(fumigation)
        
        # Mostrar fumigaciones filtradas
        self.display_fumigations(filtered_fumigations)
    
    def display_fumigations(self, fumigations):
        """Muestra las fumigaciones en la tabla"""
        if not fumigations:
            # Mostrar mensaje si no hay fumigaciones
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No hay fumigaciones que coincidan con los filtros",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.grid(row=2, column=0, columnspan=7, padx=10, pady=20)
            return
        
        # Obtener datos adicionales
        field_map = {}
        user_map = {}
        stock_map = {}
        
        # Cargar campos
        fields = self.field_controller.get_all()
        for field in fields:
            field_map[field.id] = field.name
        
        # Cargar usuarios
        users = self.user_controller.get_all()
        for user in users:
            user_map[user.get("id")] = user.get("username")
        
        # Cargar productos
        stock_items = self.stock_controller.get_all()
        for item in stock_items:
            stock_map[item.id] = item.product_name
        
        # Mostrar fumigaciones en la tabla
        for i, fumigation in enumerate(fumigations):
            row = i + 2  # +2 porque la fila 0 es la cabecera y la 1 es el separador
            
            # Campo
            field_name = field_map.get(fumigation.field_id, "Desconocido")
            field_label = ctk.CTkLabel(self.scrollable_frame, text=field_name, width=100)
            field_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")

            # Aplicador
            applicator_name = user_map.get(fumigation.applicator_id, "Desconocido")
            applicator_label = ctk.CTkLabel(self.scrollable_frame, text=applicator_name, width=100)
            applicator_label.grid(row=row, column=1, padx=10, pady=5, sticky="w")

            # Fecha
            date_text = fumigation.date.strftime("%d/%m/%Y") if fumigation.date else "No programada"
            date_label = ctk.CTkLabel(self.scrollable_frame, text=date_text, width=100)
            date_label.grid(row=row, column=2, padx=10, pady=5, sticky="w")

            # Productos
            product_names = []
            for product_id in fumigation.products:
                product_name = stock_map.get(product_id, "Desconocido")
                product_names.append(product_name)

            # Notas
            notes_text = fumigation.notes or ""
            if len(notes_text) > 30:
                notes_text = notes_text[:27] + "..."

            notes_label = ctk.CTkLabel(self.scrollable_frame, text=notes_text, width=100)
            notes_label.grid(row=row, column=3, padx=10, pady=5, sticky="w")

            # Productos
            product_names = []
            for product_id in fumigation.products:
                product_name = stock_map.get(product_id, "Desconocido")
                product_names.append(product_name)

            products_text = ", ".join(product_names) if product_names else "Ninguno"
            if len(products_text) > 30:
                products_text = products_text[:27] + "..."

            products_label = ctk.CTkLabel(self.scrollable_frame, text=products_text, width=100)
            products_label.grid(row=row, column=4, padx=10, pady=5, sticky="w")

            # Estado (con colores)
            status_text = self.status_labels.get(fumigation.status, "Desconocido")
            status_colors = {
                "scheduled": "#FFC107",  # Amarillo
                "in_progress": "#2196F3",  # Azul
                "completed": "#4CAF50",  # Verde
                "cancelled": "#F44336"   # Rojo
            }
            status_color = status_colors.get(fumigation.status, "#9E9E9E")

            status_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            status_frame.grid(row=row, column=5, padx=10, pady=5, sticky="w")

            status_indicator = ctk.CTkFrame(status_frame, width=10, height=10, fg_color=status_color, corner_radius=5)
            status_indicator.pack(side="left", padx=(0, 5))

            status_label = ctk.CTkLabel(status_frame, text=status_text, width=100)
            status_label.pack(side="left")
            
            # Frame para botones de acción
            action_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            action_frame.grid(row=row, column=6, padx=10, pady=5)
# views/fumigation_frames.py
import customtkinter as ctk
from datetime import datetime, timedelta
from controllers.fumigation_controller import FumigationController
from controllers.field_controller import FieldController
from controllers.user_controller import UserController
from controllers.stock_controller import StockController
from models.fumigation import Fumigation

class FumigationManagementFrame(ctk.CTkFrame):
    def __init__(self, master, auth_controller):
        super().__init__(master)
        self.master = master
        self.auth_controller = auth_controller
        self.fumigation_controller = FumigationController()
        self.field_controller = FieldController()
        self.user_controller = UserController(auth_controller)
        self.stock_controller = StockController()
        
        # Obtener información del usuario actual
        self.current_user = self.auth_controller.get_current_user() or {}
        self.is_admin = self.current_user and self.current_user.get('role') == 'admin'
        self.is_fumigator = self.current_user and self.current_user.get('role') == 'fumigator'

        # Lista de fumigaciones
        self.fumigations = []
        
        # Lista de estados disponibles
        self.status_options = ["scheduled", "in_progress", "completed", "cancelled"]
        self.status_labels = {
            "scheduled": "Programada",
            "in_progress": "En Progreso",
            "completed": "Completada",
            "cancelled": "Cancelada"
        }
        
        # Crear interfaz
        self.create_interface()
        
        # Cargar datos
        self.load_fumigations()
    
    def create_interface(self):
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Título
        self.grid_rowconfigure(1, weight=0)  # Botones y filtros
        self.grid_rowconfigure(2, weight=1)  # Tabla
        
        # Título
        if self.is_fumigator:
            title_text = "Mis Tareas de Fumigación"
        else:
            title_text = "Gestión de Fumigaciones"
        
        self.title_label = ctk.CTkLabel(
            self, 
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Frame para controles y filtros
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Botones de acción
        self.action_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.action_frame.pack(side="left", fill="y")
        
        # Botón para agregar fumigación
        if not self.is_fumigator:
            self.add_button = ctk.CTkButton(
                self.action_frame,
                text="+ Programar Fumigación",
                command=self.show_add_fumigation
            )
            self.add_button.pack(side="left", padx=(0, 10))
        
        # Botón para refrescar lista
        self.refresh_button = ctk.CTkButton(
            self.action_frame,
            text="↻ Refrescar",
            command=self.load_fumigations,
            fg_color="#4CAF50"
        )
        self.refresh_button.pack(side="left")
        
        # Frame para filtros
        self.filter_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.filter_frame.pack(side="right", fill="y")
        
        # Filtro por estado
        self.status_filter_var = ctk.StringVar(value="Todos los estados")
        status_options = ["Todos los estados"] + [self.status_labels[status] for status in self.status_options]
        self.status_filter = ctk.CTkOptionMenu(
            self.filter_frame,
            values=status_options,
            variable=self.status_filter_var,
            command=self.filter_fumigations
        )
        self.status_filter.pack(side="left", padx=(0, 10))
        
        # Filtro por aplicador (si es admin)
        if self.is_admin:
            self.applicator_filter_var = ctk.StringVar(value="Todos los aplicadores")
            
            # Obtener lista de usuarios (aplicadores posibles)
            users = self.user_controller.get_all()
            applicator_options = ["Todos los aplicadores"] + [user.get("username", "") for user in users]
            
            self.applicator_filter = ctk.CTkOptionMenu(
                self.filter_frame,
                values=applicator_options,
                variable=self.applicator_filter_var,
                command=self.filter_fumigations
            )
            self.applicator_filter.pack(side="left")
        
        # Frame para la tabla con scroll
        self.table_container = ctk.CTkFrame(self)
        self.table_container.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Configurar grid del contenedor
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(0, weight=1)
        
        # Crear scrollbar
        self.scrollable_frame = ctk.CTkScrollableFrame(self.table_container)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar grid del scrollable frame
        self.scrollable_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.scrollable_frame.grid_columnconfigure(6, weight=0)
        
        # Cabecera de la tabla
        headers = ["Campo", "Aplicador", "Fecha", "Notas", "Productos", "Estado", "Acciones"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.scrollable_frame,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                width=100
            )
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Separador
        separator = ctk.CTkFrame(self.scrollable_frame, height=1, fg_color="gray")
        separator.grid(row=1, column=0, columnspan=7, sticky="ew", padx=5)
    
    def load_fumigations(self):
        """Carga todas las fumigaciones"""
        # Limpiar tabla existente (excepto cabecera y separador)
        for widget in self.scrollable_frame.winfo_children():
            if widget.grid_info()["row"] > 1:  # Solo eliminar filas de datos
                widget.destroy()
        
        # Obtener fumigaciones
        if self.is_admin:
            self.fumigations = self.fumigation_controller.get_all()
        else:
            # Si no es admin, solo mostrar las fumigaciones asignadas a este usuario
            user_id = self.current_user.get('id')
            if user_id:
                self.fumigations = self.fumigation_controller.get_all(applicator_id=user_id)
            else:
                self.fumigations = []  # Si no hay ID de usuario, no mostrar fumigaciones
        
        if not self.fumigations:
            # Mostrar mensaje si no hay fumigaciones
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No hay fumigaciones registradas",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.grid(row=2, column=0, columnspan=7, padx=10, pady=20)
            return
        
        # Ordenar fumigaciones por fecha (más reciente primero)
        self.fumigations.sort(key=lambda x: x.date if x.date else datetime.now(), reverse=True)
        
        # Mostrar fumigaciones en la tabla
        self.display_fumigations(self.fumigations)
    
    def filter_fumigations(self, *args):
        """Filtra las fumigaciones según los criterios seleccionados"""
        # Limpiar tabla existente (excepto cabecera y separador)
        for widget in self.scrollable_frame.winfo_children():
            if widget.grid_info()["row"] > 1:  # Solo eliminar filas de datos
                widget.destroy()
        
        # Obtener valores de filtros
        status_filter = self.status_filter_var.get()
        
        # Si no es "Todos los estados", convertir a valor interno
        status_value = None
        for key, label in self.status_labels.items():
            if label == status_filter:
                status_value = key
                break
        
        # Filtrar por aplicador si es admin
        applicator_filter = None
        if self.is_admin and hasattr(self, 'applicator_filter_var'):
            applicator_name = self.applicator_filter_var.get()
            if applicator_name != "Todos los aplicadores":
                # Buscar ID del aplicador por nombre
                for user in self.user_controller.get_all():
                    if user.get("username") == applicator_name:
                        applicator_filter = user.get("id")
                        break
        
        # Filtrar fumigaciones
        filtered_fumigations = []
        for fumigation in self.fumigations:
            # Filtrar por estado
            if status_value and fumigation.status != status_value:
                continue
            
            # Filtrar por aplicador
            if applicator_filter and fumigation.applicator_id != applicator_filter:
                continue
            
            # Si pasa todos los filtros, incluir
            filtered_fumigations.append(fumigation)
        
        # Mostrar fumigaciones filtradas
        self.display_fumigations(filtered_fumigations)
    
    def display_fumigations(self, fumigations):
        """Muestra las fumigaciones en la tabla"""
        if not fumigations:
            # Mostrar mensaje si no hay fumigaciones
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No hay fumigaciones que coincidan con los filtros",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.grid(row=2, column=0, columnspan=7, padx=10, pady=20)
            return
        
        # Obtener datos adicionales
        field_map = {}
        user_map = {}
        stock_map = {}
        
        # Cargar campos
        fields = self.field_controller.get_all()
        for field in fields:
            field_map[field.id] = field.name
        
        # Cargar usuarios
        users = self.user_controller.get_all()
        for user in users:
            user_map[user.get("id")] = user.get("username")
        
        # Cargar productos
        stock_items = self.stock_controller.get_all()
        for item in stock_items:
            stock_map[item.id] = item.product_name
        
        # Mostrar fumigaciones en la tabla
        for i, fumigation in enumerate(fumigations):
            row = i + 2  # +2 porque la fila 0 es la cabecera y la 1 es el separador
            
            # Campo
            field_name = field_map.get(fumigation.field_id, "Desconocido")
            field_label = ctk.CTkLabel(self.scrollable_frame, text=field_name, width=100)
            field_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")

            # Aplicador
            applicator_name = user_map.get(fumigation.applicator_id, "Desconocido")
            applicator_label = ctk.CTkLabel(self.scrollable_frame, text=applicator_name, width=100)
            applicator_label.grid(row=row, column=1, padx=10, pady=5, sticky="w")

            # Fecha
            date_text = fumigation.date.strftime("%d/%m/%Y") if fumigation.date else "No programada"
            date_label = ctk.CTkLabel(self.scrollable_frame, text=date_text, width=100)
            date_label.grid(row=row, column=2, padx=10, pady=5, sticky="w")

            # Productos
            product_names = []
            for product_id in fumigation.products:
                product_name = stock_map.get(product_id, "Desconocido")
                product_names.append(product_name)

            products_text = ", ".join(product_names) if product_names else "Ninguno"
            if len(products_text) > 30:
                products_text = products_text[:27] + "..."

            products_label = ctk.CTkLabel(self.scrollable_frame, text=products_text, width=100)
            products_label.grid(row=row, column=3, padx=10, pady=5, sticky="w")

            # Estado (con colores)
            status_text = self.status_labels.get(fumigation.status, "Desconocido")
            status_colors = {
                "scheduled": "#FFC107",  # Amarillo
                "in_progress": "#2196F3",  # Azul
                "completed": "#4CAF50",  # Verde
                "cancelled": "#F44336"   # Rojo
            }
            status_color = status_colors.get(fumigation.status, "#9E9E9E")

            status_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            status_frame.grid(row=row, column=4, padx=10, pady=5, sticky="w")

            status_indicator = ctk.CTkFrame(status_frame, width=10, height=10, fg_color=status_color, corner_radius=5)
            status_indicator.pack(side="left", padx=(0, 5))

            status_label = ctk.CTkLabel(status_frame, text=status_text, width=100)
            status_label.pack(side="left")

            # Notas (truncadas si son muy largas)
            notes_text = fumigation.notes or ""
            if len(notes_text) > 30:
                notes_text = notes_text[:27] + "..."

            notes_label = ctk.CTkLabel(self.scrollable_frame, text=notes_text, width=100)
            notes_label.grid(row=row, column=5, padx=10, pady=5, sticky="w")
            
            # Frame para botones de acción
            action_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            action_frame.grid(row=row, column=6, padx=10, pady=5)
            
            # Botón para ver detalles
            details_button = ctk.CTkButton(
                action_frame,
                text="Detalles",
                width=70,
                height=25,
                command=lambda fid=fumigation.id: self.show_fumigation_details(fid)
            )
            details_button.pack(side="left", padx=(0, 5))
            
            # Según el estado, mostrar diferentes botones
            if fumigation.status == "scheduled":
                # Botón para iniciar fumigación
                start_button = ctk.CTkButton(
                    action_frame,
                    text="Iniciar",
                    width=70,
                    height=25,
                    fg_color="#2196F3",
                    command=lambda fid=fumigation.id: self.start_fumigation(fid)
                )
                start_button.pack(side="left", padx=(0, 5))
                
                # Botón para cancelar
                cancel_button = ctk.CTkButton(
                    action_frame,
                    text="Cancelar",
                    width=70,
                    height=25,
                    fg_color="#F44336",
                    command=lambda fid=fumigation.id: self.cancel_fumigation(fid)
                )
                cancel_button.pack(side="left")
            
            elif fumigation.status == "in_progress":
                # Botón para completar
                complete_button = ctk.CTkButton(
                    action_frame,
                    text="Completar",
                    width=80,
                    height=25,
                    fg_color="#4CAF50",
                    command=lambda fid=fumigation.id: self.complete_fumigation(fid)
                )
                complete_button.pack(side="left")
            
            elif fumigation.status == "completed" or fumigation.status == "cancelled":
                # Para fumigaciones completadas o canceladas, solo permitir a admin editar
                if self.is_admin:
                    edit_button = ctk.CTkButton(
                        action_frame,
                        text="Editar",
                        width=70,
                        height=25,
                        command=lambda fid=fumigation.id: self.show_edit_fumigation(fid)
                    )
                    edit_button.pack(side="left")
            
            # Agregar un separador después de cada fila
            if i < len(fumigations) - 1:
                row_separator = ctk.CTkFrame(self.scrollable_frame, height=1, fg_color="gray70")
                row_separator.grid(row=row+1, column=0, columnspan=7, sticky="ew", padx=20)
    
    def show_add_fumigation(self):
        """Muestra el formulario para agregar una nueva fumigación"""
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Programar Fumigación")
        dialog.geometry("700x600")
        dialog.resizable(False, False)
        dialog.grab_set()  # Modal
        
        # Centrar en pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Formulario con scroll
        form_container = ctk.CTkFrame(dialog)
        form_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        form_container.grid_columnconfigure(0, weight=1)
        form_container.grid_rowconfigure(0, weight=1)
        
        form_scroll = ctk.CTkScrollableFrame(form_container)
        form_scroll.grid(row=0, column=0, sticky="nsew")
        
        # Título
        title_label = ctk.CTkLabel(
            form_scroll, 
            text="Programar Nueva Fumigación",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20), anchor="w")
        
        # Obtener datos para los selectores
        fields = self.field_controller.get_all()
        fields_map = {field.id: field.name for field in fields}
        
        applicators = []
        if self.is_admin:
            applicators = self.user_controller.get_all()
        else:
            # Si no es admin, sólo se puede asignar a sí mismo
            applicators = [{"id": self.current_user.get("id"), "username": self.current_user.get("username")}]
        
        # Selección de campo
        field_label = ctk.CTkLabel(form_scroll, text="Campo *", anchor="w")
        field_label.pack(anchor="w", pady=(10, 0))
        
        field_options = ["Seleccionar campo..."]
        for field in fields:
            field_name = field.name or "Sin nombre"
            field_location = field.location or "Sin ubicación"
            field_options.append(f"{field_name} ({field_location})")
        field_var = ctk.StringVar(value=field_options[0])
        field_option = ctk.CTkOptionMenu(
            form_scroll,
            values=field_options,
            variable=field_var
        )
        field_option.pack(fill="x", pady=(5, 0))
        
        # Selección de aplicador
        applicator_label = ctk.CTkLabel(form_scroll, text="Aplicador *", anchor="w")
        applicator_label.pack(anchor="w", pady=(10, 0))
        
        applicator_options = ["Seleccionar aplicador..."]
        for user in applicators:
            username = user.get("username")
            if username is not None:  # Asegurarse de que el nombre de usuario no sea None
                applicator_options.append(username)
        applicator_var = ctk.StringVar(value=applicator_options[0])
        applicator_option = ctk.CTkOptionMenu(
            form_scroll,
            values=applicator_options,
            variable=applicator_var
        )
        applicator_option.pack(fill="x", pady=(5, 0))
        
        # Fecha de fumigación
        date_label = ctk.CTkLabel(form_scroll, text="Fecha *", anchor="w")
        date_label.pack(anchor="w", pady=(10, 0))
        
        date_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        date_frame.pack(fill="x", pady=(5, 0))
        
        # Fecha por defecto (mañana)
        tomorrow = datetime.now() + timedelta(days=1)
        
        # Dividir la fecha en día, mes y año
        day_var = ctk.StringVar(value=str(tomorrow.day))
        month_var = ctk.StringVar(value=str(tomorrow.month))
        year_var = ctk.StringVar(value=str(tomorrow.year))
        
        # Opciones para el día
        day_options = [str(i) for i in range(1, 32)]
        day_option = ctk.CTkOptionMenu(
            date_frame,
            values=day_options,
            variable=day_var,
            width=60
        )
        day_option.pack(side="left", padx=(0, 5))
        
        # Opciones para el mes
        month_options = [str(i) for i in range(1, 13)]
        month_option = ctk.CTkOptionMenu(
            date_frame,
            values=month_options,
            variable=month_var,
            width=60
        )
        month_option.pack(side="left", padx=(0, 5))
        
        # Opciones para el año
        year_options = [str(i) for i in range(tomorrow.year, tomorrow.year + 3)]
        year_option = ctk.CTkOptionMenu(
            date_frame,
            values=year_options,
            variable=year_var,
            width=80
        )
        year_option.pack(side="left")
        
        # Selección de productos
        products_label = ctk.CTkLabel(form_scroll, text="Productos *", anchor="w", font=ctk.CTkFont(weight="bold"))
        products_label.pack(anchor="w", pady=(20, 5))
        
        # Obtener productos disponibles (solo los que están recibidos)
        available_products = [p for p in self.stock_controller.get_all() if p.status == "received"]
        
        # Frame para la lista de productos con scroll
        products_container = ctk.CTkFrame(form_scroll)
        products_container.pack(fill="x", pady=(5, 0))
        
        products_container.grid_columnconfigure(0, weight=1)
        products_container.grid_rowconfigure(0, weight=1)
        
        products_scroll = ctk.CTkScrollableFrame(products_container, height=150)
        products_scroll.grid(row=0, column=0, sticky="nsew")
        
        # Variables para los checkboxes de productos
        product_vars = {}
        
        for i, product in enumerate(available_products):
            var = ctk.BooleanVar(value=False)
            checkbox = ctk.CTkCheckBox(
                products_scroll,
                text=f"{product.product_name} ({product.quantity} {product.unit})",
                variable=var
            )
            checkbox.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            product_vars[product.id] = var
        
        # Notas adicionales
        notes_label = ctk.CTkLabel(form_scroll, text="Notas Adicionales", anchor="w")
        notes_label.pack(anchor="w", pady=(10, 0))
        
        notes_entry = ctk.CTkTextbox(form_scroll, height=100)
        notes_entry.pack(fill="x", pady=(5, 0))
        
        # Mensaje de error
        error_label = ctk.CTkLabel(form_scroll, text="", text_color="red")
        error_label.pack(pady=(15, 0))
        
        # Botones
        button_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Botón cancelar
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "#DCE4EE"),
            command=dialog.destroy
        )
        cancel_button.pack(side="left", padx=(0, 10))
        
        # Botón guardar
        def save_fumigation():
            # Validar campos requeridos
            field_selection = field_var.get()
            applicator_selection = applicator_var.get()
            
            if field_selection == "Seleccionar campo...":
                error_label.configure(text="Debe seleccionar un campo")
                return
            
            if applicator_selection == "Seleccionar aplicador...":
                error_label.configure(text="Debe seleccionar un aplicador")
                return
            
            # Validar fecha
            try:
                day = int(day_var.get())
                month = int(month_var.get())
                year = int(year_var.get())
                fumigation_date = datetime(year, month, day)
                
                # Verificar que la fecha no sea en el pasado
                if fumigation_date.date() < datetime.now().date():
                    error_label.configure(text="La fecha no puede ser en el pasado")
                    return
            except ValueError:
                error_label.configure(text="Fecha inválida")
                return
            
            # Validar productos seleccionados
            selected_products = []
            for product_id, var in product_vars.items():
                if var.get():
                    selected_products.append(product_id)
            
            if not selected_products:
                error_label.configure(text="Debe seleccionar al menos un producto")
                return
            
            # Obtener IDs de campo y aplicador
            field_id = None
            for field in fields:
                field_text = f"{field.name} ({field.location})"
                if field_text == field_selection:
                    field_id = field.id
                    break
            
            applicator_id = None
            for user in applicators:
                if user.get("username") == applicator_selection:
                    applicator_id = user.get("id")
                    break
            
            # Obtener notas
            notes = notes_entry.get("0.0", "end").strip()
            
            # Crear objeto fumigación
            fumigation = Fumigation(
                field_id=field_id,
                applicator_id=applicator_id,
                products=selected_products,
                date=fumigation_date,
                status="scheduled",
                notes=notes
            )
            
            # Guardar en la base de datos
            result = self.fumigation_controller.create(fumigation)
            
            if result["success"]:
                dialog.destroy()
                self.load_fumigations()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al guardar"))
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Programar",
            command=save_fumigation
        )
        save_button.pack(side="right")
    
    def show_fumigation_details(self, fumigation_id):
        """Muestra los detalles de una fumigación"""
        # Obtener datos de la fumigación
        fumigation = self.fumigation_controller.get_by_id(fumigation_id)
        if not fumigation:
            return
        
        # Obtener datos adicionales
        field = self.field_controller.get_by_id(fumigation.field_id)
        field_name = field.name if field else "Desconocido"
        
        applicator = self.user_controller.get_by_id(fumigation.applicator_id)
        applicator_name = applicator.get("username") if applicator else "Desconocido"
        
        # Obtener nombres de productos
        product_details = []
        for product_id in fumigation.products:
            product = self.stock_controller.get_by_id(product_id)
            if product:
                product_details.append(f"{product.product_name} ({product.quantity} {product.unit})")
            else:
                product_details.append(f"Producto ID: {product_id}")
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Detalles de Fumigación")
        dialog.geometry("600x500")
        dialog.resizable(False, False)
        dialog.grab_set()  # Modal
        
        # Centrar en pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Contenedor principal
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título con estado
        status_text = self.status_labels.get(fumigation.status, "Desconocido")
        status_colors = {
            "scheduled": "#FFC107",  # Amarillo
            "in_progress": "#2196F3",  # Azul
            "completed": "#4CAF50",  # Verde
            "cancelled": "#F44336"   # Rojo
        }
        status_color = status_colors.get(fumigation.status, "#9E9E9E")
        
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        status_indicator = ctk.CTkFrame(title_frame, width=15, height=15, fg_color=status_color, corner_radius=7)
        status_indicator.pack(side="left", padx=(0, 10))
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text=f"Fumigación: {field_name} ({status_text})",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left")
        
        # Detalles principales
        details_frame = ctk.CTkFrame(main_frame)
        details_frame.pack(fill="x", pady=(0, 20))
        
        # Campo
        field_label = ctk.CTkLabel(details_frame, text="Campo:", font=ctk.CTkFont(weight="bold"))
        field_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        field_value = ctk.CTkLabel(details_frame, text=field_name)
        field_value.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Aplicador
        applicator_label = ctk.CTkLabel(details_frame, text="Aplicador:", font=ctk.CTkFont(weight="bold"))
        applicator_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        applicator_value = ctk.CTkLabel(details_frame, text=applicator_name)
        applicator_value.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Fecha programada
        date_label = ctk.CTkLabel(details_frame, text="Fecha programada:", font=ctk.CTkFont(weight="bold"))
        date_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        date_value = ctk.CTkLabel(details_frame, text=fumigation.date.strftime("%d/%m/%Y") if fumigation.date else "No establecida")
        date_value.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Fechas adicionales según estado
        row_index = 3
        
        if fumigation.started_at:
            started_label = ctk.CTkLabel(details_frame, text="Fecha de inicio:", font=ctk.CTkFont(weight="bold"))
            started_label.grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
            
            started_value = ctk.CTkLabel(details_frame, text=fumigation.started_at.strftime("%d/%m/%Y %H:%M"))
            started_value.grid(row=row_index, column=1, padx=10, pady=5, sticky="w")
            row_index += 1
        
        if fumigation.completed_at:
            completed_label = ctk.CTkLabel(details_frame, text="Fecha de finalización:", font=ctk.CTkFont(weight="bold"))
            completed_label.grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
            
            completed_value = ctk.CTkLabel(details_frame, text=fumigation.completed_at.strftime("%d/%m/%Y %H:%M"))
            completed_value.grid(row=row_index, column=1, padx=10, pady=5, sticky="w")
            row_index += 1
        
        # Lista de productos
        products_label = ctk.CTkLabel(main_frame, text="Productos utilizados:", font=ctk.CTkFont(weight="bold"))
        products_label.pack(anchor="w", pady=(0, 5))
        
        products_frame = ctk.CTkScrollableFrame(main_frame, height=100)
        products_frame.pack(fill="x", pady=(0, 10))
        
        if product_details:
            for i, product_text in enumerate(product_details):
                product_item = ctk.CTkLabel(products_frame, text=f"• {product_text}")
                product_item.pack(anchor="w", padx=10, pady=2)
        else:
            no_products = ctk.CTkLabel(products_frame, text="No hay productos asociados")
            no_products.pack(anchor="w", padx=10, pady=2)
        
        # Notas
        notes_label = ctk.CTkLabel(main_frame, text="Notas:", font=ctk.CTkFont(weight="bold"))
        notes_label.pack(anchor="w", pady=(0, 5))
        
        notes_text = fumigation.notes or "Sin notas adicionales"
        notes_box = ctk.CTkTextbox(main_frame, height=100)
        notes_box.pack(fill="x")
        notes_box.insert("0.0", notes_text)
        notes_box.configure(state="disabled")
        
        # Botones según el estado
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Botón para editar (solo admin o aplicador asignado)
        if self.is_admin or self.current_user.get("id") == fumigation.applicator_id:
            edit_button = ctk.CTkButton(
                button_frame,
                text="Editar",
                command=lambda: [dialog.destroy(), self.show_edit_fumigation(fumigation_id)]
            )
            edit_button.pack(side="left", padx=(0, 10))
        
        # Botones según el estado actual
        if fumigation.status == "scheduled":
            # Botón para iniciar
            start_button = ctk.CTkButton(
                button_frame,
                text="Iniciar Fumigación",
                fg_color="#2196F3",
                command=lambda: [dialog.destroy(), self.start_fumigation(fumigation_id)]
            )
            start_button.pack(side="left", padx=(0, 10))
            
            # Botón para cancelar
            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancelar Fumigación",
                fg_color="#F44336",
                command=lambda: [dialog.destroy(), self.cancel_fumigation(fumigation_id)]
            )
            cancel_button.pack(side="left")
        
        elif fumigation.status == "in_progress":
            # Botón para completar
            complete_button = ctk.CTkButton(
                button_frame,
                text="Completar Fumigación",
                fg_color="#4CAF50",
                command=lambda: [dialog.destroy(), self.complete_fumigation(fumigation_id)]
            )
            complete_button.pack(side="left")
        
        # Botón cerrar
        close_button = ctk.CTkButton(
            button_frame,
            text="Cerrar",
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "#DCE4EE"),
            command=dialog.destroy
        )
        close_button.pack(side="right")
    
    def show_edit_fumigation(self, fumigation_id):
        """Muestra el formulario para editar una fumigación"""
        # Obtener datos de la fumigación
        fumigation = self.fumigation_controller.get_by_id(fumigation_id)
        if not fumigation:
            return
        
        # Verificar permisos
        if not self.is_admin and self.current_user.get("id") != fumigation.applicator_id:
            # Mostrar mensaje de error
            dialog = ctk.CTkToplevel(self)
            dialog.title("Error")
            dialog.geometry("400x150")
            dialog.resizable(False, False)
            dialog.grab_set()  # Modal
            
            frame = ctk.CTkFrame(dialog)
            frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            error_label = ctk.CTkLabel(
                frame,
                text="No tienes permiso para editar esta fumigación",
                font=ctk.CTkFont(size=14)
            )
            error_label.pack(pady=(0, 20))
            
            close_button = ctk.CTkButton(
                frame,
                text="Cerrar",
                command=dialog.destroy
            )
            close_button.pack()
            
            return
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar Fumigación")
        dialog.geometry("700x600")
        dialog.resizable(False, False)
        dialog.grab_set()  # Modal
        
        # Centrar en pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Formulario con scroll
        form_container = ctk.CTkFrame(dialog)
        form_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        form_container.grid_columnconfigure(0, weight=1)
        form_container.grid_rowconfigure(0, weight=1)
        
        form_scroll = ctk.CTkScrollableFrame(form_container)
        form_scroll.grid(row=0, column=0, sticky="nsew")
        
        # Título
        title_label = ctk.CTkLabel(
            form_scroll, 
            text=f"Editar Fumigación",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20), anchor="w")
        
        # Obtener datos para los selectores
        fields = self.field_controller.get_all()
        fields_map = {field.id: field.name for field in fields}
        
        applicators = []
        if self.is_admin:
            applicators = self.user_controller.get_all()
        else:
            # Si no es admin, sólo se puede asignar a sí mismo
            applicators = [{"id": self.current_user.get("id"), "username": self.current_user.get("username")}]
        
        # Información sobre estado actual
        status_frame = ctk.CTkFrame(form_scroll, fg_color="#F0F0F0")
        status_frame.pack(fill="x", pady=(0, 20))
        
        status_text = self.status_labels.get(fumigation.status, "Desconocido")
        status_label = ctk.CTkLabel(
            status_frame,
            text=f"Estado actual: {status_text}",
            font=ctk.CTkFont(size=14)
        )
        status_label.pack(padx=20, pady=10)
        
        # Selección de campo
        field_label = ctk.CTkLabel(form_scroll, text="Campo *", anchor="w")
        field_label.pack(anchor="w", pady=(10, 0))
        
        # Preparar selección de campo
        current_field = None
        for field in fields:
            if field.id == fumigation.field_id:
                current_field = f"{field.name} ({field.location})"
                break
        
        field_options = ["Seleccionar campo..."] + [f"{field.name} ({field.location})" for field in fields]
        field_var = ctk.StringVar(value=current_field if current_field else field_options[0])
        field_option = ctk.CTkOptionMenu(
            form_scroll,
            values=field_options,
            variable=field_var
        )
        field_option.pack(fill="x", pady=(5, 0))
        
        # Selección de aplicador
        applicator_label = ctk.CTkLabel(form_scroll, text="Aplicador *", anchor="w")
        applicator_label.pack(anchor="w", pady=(10, 0))
        
        # Preparar selección de aplicador
        current_applicator = None
        for user in applicators:
            if user.get("id") == fumigation.applicator_id:
                current_applicator = user.get("username")
                break
        
        applicator_options = ["Seleccionar aplicador..."] + [user.get("username") for user in applicators]
        applicator_var = ctk.StringVar(value=current_applicator if current_applicator else applicator_options[0])
        applicator_option = ctk.CTkOptionMenu(
            form_scroll,
            values=applicator_options,
            variable=applicator_var
        )
        applicator_option.pack(fill="x", pady=(5, 0))
        
        # Fecha de fumigación
        date_label = ctk.CTkLabel(form_scroll, text="Fecha *", anchor="w")
        date_label.pack(anchor="w", pady=(10, 0))
        
        date_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        date_frame.pack(fill="x", pady=(5, 0))
        
        # Fecha actual de la fumigación
        current_date = fumigation.date or datetime.now()
        
        # Dividir la fecha en día, mes y año
        day_var = ctk.StringVar(value=str(current_date.day))
        month_var = ctk.StringVar(value=str(current_date.month))
        year_var = ctk.StringVar(value=str(current_date.year))
        
        # Opciones para el día
        day_options = [str(i) for i in range(1, 32)]
        day_option = ctk.CTkOptionMenu(
            date_frame,
            values=day_options,
            variable=day_var,
            width=60
        )
        day_option.pack(side="left", padx=(0, 5))
        
        # Opciones para el mes
        month_options = [str(i) for i in range(1, 13)]
        month_option = ctk.CTkOptionMenu(
            date_frame,
            values=month_options,
            variable=month_var,
            width=60
        )
        month_option.pack(side="left", padx=(0, 5))
        
        # Opciones para el año
        current_year = datetime.now().year
        year_options = [str(i) for i in range(current_year - 1, current_year + 3)]
        year_option = ctk.CTkOptionMenu(
            date_frame,
            values=year_options,
            variable=year_var,
            width=80
        )
        year_option.pack(side="left")
        
        # Selección de productos
        products_label = ctk.CTkLabel(form_scroll, text="Productos *", anchor="w", font=ctk.CTkFont(weight="bold"))
        products_label.pack(anchor="w", pady=(20, 5))
        
        # Obtener productos disponibles (solo los que están recibidos)
        available_products = [p for p in self.stock_controller.get_all() if p.status == "received"]
        
        # Frame para la lista de productos con scroll
        products_container = ctk.CTkFrame(form_scroll)
        products_container.pack(fill="x", pady=(5, 0))
        
        products_container.grid_columnconfigure(0, weight=1)
        products_container.grid_rowconfigure(0, weight=1)
        
        products_scroll = ctk.CTkScrollableFrame(products_container, height=150)
        products_scroll.grid(row=0, column=0, sticky="nsew")
        
        # Variables para los checkboxes de productos
        product_vars = {}
        
        for i, product in enumerate(available_products):
            is_selected = product.id in fumigation.products
            var = ctk.BooleanVar(value=is_selected)
            checkbox = ctk.CTkCheckBox(
                products_scroll,
                text=f"{product.product_name} ({product.quantity} {product.unit})",
                variable=var
            )
            checkbox.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            product_vars[product.id] = var
        
        # Notas adicionales
        notes_label = ctk.CTkLabel(form_scroll, text="Notas Adicionales", anchor="w")
        notes_label.pack(anchor="w", pady=(10, 0))
        
        notes_entry = ctk.CTkTextbox(form_scroll, height=100)
        notes_entry.pack(fill="x", pady=(5, 0))
        if fumigation.notes:
            notes_entry.insert("0.0", fumigation.notes)
        
        # Mensaje de error
        error_label = ctk.CTkLabel(form_scroll, text="", text_color="red")
        error_label.pack(pady=(15, 0))
        
        # Botones
        button_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Botón cancelar
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "#DCE4EE"),
            command=dialog.destroy
        )
        cancel_button.pack(side="left", padx=(0, 10))
        
        # Botón guardar
        def update_fumigation():
            # Validar campos requeridos
            field_selection = field_var.get()
            applicator_selection = applicator_var.get()
            
            if field_selection == "Seleccionar campo...":
                error_label.configure(text="Debe seleccionar un campo")
                return
            
            if applicator_selection == "Seleccionar aplicador...":
                error_label.configure(text="Debe seleccionar un aplicador")
                return
            
            # Validar fecha
            try:
                day = int(day_var.get())
                month = int(month_var.get())
                year = int(year_var.get())
                fumigation_date = datetime(year, month, day)
                
                # Si la fumigación ya está en progreso o completada, no validar que la fecha sea futura
                if fumigation.status == "scheduled" and fumigation_date.date() < datetime.now().date():
                    error_label.configure(text="La fecha no puede ser en el pasado para fumigaciones programadas")
                    return
            except ValueError:
                error_label.configure(text="Fecha inválida")
                return
            
            # Validar productos seleccionados
            selected_products = []
            for product_id, var in product_vars.items():
                if var.get():
                    selected_products.append(product_id)
            
            if not selected_products:
                error_label.configure(text="Debe seleccionar al menos un producto")
                return
            
            # Obtener IDs de campo y aplicador
            field_id = None
            for field in fields:
                field_text = f"{field.name} ({field.location})"
                if field_text == field_selection:
                    field_id = field.id
                    break
            
            applicator_id = None
            for user in applicators:
                if user.get("username") == applicator_selection:
                    applicator_id = user.get("id")
                    break
            
            # Obtener notas
            notes = notes_entry.get("0.0", "end").strip()
            
            # Datos actualizados
            updated_data = {
                "field_id": field_id,
                "applicator_id": applicator_id,
                "products": selected_products,
                "date": fumigation_date,
                "notes": notes
            }
            
            # Actualizar en la base de datos
            result = self.fumigation_controller.update(fumigation.id, updated_data)
            
            if result["success"]:
                dialog.destroy()
                self.load_fumigations()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al actualizar"))
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Guardar Cambios",
            command=update_fumigation
        )
        save_button.pack(side="right")
    
    def start_fumigation(self, fumigation_id):
        """Inicia una fumigación programada"""
        # Confirmar acción
        dialog = ctk.CTkToplevel(self)
        dialog.title("Iniciar Fumigación")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.grab_set()  # Modal
        
        # Centrar en pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Contenido
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mensaje
        message_label = ctk.CTkLabel(
            frame,
            text="¿Está seguro de iniciar esta fumigación?\nEsto registrará la fecha y hora de inicio.",
            font=ctk.CTkFont(size=14)
        )
        message_label.pack(pady=(0, 20))
        
        # Mensaje de error
        error_label = ctk.CTkLabel(frame, text="", text_color="red")
        error_label.pack(pady=(0, 10))
        
        # Botones
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # Botón cancelar
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "#DCE4EE"),
            command=dialog.destroy
        )
        cancel_button.pack(side="left", padx=(0, 10))
        
        # Botón iniciar
        def do_start_fumigation():
            result = self.fumigation_controller.change_status(fumigation_id, "in_progress")
            
            if result["success"]:
                dialog.destroy()
                self.load_fumigations()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al iniciar la fumigación"))
        
        start_button = ctk.CTkButton(
            button_frame,
            text="Iniciar",
            fg_color="#2196F3",
            command=do_start_fumigation
        )
        start_button.pack(side="right")
    
    def complete_fumigation(self, fumigation_id):
        """Marca una fumigación como completada"""
        # Confirmar acción
        dialog = ctk.CTkToplevel(self)
        dialog.title("Completar Fumigación")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.grab_set()  # Modal
        
        # Centrar en pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Contenido
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mensaje
        message_label = ctk.CTkLabel(
            frame,
            text="¿Está seguro de marcar esta fumigación como completada?\nEsto registrará la fecha y hora de finalización.",
            font=ctk.CTkFont(size=14)
        )
        message_label.pack(pady=(0, 20))
        
        # Mensaje de error
        error_label = ctk.CTkLabel(frame, text="", text_color="red")
        error_label.pack(pady=(0, 10))
        
        # Botones
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # Botón cancelar
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "#DCE4EE"),
            command=dialog.destroy
        )
        cancel_button.pack(side="left", padx=(0, 10))
        
        # Botón completar
        def do_complete_fumigation():
            result = self.fumigation_controller.change_status(fumigation_id, "completed")
            
            if result["success"]:
                dialog.destroy()
                self.load_fumigations()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al completar la fumigación"))
        
        complete_button = ctk.CTkButton(
            button_frame,
            text="Completar",
            fg_color="#4CAF50",
            command=do_complete_fumigation
        )
        complete_button.pack(side="right")
    
    def cancel_fumigation(self, fumigation_id):
        """Cancela una fumigación"""
        # Confirmar acción
        dialog = ctk.CTkToplevel(self)
        dialog.title("Cancelar Fumigación")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.grab_set()  # Modal
        
        # Centrar en pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Contenido
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mensaje
        message_label = ctk.CTkLabel(
            frame,
            text="¿Está seguro de cancelar esta fumigación?\nEsta acción puede ser reversible por un administrador.",
            font=ctk.CTkFont(size=14)
        )
        message_label.pack(pady=(0, 20))
        
        # Mensaje de error
        error_label = ctk.CTkLabel(frame, text="", text_color="red")
        error_label.pack(pady=(0, 10))
        
        # Botones
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # Botón no cancelar
        no_button = ctk.CTkButton(
            button_frame,
            text="No Cancelar",
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "#DCE4EE"),
            command=dialog.destroy
        )
        no_button.pack(side="left", padx=(0, 10))
        
        # Botón sí, cancelar
        def do_cancel_fumigation():
            result = self.fumigation_controller.change_status(fumigation_id, "cancelled")
            
            if result["success"]:
                dialog.destroy()
                self.load_fumigations()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al cancelar la fumigación"))
        
        yes_button = ctk.CTkButton(
            button_frame,
            text="Sí, Cancelar",
            fg_color="#F44336",
            command=do_cancel_fumigation
        )
        yes_button.pack(side="right")
