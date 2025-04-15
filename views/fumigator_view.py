
# views/fumigator_view.py
import customtkinter as ctk
from datetime import datetime
from controllers.fumigation_controller import FumigationController
from controllers.field_controller import FieldController
from controllers.stock_controller import StockController

class FumigatorDashboardView(ctk.CTkFrame):
    """Vista específica para usuarios con rol de fumigador"""
    
    def __init__(self, master, auth_controller):
        super().__init__(master)
        self.master = master
        self.auth_controller = auth_controller
        self.fumigation_controller = FumigationController()
        self.field_controller = FieldController()
        self.stock_controller = StockController()

        # Agregar función para cerrar sesión
        self.on_logout = lambda: self.auth_controller.logout()
        
        # Obtener información del usuario actual
        self.current_user = self.auth_controller.get_current_user() or {}
        
        # Lista de fumigaciones asignadas
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
        self.grid_rowconfigure(0, weight=0)  # Título y resumen
        self.grid_rowconfigure(1, weight=0)  # Filtros
        self.grid_rowconfigure(2, weight=1)  # Tabla de fumigaciones
        
        # Panel superior con título y resumen
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Configurar grid del encabezado
        self.header_frame.grid_columnconfigure(0, weight=1)  # Para el título
        self.header_frame.grid_columnconfigure(1, weight=0)  # Para el botón de logout
        
        # Título con nombre del fumigador
        title_label = ctk.CTkLabel(
            self.header_frame, 
            text=f"Panel de Fumigador: {self.current_user.get('username', 'Usuario')}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(10, 20), sticky="w")
        
        # Botón de cierre de sesión
        self.logout_button = ctk.CTkButton(
            self.header_frame,
            text="Cerrar Sesión",
            command=self.on_logout,
            width=120
        )
        self.logout_button.grid(row=0, column=1, padx=20, pady=(10, 20), sticky="e")

        # Resumen de tareas
        self.summary_scheduled = self.create_summary_card(self.header_frame, "Programadas", "0", "#FFC107")
        self.summary_scheduled.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.summary_in_progress = self.create_summary_card(self.header_frame, "En Progreso", "0", "#2196F3")
        self.summary_in_progress.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        self.summary_completed = self.create_summary_card(self.header_frame, "Completadas", "0", "#4CAF50")
        self.summary_completed.grid(row=1, column=2, padx=10, pady=10, sticky="ew")
        
        # Panel de filtros
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="ew")
        
        # Botón para refrescar lista
        self.refresh_button = ctk.CTkButton(
            self.filter_frame,
            text="↻ Refrescar",
            command=self.load_fumigations,
            fg_color="#4CAF50",
            width=100
        )
        self.refresh_button.pack(side="left", padx=(0, 10))
        
        # Filtro por estado
        self.status_filter_var = ctk.StringVar(value="Todos los estados")
        status_options = ["Todos los estados"] + [self.status_labels[status] for status in self.status_options]
        self.status_filter = ctk.CTkOptionMenu(
            self.filter_frame,
            values=status_options,
            variable=self.status_filter_var,
            command=self.filter_fumigations
        )
        self.status_filter.pack(side="right", padx=(10, 0))
        
        filter_label = ctk.CTkLabel(self.filter_frame, text="Filtrar por estado:")
        filter_label.pack(side="right")
        
        # Tabla de fumigaciones
        self.table_container = ctk.CTkFrame(self)
        self.table_container.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Configurar grid del contenedor
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(0, weight=1)
        
        # Crear scrollbar
        self.scrollable_frame = ctk.CTkScrollableFrame(self.table_container)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar grid del scrollable frame
        self.scrollable_frame.grid_columnconfigure(0, weight=1)  # Campo
        self.scrollable_frame.grid_columnconfigure(1, weight=1)  # Fecha
        self.scrollable_frame.grid_columnconfigure(2, weight=1)  # Estado
        self.scrollable_frame.grid_columnconfigure(3, weight=2)  # Productos
        self.scrollable_frame.grid_columnconfigure(4, weight=0)  # Acciones
        
        # Cabecera de la tabla
        headers = ["Campo", "Fecha", "Estado", "Productos", "Notas", "Acciones"]
        for i, header in enumerate(headers):
            if header == "Notas":
                label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text=header,
                    font=ctk.CTkFont(weight="bold")
                )
                label.grid(row=0, column=i, padx=0, pady=10, sticky="w")
            else:
                label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text=header,
                    font=ctk.CTkFont(weight="bold")
                )
                label.grid(row=0, column=i, padx=5, pady=10, sticky="w")
        
        # Separador
        separator = ctk.CTkFrame(self.scrollable_frame, height=1, fg_color="gray")
        separator.grid(row=1, column=0, columnspan=5, sticky="ew", padx=5)
    
    def create_summary_card(self, parent, title, value, color):
        """Crea una tarjeta de resumen para mostrar contadores de tareas"""
        card = ctk.CTkFrame(parent)
        
        # Título
        card_title = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14)
        )
        card_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Frame para el valor con indicador de color
        value_frame = ctk.CTkFrame(card, fg_color="transparent")
        value_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Indicador de color
        color_indicator = ctk.CTkFrame(value_frame, width=10, height=25, fg_color=color, corner_radius=3)
        color_indicator.pack(side="left", padx=(0, 10))
        
        # Valor
        self.value_label = ctk.CTkLabel(
            value_frame,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.value_label.pack(side="left")
        
        return card
    
    def load_fumigations(self):
        """Carga las fumigaciones asignadas al fumigador actual"""
        # Limpiar tabla existente (excepto cabecera y separador)
        for widget in self.scrollable_frame.winfo_children():
            if widget.grid_info()["row"] > 1:  # Solo eliminar filas de datos
                widget.destroy()
        
        # Obtener el ID del fumigador actual
        fumigator_id = self.current_user.get('id')
        if not fumigator_id:
            # Mostrar mensaje si no hay ID de usuario
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No se puede identificar al fumigador actual",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.grid(row=2, column=0, columnspan=5, padx=10, pady=20)
            return
        
        # Obtener fumigaciones asignadas a este fumigador
        self.fumigations = self.fumigation_controller.get_all(applicator_id=fumigator_id)
        
        # Actualizar contadores en las tarjetas de resumen
        counts = {
            "scheduled": 0,
            "in_progress": 0,
            "completed": 0,
            "cancelled": 0
        }
        
        for fumigation in self.fumigations:
            status = fumigation.status or "scheduled"
            if status in counts:
                counts[status] += 1
        
        # Actualizar tarjetas de resumen
        self.summary_scheduled.winfo_children()[1].winfo_children()[1].configure(text=str(counts["scheduled"]))
        self.summary_in_progress.winfo_children()[1].winfo_children()[1].configure(text=str(counts["in_progress"]))
        self.summary_completed.winfo_children()[1].winfo_children()[1].configure(text=str(counts["completed"]))
        
        if not self.fumigations:
            # Mostrar mensaje si no hay fumigaciones
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No tienes tareas de fumigación asignadas",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.grid(row=2, column=0, columnspan=5, padx=10, pady=20)
            return
        
        # Ordenar fumigaciones por fecha (más reciente primero)
        self.fumigations.sort(key=lambda x: x.date if x.date else datetime.now(), reverse=True)
        
        # Mostrar fumigaciones en la tabla
        self.display_fumigations(self.fumigations)
    
    def filter_fumigations(self, *args):
        """Filtra las fumigaciones según el estado seleccionado"""
        # Limpiar tabla existente (excepto cabecera y separador)
        for widget in self.scrollable_frame.winfo_children():
            if widget.grid_info()["row"] > 1:  # Solo eliminar filas de datos
                widget.destroy()
        
        # Obtener valor del filtro
        status_filter = self.status_filter_var.get()
        
        # Si no es "Todos los estados", convertir a valor interno
        status_value = None
        for key, label in self.status_labels.items():
            if label == status_filter:
                status_value = key
                break
        
        # Filtrar fumigaciones
        if status_value:
            filtered_fumigations = [f for f in self.fumigations if f.status == status_value]
        else:
            filtered_fumigations = self.fumigations
        
        # Mostrar fumigaciones filtradas
        self.display_fumigations(filtered_fumigations)
    
    def display_fumigations(self, fumigations):
        """Muestra las fumigaciones en la tabla"""
        if not fumigations:
            # Mostrar mensaje si no hay fumigaciones
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No hay tareas que coincidan con los filtros",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.grid(row=2, column=0, columnspan=5, padx=10, pady=20)
            return
        
        # Obtener datos adicionales
        field_map = {}
        stock_map = {}
        
        # Cargar campos
        fields = self.field_controller.get_all()
        for field in fields:
            field_map[field.id] = field.name
        
        # Cargar productos
        stock_items = self.stock_controller.get_all()
        for item in stock_items:
            stock_map[item.id] = item.product_name
        
        # Mostrar fumigaciones en la tabla
        for i, fumigation in enumerate(fumigations):
            row = i + 2  # +2 porque la fila 0 es la cabecera y la 1 es el separador
            
            # Campo
            field_name = field_map.get(fumigation.field_id, "Desconocido")
            field_label = ctk.CTkLabel(self.scrollable_frame, text=field_name)
            field_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            
            # Fecha
            date_text = fumigation.date.strftime("%d/%m/%Y") if fumigation.date else "No programada"
            date_label = ctk.CTkLabel(self.scrollable_frame, text=date_text)
            date_label.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            
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
            status_frame.grid(row=row, column=2, padx=10, pady=5, sticky="w")
            
            status_indicator = ctk.CTkFrame(status_frame, width=10, height=10, fg_color=status_color, corner_radius=5)
            status_indicator.pack(side="left", padx=(0, 5))
            
            status_label = ctk.CTkLabel(status_frame, text=status_text)
            status_label.pack(side="left")
            
            # Productos y notas
            product_names = []
            for product_id in fumigation.products:
                product_name = stock_map.get(product_id, "Desconocido")
                product_names.append(product_name)
            
            products_text = ", ".join(product_names) if product_names else "Ninguno"
            products_label = ctk.CTkLabel(self.scrollable_frame, text=products_text, wraplength=300)
            products_label.grid(row=row, column=3, padx=10, pady=5, sticky="w")
            
            notes_text = fumigation.notes or "Sin notas"
            notes_label = ctk.CTkLabel(self.scrollable_frame, text=f"Notas: {notes_text}", wraplength=300, anchor="w")
            notes_label.grid(row=row, column=4, padx=0, pady=5, sticky="w")

            # Frame para botones de acción
            action_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            action_frame.grid(row=row, column=5, padx=5, pady=5)
            
            # Botón para ver detalles
            details_button = ctk.CTkButton(
                action_frame,
                text="Detalles",
                width=70,
                height=25,
                command=lambda fid=fumigation.id: self.show_fumigation_details(fid)
            )
            details_button.pack(side="top", padx=(0, 5), pady=(0, 5))
            
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
                start_button.pack(side="top", padx=(0, 5), pady=(0, 5))
            
            elif fumigation.status == "in_progress":
                # Botón para completar
                complete_button = ctk.CTkButton(
                    action_frame,
                    text="Completar",
                    width=70,
                    height=25,
                    fg_color="#4CAF50",
                    command=lambda fid=fumigation.id: self.complete_fumigation(fid)
                )
                complete_button.pack(side="top", padx=(0, 5))
            
            # Agregar un separador después de cada fila
            if i < len(fumigations) - 1:
                row_separator = ctk.CTkFrame(self.scrollable_frame, height=1, fg_color="gray70")
                row_separator.grid(row=row+1, column=0, columnspan=5, sticky="ew", padx=20)
    
    def show_fumigation_details(self, fumigation_id):
        """Muestra los detalles de una fumigación"""
        # Aquí podemos reutilizar gran parte del código de la vista de fumigación regular
        from views.fumigation_frames import FumigationManagementFrame
        
        # Obtener datos de la fumigación
        fumigation = self.fumigation_controller.get_by_id(fumigation_id)
        if not fumigation:
            return
        
        # Obtener datos adicionales
        field = self.field_controller.get_by_id(fumigation.field_id)
        field_name = field.name if field else "Desconocido"
        
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
        
        # Fecha programada
        date_label = ctk.CTkLabel(details_frame, text="Fecha programada:", font=ctk.CTkFont(weight="bold"))
        date_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        date_value = ctk.CTkLabel(details_frame, text=fumigation.date.strftime("%d/%m/%Y") if fumigation.date else "No establecida")
        date_value.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Fechas adicionales según estado
        row_index = 2
        
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
        products_label = ctk.CTkLabel(main_frame, text="Productos a utilizar:", font=ctk.CTkFont(weight="bold"))
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
