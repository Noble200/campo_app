# views/warehouse_frames.py
import customtkinter as ctk
from datetime import datetime
from controllers.warehouse_controller import WarehouseController
from models.warehouse import Warehouse

class WarehouseManagementFrame(ctk.CTkFrame):
    def __init__(self, master, auth_controller):
        super().__init__(master)
        self.master = master
        self.auth_controller = auth_controller
        self.warehouse_controller = WarehouseController()
        
        # Lista de almacenes
        self.warehouses = []
        
        # Crear interfaz
        self.create_interface()
        
        # Cargar datos
        self.load_warehouses()
    
    def create_interface(self):
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Título
        self.grid_rowconfigure(1, weight=0)  # Botones
        self.grid_rowconfigure(2, weight=1)  # Tabla
        
        # Título
        self.title_label = ctk.CTkLabel(
            self, 
            text="Gestión de Almacenes",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Frame para botones
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Botón para agregar almacén
        self.add_button = ctk.CTkButton(
            self.button_frame,
            text="+ Agregar Almacén",
            command=self.show_add_warehouse
        )
        self.add_button.pack(side="left", padx=(0, 10))
        
        # Botón para refrescar lista
        self.refresh_button = ctk.CTkButton(
            self.button_frame,
            text="↻ Refrescar",
            command=self.load_warehouses,
            fg_color="#4CAF50"
        )
        self.refresh_button.pack(side="left")
        
        # Frame para la tabla
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Configurar grid de la tabla
        self.table_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.table_frame.grid_columnconfigure(4, weight=0)
        
        # Cabecera de la tabla
        headers = ["Nombre", "Ubicación", "Capacidad", "Descripción", "Acciones"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.table_frame,
                text=header,
                font=ctk.CTkFont(weight="bold")
            )
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Separador
        separator = ctk.CTkFrame(self.table_frame, height=1, fg_color="gray")
        separator.grid(row=1, column=0, columnspan=5, sticky="ew", padx=5)
    
    def load_warehouses(self):
        # Limpiar tabla existente (excepto cabecera y separador)
        for widget in self.table_frame.winfo_children():
            if widget.grid_info()["row"] > 1:  # Solo eliminar filas de datos
                widget.destroy()
        
        # Obtener almacenes
        self.warehouses = self.warehouse_controller.get_all()
        
        if not self.warehouses:
            # Mostrar mensaje si no hay almacenes
            no_data_label = ctk.CTkLabel(
                self.table_frame,
                text="No hay almacenes registrados",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.grid(row=2, column=0, columnspan=5, padx=10, pady=20)
            return
        
        # Mostrar almacenes en la tabla
        for i, warehouse in enumerate(self.warehouses):
            row = i + 2  # +2 porque la fila 0 es la cabecera y la 1 es el separador
            
            # Nombre
            name_label = ctk.CTkLabel(self.table_frame, text=warehouse.name or "")
            name_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            
            # Ubicación
            location_label = ctk.CTkLabel(self.table_frame, text=warehouse.location or "")
            location_label.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            
            # Capacidad
            capacity_label = ctk.CTkLabel(self.table_frame, text=str(warehouse.capacity or ""))
            capacity_label.grid(row=row, column=2, padx=10, pady=5, sticky="w")
            
            # Descripción (truncada si es muy larga)
            description = warehouse.description or ""
            if len(description) > 30:
                description = description[:30] + "..."
            description_label = ctk.CTkLabel(self.table_frame, text=description)
            description_label.grid(row=row, column=3, padx=10, pady=5, sticky="w")
            
            # Frame para botones de acción
            action_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            action_frame.grid(row=row, column=4, padx=10, pady=5)
            
            # Botón editar
            edit_button = ctk.CTkButton(
                action_frame,
                text="Editar",
                width=70,
                height=25,
                command=lambda wid=warehouse.id: self.show_edit_warehouse(wid)
            )
            edit_button.pack(side="left", padx=(0, 5))
            
            # Botón eliminar
            delete_button = ctk.CTkButton(
                action_frame,
                text="Eliminar",
                width=70,
                height=25,
                fg_color="#FF5252",
                command=lambda wid=warehouse.id: self.confirm_delete(wid)
            )
            delete_button.pack(side="left")
            
            # Agregar un separador después de cada fila
            if i < len(self.warehouses) - 1:
                row_separator = ctk.CTkFrame(self.table_frame, height=1, fg_color="gray70")
                row_separator.grid(row=row+1, column=0, columnspan=5, sticky="ew", padx=20)
    
    def show_add_warehouse(self):
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agregar Almacén")
        dialog.geometry("500x500")
        dialog.resizable(False, False)
        dialog.grab_set()  # Modal

        # Centrar en pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
        # Formulario
        form_frame = ctk.CTkFrame(dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
        # Título
        title_label = ctk.CTkLabel(
            form_frame, 
            text="Nuevo Almacén",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20), anchor="w")
    
        # Campos del formulario
        fields = [
            {"label": "Nombre", "var": "name", "required": True},
            {"label": "Ubicación", "var": "location", "required": True},
            {"label": "Capacidad", "var": "capacity", "required": False},
            {"label": "Descripción", "var": "description", "required": False, "multiline": True}
        ]
    
        field_entries = {}
    
        for field in fields:
            # Label
            label_text = field["label"]
            if field["required"]:
                label_text += " *"
        
            label = ctk.CTkLabel(form_frame, text=label_text, anchor="w")
            label.pack(anchor="w", pady=(10, 0))
        
            # Entry
            if field.get("multiline", False):
                entry = ctk.CTkTextbox(form_frame, height=80)
                entry.pack(fill="x", pady=(5, 0))
            else:
                entry = ctk.CTkEntry(form_frame)
                entry.pack(fill="x", pady=(5, 0))
        
            field_entries[field["var"]] = entry
    
        # Mensaje de error
        error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        error_label.pack(pady=(10, 0))

        # Botones
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        def save_warehouse():
            # Validar campos requeridos
            for field in fields:
                if field["required"]:
                    if field.get("multiline", False):
                        value = field_entries[field["var"]].get("0.0", "end").strip()
                    else:
                        value = field_entries[field["var"]].get().strip()

                    if not value:
                        error_label.configure(text=f"El campo {field['label']} es obligatorio")
                        return

            # Crear objeto almacén
            warehouse = Warehouse(
                name=field_entries["name"].get().strip(),
                location=field_entries["location"].get().strip(),
                capacity=field_entries["capacity"].get().strip(),
                description=field_entries["description"].get("0.0", "end").strip()
            )

            # Guardar en la base de datos
            result = self.warehouse_controller.create(warehouse)

            if result["success"]:
                dialog.destroy()
                self.load_warehouses()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al guardar"))

        # Botón guardar
        save_button = ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=lambda: save_warehouse()
        )
        save_button.pack(side="right")

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

    def show_edit_warehouse(self, warehouse_id):
        # Obtener datos del almacén
        warehouse = self.warehouse_controller.get_by_id(warehouse_id)
        if not warehouse:
            return
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar Almacén")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.grab_set()  # Modal
        
        # Centrar en pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Formulario
        form_frame = ctk.CTkFrame(dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            form_frame, 
            text=f"Editar Almacén: {warehouse.name}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20), anchor="w")
        
        # Campos del formulario
        fields = [
            {"label": "Nombre", "var": "name", "required": True, "value": warehouse.name or ""},
            {"label": "Ubicación", "var": "location", "required": True, "value": warehouse.location or ""},
            {"label": "Capacidad", "var": "capacity", "required": False, "value": warehouse.capacity or ""},
            {"label": "Descripción", "var": "description", "required": False, "multiline": True, "value": warehouse.description or ""}
        ]
        
        field_entries = {}
        
        for field in fields:
            # Label
            label_text = field["label"]
            if field["required"]:
                label_text += " *"
            
            label = ctk.CTkLabel(form_frame, text=label_text, anchor="w")
            label.pack(anchor="w", pady=(10, 0))
            
            # Entry
            if field.get("multiline", False):
                entry = ctk.CTkTextbox(form_frame, height=80)
                entry.insert("0.0", field["value"])
                entry.pack(fill="x", pady=(5, 0))
            else:
                entry = ctk.CTkEntry(form_frame)
                entry.insert(0, field["value"])
                entry.pack(fill="x", pady=(5, 0))
            
            field_entries[field["var"]] = entry
        
        # Mensaje de error
        error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        error_label.pack(pady=(10, 0))
        
        # Botones
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
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
        def update_warehouse():
            # Validar campos requeridos
            for field in fields:
                if field["required"]:
                    if field.get("multiline", False):
                        value = field_entries[field["var"]].get("0.0", "end").strip()
                    else:
                        value = field_entries[field["var"]].get().strip()
                    
                    if not value:
                        error_label.configure(text=f"El campo {field['label']} es obligatorio")
                        return
            
            # Datos actualizados
            updated_data = {
                "name": field_entries["name"].get().strip(),
                "location": field_entries["location"].get().strip(),
                "capacity": field_entries["capacity"].get().strip(),
                "description": field_entries["description"].get("0.0", "end").strip()
            }
            
            # Guardar en la base de datos
            result = self.warehouse_controller.update(warehouse.id, updated_data)
            
            if result["success"]:
                dialog.destroy()
                self.load_warehouses()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al actualizar"))
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Actualizar",
            command=update_warehouse
        )
        save_button.pack(side="right")
    
    def confirm_delete(self, warehouse_id):
        # Obtener datos del almacén
        warehouse = self.warehouse_controller.get_by_id(warehouse_id)
        if not warehouse:
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
            text="⚠️",  # Emoji de advertencia
            font=ctk.CTkFont(size=36)
        )
        warning_label.pack(pady=(0, 10))
        
        message_label = ctk.CTkLabel(
            frame,
            text=f"¿Está seguro de eliminar el almacén '{warehouse.name}'?\nEsta acción no se puede deshacer.",
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
        def delete_warehouse():
            result = self.warehouse_controller.delete(warehouse_id)
            
            if result["success"]:
                dialog.destroy()
                self.load_warehouses()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al eliminar"))
        
        delete_button = ctk.CTkButton(
            button_frame,
            text="Eliminar",
            fg_color="#FF5252",
            command=delete_warehouse
        )
        delete_button.pack(side="right")
