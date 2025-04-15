# views/stock_frames.py
import customtkinter as ctk
from datetime import datetime
from controllers.stock_controller import StockController
from controllers.warehouse_controller import WarehouseController
from models.stock import Stock

class StockManagementFrame(ctk.CTkFrame):
    def __init__(self, master, auth_controller):
        super().__init__(master)
        self.master = master
        self.auth_controller = auth_controller
        self.stock_controller = StockController()
        self.warehouse_controller = WarehouseController()
        
        # Lista de unidades disponibles
        self.units = ["kg", "g", "ton", "lb", "oz", "l", "ml", "unidad", "paquete"]
        
        # Lista de categorías
        self.categories = ["Fertilizante", "Pesticida", "Semilla", "Herramienta", "Equipo", "Otro"]
        
        # Lista de estados
        self.status_options = ["purchased", "received"]
        
        # Obtener lista de almacenes
        self.warehouses = []
        self.load_warehouses()
        
        # Lista de productos en stock
        self.stock_items = []
        
        # Crear interfaz
        self.create_interface()
        
        # Cargar datos
        self.load_stock()
    
    def load_warehouses(self):
        """Carga la lista de almacenes disponibles"""
        self.warehouses = self.warehouse_controller.get_all()
    
    def create_interface(self):
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Título
        self.grid_rowconfigure(1, weight=0)  # Controles y filtros
        self.grid_rowconfigure(2, weight=1)  # Tabla
        
        # Título
        self.title_label = ctk.CTkLabel(
            self, 
            text="Gestión de Inventario",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Frame para controles y filtros
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Botones de acción
        self.action_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.action_frame.pack(side="left", fill="y")
        
        # Botón para agregar producto
        self.add_button = ctk.CTkButton(
            self.action_frame,
            text="+ Agregar Producto",
            command=self.show_add_stock
        )
        self.add_button.pack(side="left", padx=(0, 10))
        
        # Botón para transferir producto
        self.transfer_button = ctk.CTkButton(
            self.action_frame,
            text="↔ Transferir",
            command=self.show_transfer_stock,
            fg_color="#FFA000"
        )
        self.transfer_button.pack(side="left", padx=(0, 10))
        
        # Botón para refrescar lista
        self.refresh_button = ctk.CTkButton(
            self.action_frame,
            text="↻ Refrescar",
            command=self.load_stock,
            fg_color="#4CAF50"
        )
        self.refresh_button.pack(side="left")
        
        # Frame para filtros
        self.filter_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.filter_frame.pack(side="right", fill="y")
        
        # Filtro por almacén
        self.warehouse_filter_var = ctk.StringVar(value="Todos los almacenes")
        
        # Crear lista de opciones para el filtro
        warehouse_options = ["Todos los almacenes"]
        warehouse_options.extend([w.name for w in self.warehouses])
        
        self.warehouse_filter = ctk.CTkOptionMenu(
            self.filter_frame,
            values=warehouse_options,
            variable=self.warehouse_filter_var,
            command=self.filter_stock
        )
        self.warehouse_filter.pack(side="left", padx=(0, 10))
        
        # Filtro por estado
        self.status_filter_var = ctk.StringVar(value="Todos los estados")
        self.status_filter = ctk.CTkOptionMenu(
            self.filter_frame,
            values=["Todos los estados", "Comprado", "Recibido"],
            variable=self.status_filter_var,
            command=self.filter_stock
        )
        self.status_filter.pack(side="left")
        
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
        headers = ["Producto", "Cantidad", "Unidad", "Almacén", "Estado", "Categoría", "Acciones"]
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
    
    def load_stock(self):
        """Carga todos los productos en stock"""
        # Limpiar tabla existente (excepto cabecera y separador)
        for widget in self.scrollable_frame.winfo_children():
            if widget.grid_info()["row"] > 1:  # Solo eliminar filas de datos
                widget.destroy()
        
        # Obtener productos en stock
        self.stock_items = self.stock_controller.get_all()
        
        if not self.stock_items:
            # Mostrar mensaje si no hay productos
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No hay productos en inventario",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.grid(row=2, column=0, columnspan=7, padx=10, pady=20)
            return
        
        # Mostrar productos en la tabla
        self.display_stock_items(self.stock_items)
    
    def display_stock_items(self, items):
        """Muestra los elementos de stock en la tabla"""
        if not items:
            # Mostrar mensaje si no hay productos
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No hay productos que coincidan con los filtros",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.grid(row=2, column=0, columnspan=7, padx=10, pady=20)
            return
        
        # Crear mapa de ID de almacén a nombre
        warehouse_map = {w.id: w.name for w in self.warehouses}
        
        # Mostrar productos en la tabla
        for i, item in enumerate(items):
            row = i + 2  # +2 porque la fila 0 es la cabecera y la 1 es el separador
            
            # Producto
            product_label = ctk.CTkLabel(self.scrollable_frame, text=item.product_name or "")
            product_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            
            # Cantidad
            quantity_label = ctk.CTkLabel(self.scrollable_frame, text=str(item.quantity or ""))
            quantity_label.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            
            # Unidad
            unit_label = ctk.CTkLabel(self.scrollable_frame, text=item.unit or "")
            unit_label.grid(row=row, column=2, padx=10, pady=5, sticky="w")
            
            # Almacén
            warehouse_name = warehouse_map.get(item.warehouse_id, "Sin asignar")
            warehouse_label = ctk.CTkLabel(self.scrollable_frame, text=warehouse_name)
            warehouse_label.grid(row=row, column=3, padx=10, pady=5, sticky="w")
            
            # Estado
            status_text = "Recibido" if item.status == "received" else "Comprado"
            status_color = "#4CAF50" if item.status == "received" else "#FFC107"
            
            status_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            status_frame.grid(row=row, column=4, padx=10, pady=5, sticky="w")
            
            status_indicator = ctk.CTkFrame(status_frame, width=10, height=10, fg_color=status_color, corner_radius=5)
            status_indicator.pack(side="left", padx=(0, 5))
            
            status_label = ctk.CTkLabel(status_frame, text=status_text)
            status_label.pack(side="left")
            
            # Categoría
            category_label = ctk.CTkLabel(self.scrollable_frame, text=item.category or "Sin categoría")
            category_label.grid(row=row, column=5, padx=10, pady=5, sticky="w")
            
            # Frame para botones de acción
            action_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            action_frame.grid(row=row, column=6, padx=10, pady=5)
            
            # Botón editar
            edit_button = ctk.CTkButton(
                action_frame,
                text="Editar",
                width=70,
                height=25,
                command=lambda sid=item.id: self.show_edit_stock(sid)
            )
            edit_button.pack(side="left", padx=(0, 5))
            
            # Botón eliminar
            delete_button = ctk.CTkButton(
                action_frame,
                text="Eliminar",
                width=70,
                height=25,
                fg_color="#FF5252",
                command=lambda sid=item.id: self.confirm_delete(sid)
            )
            delete_button.pack(side="left")
            
            # Agregar un separador después de cada fila
            if i < len(items) - 1:
                row_separator = ctk.CTkFrame(self.scrollable_frame, height=1, fg_color="gray70")
                row_separator.grid(row=row+1, column=0, columnspan=7, sticky="ew", padx=20)
    
    def filter_stock(self, *args):
        """Filtra los productos en stock según los criterios seleccionados"""
        # Limpiar tabla existente (excepto cabecera y separador)
        for widget in self.scrollable_frame.winfo_children():
            if widget.grid_info()["row"] > 1:  # Solo eliminar filas de datos
                widget.destroy()
        
        # Obtener valores de filtros
        warehouse_filter = self.warehouse_filter_var.get()
        status_filter = self.status_filter_var.get()
        
        # Filtrar por almacén
        filtered_items = self.stock_items
        if warehouse_filter != "Todos los almacenes":
            # Encontrar ID del almacén
            warehouse_id = None
            for w in self.warehouses:
                if w.name == warehouse_filter:
                    warehouse_id = w.id
                    break
            
            if warehouse_id:
                filtered_items = [item for item in filtered_items if item.warehouse_id == warehouse_id]
        
        # Filtrar por estado
        if status_filter != "Todos los estados":
            status_map = {"Comprado": "purchased", "Recibido": "received"}
            status_value = status_map.get(status_filter)
            if status_value:
                filtered_items = [item for item in filtered_items if item.status == status_value]
        
        # Mostrar productos filtrados
        self.display_stock_items(filtered_items)
    
    def show_add_stock(self):
        """Muestra el formulario para agregar un nuevo producto al stock"""
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agregar Producto")
        dialog.geometry("500x600")
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
            text="Nuevo Producto",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20), anchor="w")
        
        # Nombre del producto
        product_label = ctk.CTkLabel(form_scroll, text="Nombre del Producto *", anchor="w")
        product_label.pack(anchor="w", pady=(10, 0))
        
        product_entry = ctk.CTkEntry(form_scroll)
        product_entry.pack(fill="x", pady=(5, 0))
        
        # Cantidad
        quantity_label = ctk.CTkLabel(form_scroll, text="Cantidad *", anchor="w")
        quantity_label.pack(anchor="w", pady=(10, 0))
        
        quantity_entry = ctk.CTkEntry(form_scroll)
        quantity_entry.pack(fill="x", pady=(5, 0))
        
        # Unidad
        unit_label = ctk.CTkLabel(form_scroll, text="Unidad *", anchor="w")
        unit_label.pack(anchor="w", pady=(10, 0))
        
        unit_var = ctk.StringVar(value=self.units[0])
        unit_option = ctk.CTkOptionMenu(
            form_scroll,
            values=self.units,
            variable=unit_var
        )
        unit_option.pack(fill="x", pady=(5, 0))

        # Estado
        status_label = ctk.CTkLabel(form_scroll, text="Estado *", anchor="w")
        status_label.pack(anchor="w", pady=(10, 0))
       
        status_var = ctk.StringVar(value="received")
        status_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        status_frame.pack(fill="x", pady=(5, 0))
       
        received_radio = ctk.CTkRadioButton(
            status_frame,
            text="Recibido",
            variable=status_var,
            value="received",
            command=lambda: self.toggle_warehouse_selection(warehouse_frame, True)
        )
        received_radio.pack(side="left", padx=(0, 20))

        purchased_radio = ctk.CTkRadioButton(
            status_frame,
            text="Comprado (pendiente)",
            variable=status_var,
            value="purchased",
            command=lambda: self.toggle_warehouse_selection(warehouse_frame, False)
        )
        purchased_radio.pack(side="left")

        # Almacén
        warehouse_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        warehouse_frame.pack(fill="x", pady=(10, 0))
       
        warehouse_label = ctk.CTkLabel(warehouse_frame, text="Almacén *", anchor="w")
        warehouse_label.pack(anchor="w")
       
        warehouse_options = ["Seleccionar almacén..."] + [w.name for w in self.warehouses]
        warehouse_var = ctk.StringVar(value=warehouse_options[0])
        warehouse_option = ctk.CTkOptionMenu(
            warehouse_frame,
            values=warehouse_options,
            variable=warehouse_var
        )
        warehouse_option.pack(fill="x", pady=(5, 0))

        # Categoría
        category_label = ctk.CTkLabel(form_scroll, text="Categoría", anchor="w")
        category_label.pack(anchor="w", pady=(10, 0))
       
        category_var = ctk.StringVar(value=self.categories[0])
        category_option = ctk.CTkOptionMenu(
            form_scroll,
            values=self.categories,
            variable=category_var
        )
        category_option.pack(fill="x", pady=(5, 0))

        # Fecha de compra
        purchase_date_label = ctk.CTkLabel(form_scroll, text="Fecha de Compra", anchor="w")
        purchase_date_label.pack(anchor="w", pady=(10, 0))
       
        purchase_date_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        purchase_date_frame.pack(fill="x", pady=(5, 0))
       
        # Dividir la fecha en día, mes y año
        today = datetime.now()
        day_var = ctk.StringVar(value=str(today.day))
        month_var = ctk.StringVar(value=str(today.month))
        year_var = ctk.StringVar(value=str(today.year))
       
        # Opciones para el día
        day_options = [str(i) for i in range(1, 32)]
        day_option = ctk.CTkOptionMenu(
            purchase_date_frame,
            values=day_options,
            variable=day_var,
            width=60
        )
        day_option.pack(side="left", padx=(0, 5))

        # Opciones para el mes
        month_options = [str(i) for i in range(1, 13)]
        month_option = ctk.CTkOptionMenu(
            purchase_date_frame,
            values=month_options,
            variable=month_var,
            width=60
        )
        month_option.pack(side="left", padx=(0, 5))
       
        # Opciones para el año
        year_options = [str(i) for i in range(today.year - 5, today.year + 2)]
        year_option = ctk.CTkOptionMenu(
            purchase_date_frame,
            values=year_options,
            variable=year_var,
            width=80
        )
        year_option.pack(side="left")

        # Fecha de vencimiento (opcional)
        expiry_date_label = ctk.CTkLabel(form_scroll, text="Fecha de Vencimiento (opcional)", anchor="w")
        expiry_date_label.pack(anchor="w", pady=(10, 0))
       
        expiry_date_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        expiry_date_frame.pack(fill="x", pady=(5, 0))
       
        # Checkbox para habilitar/deshabilitar la fecha de vencimiento
        has_expiry_var = ctk.BooleanVar(value=False)
        has_expiry_check = ctk.CTkCheckBox(
            expiry_date_frame,
            text="Tiene fecha de vencimiento",
            variable=has_expiry_var,
            command=lambda: self.toggle_expiry_date(expiry_day_option, expiry_month_option, expiry_year_option, has_expiry_var.get())
        )
        has_expiry_check.pack(anchor="w", pady=(0, 5))
       
        # Dividir la fecha en día, mes y año
        expiry_day_var = ctk.StringVar(value="1")
        expiry_month_var = ctk.StringVar(value="1")
        expiry_year_var = ctk.StringVar(value=str(today.year + 1))

        # Opciones para el día
        expiry_day_option = ctk.CTkOptionMenu(
            expiry_date_frame,
            values=day_options,
            variable=expiry_day_var,
            width=60,
            state="disabled"
        )
        expiry_day_option.pack(side="left", padx=(0, 5))

        # Opciones para el mes
        expiry_month_option = ctk.CTkOptionMenu(
            expiry_date_frame,
            values=month_options,
            variable=expiry_month_var,
            width=60,
            state="disabled"
        )
        expiry_month_option.pack(side="left", padx=(0, 5))

        # Opciones para el año
        expiry_year_options = [str(i) for i in range(today.year, today.year + 11)]
        expiry_year_option = ctk.CTkOptionMenu(
            expiry_date_frame,
            values=expiry_year_options,
            variable=expiry_year_var,
            width=80,
            state="disabled"
        )
        expiry_year_option.pack(side="left")

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
        def save_stock():
            # Validar campos obligatorios
            product_name = product_entry.get().strip()
            quantity_str = quantity_entry.get().strip()
            unit = unit_var.get()
            status = status_var.get()
            warehouse_name = warehouse_var.get()
           
            if not product_name:
                error_label.configure(text="El nombre del producto es obligatorio")
                return
           
            try:
                quantity = float(quantity_str)
                if quantity <= 0:
                    error_label.configure(text="La cantidad debe ser un número mayor que cero")
                    return
            except ValueError:
                error_label.configure(text="La cantidad debe ser un número válido")
                return
           
            if status == "received" and warehouse_name == "Seleccionar almacén...":
                error_label.configure(text="Debe seleccionar un almacén para productos recibidos")
                return
            
            # Obtener ID del almacén
            warehouse_id = None
            if warehouse_name != "Seleccionar almacén...":
                for w in self.warehouses:
                    if w.name == warehouse_name:
                        warehouse_id = w.id
                        break
            # Obtener categoría
            category = category_var.get()
           
            # Obtener fecha de compra
            try:
                day = int(day_var.get())
                month = int(month_var.get())
                year = int(year_var.get())
                purchase_date = datetime(year, month, day)
            except ValueError:
                error_label.configure(text="Fecha de compra inválida")
                return
            
            # Obtener fecha de vencimiento (si aplica)
            expiry_date = None
            if has_expiry_var.get():
                try:
                    expiry_day = int(expiry_day_var.get())
                    expiry_month = int(expiry_month_var.get())
                    expiry_year = int(expiry_year_var.get())
                    expiry_date = datetime(expiry_year, expiry_month, expiry_day)
                   
                    # Verificar que la fecha de vencimiento sea posterior a la de compra
                    if expiry_date <= purchase_date:
                        error_label.configure(text="La fecha de vencimiento debe ser posterior a la de compra")
                        return
                except ValueError:
                    error_label.configure(text="Fecha de vencimiento inválida")
                    return
            
            # Crear objeto de stock
            stock_item = Stock(
                product_name=product_name,
                quantity=quantity,
                unit=unit,
                warehouse_id=warehouse_id,
                status=status,
                category=category,
                purchase_date=purchase_date,
                expiry_date=expiry_date
            )

            # Guardar en la base de datos
            result = self.stock_controller.create(stock_item)
           
            if result["success"]:
                dialog.destroy()
                self.load_stock()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al guardar el producto"))
       
        save_button = ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=save_stock
        )
        save_button.pack(side="right")

    def toggle_warehouse_selection(self, warehouse_frame, enable):
        """Habilita o deshabilita la selección de almacén según el estado"""
        for widget in warehouse_frame.winfo_children():
            if isinstance(widget, ctk.CTkOptionMenu):
                if enable:
                    widget.configure(state="normal")
                else:
                    widget.configure(state="disabled")

    def toggle_expiry_date(self, day_option, month_option, year_option, enable):
        """Habilita o deshabilita los selectores de fecha de vencimiento"""
        state = "normal" if enable else "disabled"
        day_option.configure(state=state)
        month_option.configure(state=state)
        year_option.configure(state=state)
   
    def show_edit_stock(self, stock_id):
        """Muestra el formulario para editar un producto existente"""
        # Obtener datos del producto
        stock_item = self.stock_controller.get_by_id(stock_id)
        if not stock_item:
            return
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar Producto")
        dialog.geometry("500x600")
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
            text=f"Editar Producto: {stock_item.product_name}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20), anchor="w")

        # Nombre del producto
        product_label = ctk.CTkLabel(form_scroll, text="Nombre del Producto *", anchor="w")
        product_label.pack(anchor="w", pady=(10, 0))
       
        product_entry = ctk.CTkEntry(form_scroll)
        product_entry.insert(0, stock_item.product_name or "")
        product_entry.pack(fill="x", pady=(5, 0))
       
        # Cantidad
        quantity_label = ctk.CTkLabel(form_scroll, text="Cantidad *", anchor="w")
        quantity_label.pack(anchor="w", pady=(10, 0))
       
        quantity_entry = ctk.CTkEntry(form_scroll)
        quantity_entry.insert(0, str(stock_item.quantity or ""))
        quantity_entry.pack(fill="x", pady=(5, 0))
       
        # Unidad
        unit_label = ctk.CTkLabel(form_scroll, text="Unidad *", anchor="w")
        unit_label.pack(anchor="w", pady=(10, 0))
       
        unit_var = ctk.StringVar(value=stock_item.unit if stock_item.unit in self.units else self.units[0])
        unit_option = ctk.CTkOptionMenu(
            form_scroll,
            values=self.units,
            variable=unit_var
        )
        unit_option.pack(fill="x", pady=(5, 0))

        # Estado
        status_label = ctk.CTkLabel(form_scroll, text="Estado *", anchor="w")
        status_label.pack(anchor="w", pady=(10, 0))
       
        status_var = ctk.StringVar(value=stock_item.status or "received")
        status_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        status_frame.pack(fill="x", pady=(5, 0))
       
        received_radio = ctk.CTkRadioButton(
            status_frame,
            text="Recibido",
            variable=status_var,
            value="received",
            command=lambda: self.toggle_warehouse_selection(warehouse_frame, True)
        )
        received_radio.pack(side="left", padx=(0, 20))
       
        purchased_radio = ctk.CTkRadioButton(
            status_frame,
            text="Comprado (pendiente)",
            variable=status_var,
            value="purchased",
            command=lambda: self.toggle_warehouse_selection(warehouse_frame, False)
        )
        purchased_radio.pack(side="left")

        # Almacén
        warehouse_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        warehouse_frame.pack(fill="x", pady=(10, 0))
       
        warehouse_label = ctk.CTkLabel(warehouse_frame, text="Almacén *", anchor="w")
        warehouse_label.pack(anchor="w")
       
        # Obtener nombre del almacén actual
        current_warehouse_name = "Seleccionar almacén..."
        for w in self.warehouses:
            if w.id == stock_item.warehouse_id:
                current_warehouse_name = w.name
                break
       
        warehouse_options = ["Seleccionar almacén..."] + [w.name for w in self.warehouses]
        warehouse_var = ctk.StringVar(value=current_warehouse_name)
        warehouse_option = ctk.CTkOptionMenu(
            warehouse_frame,
            values=warehouse_options,
            variable=warehouse_var
        )
        warehouse_option.pack(fill="x", pady=(5, 0))

        # Configurar estado inicial del selector de almacén
        self.toggle_warehouse_selection(warehouse_frame, status_var.get() == "received")
       
        # Categoría
        category_label = ctk.CTkLabel(form_scroll, text="Categoría", anchor="w")
        category_label.pack(anchor="w", pady=(10, 0))
       
        category_var = ctk.StringVar(value=stock_item.category if stock_item.category in self.categories else self.categories[0])
        category_option = ctk.CTkOptionMenu(
            form_scroll,
            values=self.categories,
            variable=category_var
        )
        category_option.pack(fill="x", pady=(5, 0))
       
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
        def update_stock():
            # Validar campos obligatorios
            product_name = product_entry.get().strip()
            quantity_str = quantity_entry.get().strip()
            unit = unit_var.get()
            status = status_var.get()
            warehouse_name = warehouse_var.get()
           
            if not product_name:
                error_label.configure(text="El nombre del producto es obligatorio")
                return
           
            try:
                quantity = float(quantity_str)
                if quantity <= 0:
                    error_label.configure(text="La cantidad debe ser un número mayor que cero")
                    return
            except ValueError:
                error_label.configure(text="La cantidad debe ser un número válido")
                return
           
            if status == "received" and warehouse_name == "Seleccionar almacén...":
                error_label.configure(text="Debe seleccionar un almacén para productos recibidos")
                return
            
            # Obtener ID del almacén
            warehouse_id = None
            if warehouse_name != "Seleccionar almacén...":
                for w in self.warehouses:
                    if w.name == warehouse_name:
                        warehouse_id = w.id
                        break
           
            # Obtener categoría
            category = category_var.get()
           
            # Datos actualizados
            updated_data = {
                "product_name": product_name,
                "quantity": quantity,
                "unit": unit,
                "warehouse_id": warehouse_id,
                "status": status,
                "category": category
            }
            # Actualizar en la base de datos
            result = self.stock_controller.update(stock_item.id, updated_data)
           
            if result["success"]:
                dialog.destroy()
                self.load_stock()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al actualizar el producto"))
       
        save_button = ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=update_stock
        )
        save_button.pack(side="right")

    def show_transfer_stock(self):
        """Muestra el formulario para transferir productos entre almacenes"""
        # Comprobar si hay almacenes
        if len(self.warehouses) < 2:
            # Mostrar mensaje de error
            dialog = ctk.CTkToplevel(self)
            dialog.title("Error")
            dialog.geometry("400x150")
            dialog.resizable(False, False)
            dialog.grab_set()  # Modal
           
            # Centrar en pantalla
            dialog.update_idletasks()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (dialog.winfo_screenheight() // 2) - (height // 2)
            dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))

            # Mensaje
            frame = ctk.CTkFrame(dialog)
            frame.pack(fill="both", expand=True, padx=20, pady=20)
           
            message_label = ctk.CTkLabel(
                frame,
                text="Se necesitan al menos dos almacenes para realizar transferencias.",
                font=ctk.CTkFont(size=14),
                wraplength=360
            )
            message_label.pack(pady=(0, 20))

            # Botón cerrar
            close_button = ctk.CTkButton(
                frame,
                text="Cerrar",
                command=dialog.destroy
            )
            close_button.pack()
           
            return
        
        # Filtrar productos recibidos y con almacén asignado
        transfer_items = [item for item in self.stock_items if item.status == "received" and item.warehouse_id]

        if not transfer_items:
            # Mostrar mensaje de error
            dialog = ctk.CTkToplevel(self)
            dialog.title("Error")
            dialog.geometry("400x150")
            dialog.resizable(False, False)
            dialog.grab_set()  # Modal
           
            # Centrar en pantalla
            dialog.update_idletasks()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (dialog.winfo_screenheight() // 2) - (height // 2)
            dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
           
            # Mensaje
            frame = ctk.CTkFrame(dialog)
            frame.pack(fill="both", expand=True, padx=20, pady=20)

            message_label = ctk.CTkLabel(
                frame,
                text="No hay productos disponibles para transferir. Solo se pueden transferir productos recibidos en almacén.",
                font=ctk.CTkFont(size=14),
                wraplength=360
            )
            message_label.pack(pady=(0, 20))
           
            # Botón cerrar
            close_button = ctk.CTkButton(
                frame,
                text="Cerrar",
                command=dialog.destroy
            )
            close_button.pack()
           
            return
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Transferir Producto")
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
            text="Transferir Producto",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20), anchor="w")
       
        # Producto a transferir
        product_label = ctk.CTkLabel(form_frame, text="Producto *", anchor="w")
        product_label.pack(anchor="w", pady=(10, 0))
       
        # Crear mapa de ID de almacén a nombre
        warehouse_map = {w.id: w.name for w in self.warehouses}

        # Lista de productos con su almacén actual
        product_options = []
        for item in transfer_items:
            warehouse_name = warehouse_map.get(item.warehouse_id, "Desconocido")
            option_text = f"{item.product_name} ({item.quantity} {item.unit}, en {warehouse_name})"
            product_options.append(option_text)
       
        product_var = ctk.StringVar(value=product_options[0])
        product_option = ctk.CTkOptionMenu(
            form_frame,
            values=product_options,
            variable=product_var,
            command=self.update_transfer_quantity
        )
        product_option.pack(fill="x", pady=(5, 0))
       
        # Variable para almacenar el elemento de stock seleccionado
        self.selected_stock_item = transfer_items[0]

        # Cantidad a transferir
        quantity_label = ctk.CTkLabel(form_frame, text=f"Cantidad a transferir (máx. {transfer_items[0].quantity} {transfer_items[0].unit}) *", anchor="w")
        quantity_label.pack(anchor="w", pady=(10, 0))
       
        quantity_entry = ctk.CTkEntry(form_frame)
        quantity_entry.insert(0, str(transfer_items[0].quantity))
        quantity_entry.pack(fill="x", pady=(5, 0))
       
        # Almacén destino
        target_label = ctk.CTkLabel(form_frame, text="Almacén Destino *", anchor="w")
        target_label.pack(anchor="w", pady=(10, 0))
       
        # Obtener lista de almacenes destino (excluir el actual)
        current_warehouse_id = transfer_items[0].warehouse_id
        target_warehouses = [w for w in self.warehouses if w.id != current_warehouse_id]
       
        target_options = [w.name for w in target_warehouses]
        target_var = ctk.StringVar(value=target_options[0] if target_options else "")
        target_option = ctk.CTkOptionMenu(
            form_frame,
            values=target_options,
            variable=target_var
        )
        target_option.pack(fill="x", pady=(5, 0))

        # Mensaje de error
        error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        error_label.pack(pady=(15, 0))
       
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

        # Función para actualizar etiqueta de cantidad cuando cambia el producto
        def update_transfer_quantity(selected_option):
            # Encontrar el elemento de stock seleccionado
            index = product_options.index(selected_option)
            self.selected_stock_item = transfer_items[index]
           
            # Actualizar etiqueta de cantidad
            quantity_label.configure(text=f"Cantidad a transferir (máx. {self.selected_stock_item.quantity} {self.selected_stock_item.unit}) *")
           
            # Actualizar valor por defecto en el campo
            quantity_entry.delete(0, "end")
            quantity_entry.insert(0, str(self.selected_stock_item.quantity))
           
            # Actualizar lista de almacenes destino
            current_warehouse_id = self.selected_stock_item.warehouse_id
            new_target_warehouses = [w for w in self.warehouses if w.id != current_warehouse_id]
           
            new_target_options = [w.name for w in new_target_warehouses]
            target_option.configure(values=new_target_options)
           
            if new_target_options:
                target_var.set(new_target_options[0])
        
         # Asignar la función de actualización
        self.update_transfer_quantity = update_transfer_quantity
       
        # Botón transferir
        def transfer_stock():
            # Validar campos
            quantity_str = quantity_entry.get().strip()
            target_warehouse_name = target_var.get()
           
            try:
                quantity = float(quantity_str)
                if quantity <= 0:
                    error_label.configure(text="La cantidad debe ser un número mayor que cero")
                    return
               
                if quantity > self.selected_stock_item.quantity:
                    error_label.configure(text=f"La cantidad no puede ser mayor que {self.selected_stock_item.quantity}")
                    return
            except ValueError:
                error_label.configure(text="La cantidad debe ser un número válido")
                return
           
            if not target_warehouse_name:
                error_label.configure(text="Debe seleccionar un almacén destino")
                return
            
            # Obtener ID del almacén destino
            target_warehouse_id = None
            for w in self.warehouses:
                if w.name == target_warehouse_name:
                    target_warehouse_id = w.id
                    break
           
            if not target_warehouse_id:
                error_label.configure(text="Almacén destino no encontrado")
                return
            
            # Realizar la transferencia
            result = self.stock_controller.transfer(
                self.selected_stock_item.id,
                target_warehouse_id,
                quantity
            )
           
            if result["success"]:
                dialog.destroy()
                self.load_stock()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al transferir el producto"))
       
        transfer_button = ctk.CTkButton(
            button_frame,
            text="Transferir",
            command=transfer_stock
        )
        transfer_button.pack(side="right")

    def confirm_delete(self, stock_id):
        """Muestra un diálogo de confirmación para eliminar un producto"""
        # Obtener datos del producto
        stock_item = self.stock_controller.get_by_id(stock_id)
        if not stock_item:
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
            text=f"¿Está seguro de eliminar el producto '{stock_item.product_name}'?\nEsta acción no se puede deshacer.",
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
        def delete_stock():
            result = self.stock_controller.delete(stock_id)
           
            if result["success"]:
                dialog.destroy()
                self.load_stock()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al eliminar el producto"))
       
        delete_button = ctk.CTkButton(
            button_frame,
            text="Eliminar",
            fg_color="#FF5252",
            command=delete_stock
        )
        delete_button.pack(side="right")
