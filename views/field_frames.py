# views/field_frames.py
import customtkinter as ctk
from datetime import datetime
from controllers.field_controller import FieldController
from models.field import Field

class FieldManagementFrame(ctk.CTkFrame):
    def __init__(self, master, auth_controller):
        super().__init__(master)
        self.master = master
        self.auth_controller = auth_controller
        self.field_controller = FieldController()
        
        # Lista de campos
        self.fields = []
        
        # Valores predefinidos para los selectores
        self.status_options = ["Activo", "En descanso", "En preparación", "Cosechado"]
        self.risk_levels = ["Bajo", "Medio", "Alto", "Crítico"]
        
        # Crear interfaz
        self.create_interface()
        
        # Cargar datos
        self.load_fields()
    
    def create_interface(self):
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Título
        self.grid_rowconfigure(1, weight=0)  # Botones y búsqueda
        self.grid_rowconfigure(2, weight=1)  # Tabla
        
        # Título
        self.title_label = ctk.CTkLabel(
            self, 
            text="Gestión de Campos",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Frame para botones y búsqueda
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Botón para agregar campo
        self.add_button = ctk.CTkButton(
            self.controls_frame,
            text="+ Agregar Campo",
            command=self.show_add_field
        )
        self.add_button.pack(side="left", padx=(0, 10))
        
        # Botón para refrescar lista
        self.refresh_button = ctk.CTkButton(
            self.controls_frame,
            text="↻ Refrescar",
            command=self.load_fields,
            fg_color="#4CAF50"
        )
        self.refresh_button.pack(side="left")
        
        # Campo de búsqueda (lado derecho)
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.controls_frame,
            placeholder_text="Buscar campo...",
            width=200,
            textvariable=self.search_var
        )
        self.search_entry.pack(side="right")
        
        # Botón de búsqueda
        self.search_button = ctk.CTkButton(
            self.controls_frame,
            text="🔍",
            width=30,
            command=self.search_fields
        )
        self.search_button.pack(side="right", padx=(5, 0))
        
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
        headers = ["Nombre", "Ubicación", "Tamaño", "Cultivo", "Estado", "Nivel de Riesgo", "Acciones"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.scrollable_frame,
                text=header,
                font=ctk.CTkFont(weight="bold")
            )
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Separador
        separator = ctk.CTkFrame(self.scrollable_frame, height=1, fg_color="gray")
        separator.grid(row=1, column=0, columnspan=7, sticky="ew", padx=5)
    
    def load_fields(self):
        # Limpiar tabla existente (excepto cabecera y separador)
        for widget in self.scrollable_frame.winfo_children():
            if widget.grid_info()["row"] > 1:  # Solo eliminar filas de datos
                widget.destroy()
        
        # Obtener campos
        self.fields = self.field_controller.get_all()
        
        if not self.fields:
            # Mostrar mensaje si no hay campos
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No hay campos registrados",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.grid(row=2, column=0, columnspan=7, padx=10, pady=20)
            return
        
        # Mostrar campos en la tabla
        for i, field in enumerate(self.fields):
            row = i + 2  # +2 porque la fila 0 es la cabecera y la 1 es el separador
            
            # Nombre
            name_label = ctk.CTkLabel(self.scrollable_frame, text=field.name or "")
            name_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            
            # Ubicación
            location_label = ctk.CTkLabel(self.scrollable_frame, text=field.location or "")
            location_label.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            
            # Tamaño
            size_label = ctk.CTkLabel(self.scrollable_frame, text=str(field.size or ""))
            size_label.grid(row=row, column=2, padx=10, pady=5, sticky="w")
            
            # Cultivo
            crop_label = ctk.CTkLabel(self.scrollable_frame, text=field.crop_type or "")
            crop_label.grid(row=row, column=3, padx=10, pady=5, sticky="w")
            
            # Estado
            status_label = ctk.CTkLabel(self.scrollable_frame, text=field.status or "")
            status_label.grid(row=row, column=4, padx=10, pady=5, sticky="w")
            
            # Nivel de riesgo con color
            risk_text = field.risk_level or "Bajo"
            risk_colors = {
                "Bajo": "#4CAF50",
                "Medio": "#FFC107",
                "Alto": "#FF5722",
                "Crítico": "#F44336"
            }
            risk_color = risk_colors.get(risk_text, "#4CAF50")
            
            risk_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            risk_frame.grid(row=row, column=5, padx=10, pady=5, sticky="w")
            
            risk_indicator = ctk.CTkFrame(risk_frame, width=15, height=15, fg_color=risk_color, corner_radius=7)
            risk_indicator.pack(side="left", padx=(0, 5))
            
            risk_label = ctk.CTkLabel(risk_frame, text=risk_text)
            risk_label.pack(side="left")
            
            # Frame para botones de acción
            action_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            action_frame.grid(row=row, column=6, padx=10, pady=5)
            
            # Botón editar
            edit_button = ctk.CTkButton(
                action_frame,
                text="Editar",
                width=70,
                height=25,
                command=lambda fid=field.id: self.show_edit_field(fid)
            )
            edit_button.pack(side="left", padx=(0, 5))
            
            # Botón eliminar
            delete_button = ctk.CTkButton(
                action_frame,
                text="Eliminar",
                width=70,
                height=25,
                fg_color="#FF5252",
                command=lambda fid=field.id: self.confirm_delete(fid)
            )
            delete_button.pack(side="left")
            
            # Agregar un separador después de cada fila
            if i < len(self.fields) - 1:
                row_separator = ctk.CTkFrame(self.scrollable_frame, height=1, fg_color="gray70")
                row_separator.grid(row=row+1, column=0, columnspan=7, sticky="ew", padx=20)
    
    def search_fields(self):
        search_text = self.search_var.get().lower().strip()
        
        # Si no hay texto de búsqueda, mostrar todos
        if not search_text:
            self.load_fields()
            return
        
        # Filtrar campos
        filtered_fields = [
            field for field in self.fields 
            if (search_text in (field.name or "").lower() or 
                search_text in (field.location or "").lower() or
                search_text in (field.crop_type or "").lower())
        ]
        
        # Limpiar tabla existente (excepto cabecera y separador)
        for widget in self.scrollable_frame.winfo_children():
            if widget.grid_info()["row"] > 1:  # Solo eliminar filas de datos
                widget.destroy()
        
        if not filtered_fields:
            # Mostrar mensaje si no hay resultados
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text=f"No se encontraron campos con '{search_text}'",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.grid(row=2, column=0, columnspan=7, padx=10, pady=20)
            return
        
        # Mostrar campos filtrados
        for i, field in enumerate(filtered_fields):
            row = i + 2  # +2 porque la fila 0 es la cabecera y la 1 es el separador
            
            # Nombre
            name_label = ctk.CTkLabel(self.scrollable_frame, text=field.name or "")
            name_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            
            # Ubicación
            location_label = ctk.CTkLabel(self.scrollable_frame, text=field.location or "")
            location_label.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            
            # Tamaño
            size_label = ctk.CTkLabel(self.scrollable_frame, text=str(field.size or ""))
            size_label.grid(row=row, column=2, padx=10, pady=5, sticky="w")
            
            # Cultivo
            crop_label = ctk.CTkLabel(self.scrollable_frame, text=field.crop_type or "")
            crop_label.grid(row=row, column=3, padx=10, pady=5, sticky="w")
            
            # Estado
            status_label = ctk.CTkLabel(self.scrollable_frame, text=field.status or "")
            status_label.grid(row=row, column=4, padx=10, pady=5, sticky="w")
            
            # Nivel de riesgo con color
            risk_text = field.risk_level or "Bajo"
            risk_colors = {
                "Bajo": "#4CAF50",
                "Medio": "#FFC107",
                "Alto": "#FF5722",
                "Crítico": "#F44336"
            }
            risk_color = risk_colors.get(risk_text, "#4CAF50")
            
            risk_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            risk_frame.grid(row=row, column=5, padx=10, pady=5, sticky="w")
            
            risk_indicator = ctk.CTkFrame(risk_frame, width=15, height=15, fg_color=risk_color, corner_radius=7)
            risk_indicator.pack(side="left", padx=(0, 5))
            
            risk_label = ctk.CTkLabel(risk_frame, text=risk_text)
            risk_label.pack(side="left")
            
            # Frame para botones de acción
            action_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            action_frame.grid(row=row, column=6, padx=10, pady=5)
            
            # Botón editar
            edit_button = ctk.CTkButton(
                action_frame,
                text="Editar",
                width=70,
                height=25,
                command=lambda fid=field.id: self.show_edit_field(fid)
            )
            edit_button.pack(side="left", padx=(0, 5))
            
            # Botón eliminar
            delete_button = ctk.CTkButton(
                action_frame,
                text="Eliminar",
                width=70,
                height=25,
                fg_color="#FF5252",
                command=lambda fid=field.id: self.confirm_delete(fid)
            )
            delete_button.pack(side="left")
            
            # Agregar un separador después de cada fila
            if i < len(filtered_fields) - 1:
                row_separator = ctk.CTkFrame(self.scrollable_frame, height=1, fg_color="gray70")
                row_separator.grid(row=row+1, column=0, columnspan=7, sticky="ew", padx=20)
    
    def show_add_field(self):
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agregar Campo")
        dialog.geometry("600x600")
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
            text="Nuevo Campo",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20), anchor="w")
        
        # Campos del formulario básicos
        basic_fields = [
            {"label": "Nombre", "var": "name", "required": True},
            {"label": "Ubicación", "var": "location", "required": True},
            {"label": "Tamaño", "var": "size", "required": True},
            {"label": "Tipo de Cultivo", "var": "crop_type", "required": True}
        ]
        
        field_entries = {}
        
        for field in basic_fields:
            # Label
            label_text = field["label"]
            if field["required"]:
                label_text += " *"
            
            label = ctk.CTkLabel(form_scroll, text=label_text, anchor="w")
            label.pack(anchor="w", pady=(10, 0))
            
            # Entry
            entry = ctk.CTkEntry(form_scroll)
            entry.pack(fill="x", pady=(5, 0))
            
            field_entries[field["var"]] = entry
        
        # Estado (selector)
        status_label = ctk.CTkLabel(form_scroll, text="Estado *", anchor="w")
        status_label.pack(anchor="w", pady=(10, 0))
        
        status_var = ctk.StringVar(value=self.status_options[0])
        status_option = ctk.CTkOptionMenu(
            form_scroll,
            values=self.status_options,
            variable=status_var
        )
        status_option.pack(fill="x", pady=(5, 0))
        field_entries["status"] = status_var
        
        # Nivel de riesgo (selector)
        risk_label = ctk.CTkLabel(form_scroll, text="Nivel de Riesgo *", anchor="w")
        risk_label.pack(anchor="w", pady=(10, 0))
        
        risk_var = ctk.StringVar(value=self.risk_levels[0])
        risk_option = ctk.CTkOptionMenu(
            form_scroll,
            values=self.risk_levels,
            variable=risk_var
        )
        risk_option.pack(fill="x", pady=(5, 0))
        field_entries["risk_level"] = risk_var
        
        # Plagas/Enfermedades (entrada de lista)
        pests_label = ctk.CTkLabel(form_scroll, text="Plagas/Enfermedades (separadas por coma)", anchor="w")
        pests_label.pack(anchor="w", pady=(10, 0))
        
        pests_entry = ctk.CTkEntry(form_scroll)
        pests_entry.pack(fill="x", pady=(5, 0))
        field_entries["pests"] = pests_entry
        
        # Trabajadores (entrada de lista)
        workers_label = ctk.CTkLabel(form_scroll, text="Trabajadores (separados por coma)", anchor="w")
        workers_label.pack(anchor="w", pady=(10, 0))
        
        workers_entry = ctk.CTkEntry(form_scroll)
        workers_entry.pack(fill="x", pady=(5, 0))
        field_entries["workers"] = workers_entry
        
        # Mensaje de error
        error_label = ctk.CTkLabel(form_scroll, text="", text_color="red")
        error_label.pack(pady=(10, 0))
        
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
        def save_field():
            # Validar campos requeridos
            for field in basic_fields:
                if field["required"]:
                    value = field_entries[field["var"]].get().strip()
                    
                    if not value:
                        error_label.configure(text=f"El campo {field['label']} es obligatorio")
                        return
            
            # Obtener listas de plagas y trabajadores
            pests_text = field_entries["pests"].get().strip()
            pests_list = [p.strip() for p in pests_text.split(",")] if pests_text else []
            
            workers_text = field_entries["workers"].get().strip()
            workers_list = [w.strip() for w in workers_text.split(",")] if workers_text else []
            
            # Crear objeto campo
            field = Field(
                name=field_entries["name"].get().strip(),
                location=field_entries["location"].get().strip(),
                size=field_entries["size"].get().strip(),
                crop_type=field_entries["crop_type"].get().strip(),
                status=field_entries["status"].get(),
                risk_level=field_entries["risk_level"].get(),
                pests=pests_list,
                workers=workers_list
            )
            
            # Guardar en la base de datos
            result = self.field_controller.create(field)
            
            if result["success"]:
                dialog.destroy()
                self.load_fields()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al guardar"))
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=save_field
        )
        save_button.pack(side="right")
    
    def show_edit_field(self, field_id):
        # Obtener datos del campo
        field = self.field_controller.get_by_id(field_id)
        if not field:
            return
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar Campo")
        dialog.geometry("600x600")
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
            text=f"Editar Campo: {field.name}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20), anchor="w")
        
        # Campos del formulario básicos
        basic_fields = [
            {"label": "Nombre", "var": "name", "required": True, "value": field.name or ""},
            {"label": "Ubicación", "var": "location", "required": True, "value": field.location or ""},
            {"label": "Tamaño", "var": "size", "required": True, "value": field.size or ""},
            {"label": "Tipo de Cultivo", "var": "crop_type", "required": True, "value": field.crop_type or ""}
        ]
        
        field_entries = {}
        
        for field_item in basic_fields:
            # Label
            label_text = field_item["label"]
            if field_item["required"]:
                label_text += " *"
            
            label = ctk.CTkLabel(form_scroll, text=label_text, anchor="w")
            label.pack(anchor="w", pady=(10, 0))
            
            # Entry
            entry = ctk.CTkEntry(form_scroll)
            entry.insert(0, field_item["value"])
            entry.pack(fill="x", pady=(5, 0))
            
            field_entries[field_item["var"]] = entry
        
        # Estado (selector)
        status_label = ctk.CTkLabel(form_scroll, text="Estado *", anchor="w")
        status_label.pack(anchor="w", pady=(10, 0))
        
        status_var = ctk.StringVar(value=field.status if field.status in self.status_options else self.status_options[0])
        status_option = ctk.CTkOptionMenu(
            form_scroll,
            values=self.status_options,
            variable=status_var
        )
        status_option.pack(fill="x", pady=(5, 0))
        field_entries["status"] = status_var
        
        # Nivel de riesgo (selector)
        risk_label = ctk.CTkLabel(form_scroll, text="Nivel de Riesgo *", anchor="w")
        risk_label.pack(anchor="w", pady=(10, 0))
        
        risk_var = ctk.StringVar(value=field.risk_level if field.risk_level in self.risk_levels else self.risk_levels[0])
        risk_option = ctk.CTkOptionMenu(
            form_scroll,
            values=self.risk_levels,
            variable=risk_var
        )
        risk_option.pack(fill="x", pady=(5, 0))
        field_entries["risk_level"] = risk_var
        
        # Plagas/Enfermedades (entrada de lista)
        pests_label = ctk.CTkLabel(form_scroll, text="Plagas/Enfermedades (separadas por coma)", anchor="w")
        pests_label.pack(anchor="w", pady=(10, 0))
        
        pests_entry = ctk.CTkEntry(form_scroll)
        pests_entry.insert(0, ", ".join(field.pests) if field.pests else "")
        pests_entry.pack(fill="x", pady=(5, 0))
        field_entries["pests"] = pests_entry
        
        # Trabajadores (entrada de lista)
        workers_label = ctk.CTkLabel(form_scroll, text="Trabajadores (separados por coma)", anchor="w")
        workers_label.pack(anchor="w", pady=(10, 0))
        
        workers_entry = ctk.CTkEntry(form_scroll)
        workers_entry.insert(0, ", ".join(field.workers) if field.workers else "")
        workers_entry.pack(fill="x", pady=(5, 0))
        field_entries["workers"] = workers_entry
        
        # Mensaje de error
        error_label = ctk.CTkLabel(form_scroll, text="", text_color="red")
        error_label.pack(pady=(10, 0))
        
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
        def update_field():
            # Validar campos requeridos
            for field_item in basic_fields:
                if field_item["required"]:
                    value = field_entries[field_item["var"]].get().strip()
                    
                    if not value:
                        error_label.configure(text=f"El campo {field_item['label']} es obligatorio")
                        return
            
            # Obtener listas de plagas y trabajadores
            pests_text = field_entries["pests"].get().strip()
            pests_list = [p.strip() for p in pests_text.split(",")] if pests_text else []
            
            workers_text = field_entries["workers"].get().strip()
            workers_list = [w.strip() for w in workers_text.split(",")] if workers_text else []
            
            # Datos actualizados
            updated_data = {
                "name": field_entries["name"].get().strip(),
                "location": field_entries["location"].get().strip(),
                "size": field_entries["size"].get().strip(),
                "crop_type": field_entries["crop_type"].get().strip(),
                "status": field_entries["status"].get(),
                "risk_level": field_entries["risk_level"].get(),
                "pests": pests_list,
                "workers": workers_list
            }
            
            # Guardar en la base de datos
            result = self.field_controller.update(field.id, updated_data)
            
            if result["success"]:
                dialog.destroy()
                self.load_fields()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al actualizar"))
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Actualizar",
            command=update_field
        )
        save_button.pack(side="right")
    
    def confirm_delete(self, field_id):
        # Obtener datos del campo
        field = self.field_controller.get_by_id(field_id)
        if not field:
            return
        
        # Crear ventana de confirmación
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar Eliminación")
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
        
        # Icono y mensaje
        warning_label = ctk.CTkLabel(
            frame,
            text="⚠️",
            font=ctk.CTkFont(size=40)
        )
        warning_label.pack(pady=(0, 10))

        message_label = ctk.CTkLabel(
           frame,
           text=f"¿Está seguro de eliminar el campo '{field.name}'?\nEsta acción no se puede deshacer.",
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

        # Botón eliminar
        def delete_field():
           result = self.field_controller.delete(field_id)
           
           if result["success"]:
               dialog.destroy()
               self.load_fields()  # Recargar lista
           else:
               error_label.configure(text=result.get("error", "Error al eliminar"))
       
        delete_button = ctk.CTkButton(
           button_frame,
           text="Eliminar",
           fg_color="#FF5252",
           command=delete_field
       )
        delete_button.pack(side="right")