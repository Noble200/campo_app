# views/user_management_frames.py
import customtkinter as ctk
from datetime import datetime
from controllers.user_controller import UserController

class UserManagementFrame(ctk.CTkFrame):
    def __init__(self, master, auth_controller):
        super().__init__(master)
        self.master = master
        self.auth_controller = auth_controller
        self.user_controller = UserController(auth_controller)
        
        # Obtener información del usuario actual
        self.current_user = self.auth_controller.get_current_user() or {}
        self.is_admin = self.current_user and self.current_user.get('role') == 'admin'
        
        # Lista de roles disponibles
        self.roles = ["basic", "manager", "fumigator"]
        if self.is_admin:
            self.roles.append("admin")
            
        # Lista de permisos posibles
        self.available_permissions = [
            "create_user",      # Permiso para crear usuarios
            "manage_users",     # Permiso para editar/eliminar usuarios
            "manage_permissions", # Permiso para asignar permisos
            "manage_fields",    # Permiso para gestionar campos
            "manage_warehouses", # Permiso para gestionar almacenes
            "manage_stock",     # Permiso para gestionar inventario
            "view_reports",     # Permiso para ver reportes
            "manage_fumigation", # Permiso para gestionar fumigación
            "is_fumigator"      # Permiso para identificar fumigadores
        ]
        
        # Lista de usuarios
        self.users = []
        
        # Crear interfaz
        self.create_interface()
        
        # Cargar datos
        self.load_users()
    
    def create_interface(self):
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Título
        self.grid_rowconfigure(1, weight=0)  # Botones y búsqueda
        self.grid_rowconfigure(2, weight=1)  # Tabla
        
        # Título
        self.title_label = ctk.CTkLabel(
            self, 
            text="Gestión de Usuarios",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Frame para botones y búsqueda
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Botón para agregar usuario (si tiene permiso)
        can_create_user = self.auth_controller.has_permission("create_user")
        if can_create_user:
            self.add_button = ctk.CTkButton(
                self.controls_frame,
                text="+ Agregar Usuario",
                command=self.show_add_user
            )
            self.add_button.pack(side="left", padx=(0, 10))
        
        # Botón para refrescar lista
        self.refresh_button = ctk.CTkButton(
            self.controls_frame,
            text="↻ Refrescar",
            command=self.load_users,
            fg_color="#4CAF50"
        )
        self.refresh_button.pack(side="left")
        
        # Checkbox para mostrar administradores (solo para admins)
        if self.is_admin:
            self.show_admins_var = ctk.BooleanVar(value=False)
            self.show_admins_checkbox = ctk.CTkCheckBox(
                self.controls_frame,
                text="Mostrar administradores",
                variable=self.show_admins_var,
                command=self.load_users
            )
            self.show_admins_checkbox.pack(side="left", padx=(20, 0))
        
        # Campo de búsqueda (lado derecho)
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.controls_frame,
            placeholder_text="Buscar usuario...",
            width=200,
            textvariable=self.search_var
        )
        self.search_entry.pack(side="right")
        
        # Botón de búsqueda
        self.search_button = ctk.CTkButton(
            self.controls_frame,
            text="🔍",
            width=30,
            command=self.search_users
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
        self.scrollable_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.scrollable_frame.grid_columnconfigure(4, weight=0)
        
        # Cabecera de la tabla
        headers = ["Usuario", "Rol", "Permisos", "Último Acceso", "Acciones"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.scrollable_frame,
                text=header,
                font=ctk.CTkFont(weight="bold")
            )
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Separador
        separator = ctk.CTkFrame(self.scrollable_frame, height=1, fg_color="gray")
        separator.grid(row=1, column=0, columnspan=5, sticky="ew", padx=5)
    
    def load_users(self):
        # Limpiar tabla existente (excepto cabecera y separador)
        for widget in self.scrollable_frame.winfo_children():
            if widget.grid_info()["row"] > 1:  # Solo eliminar filas de datos
                widget.destroy()
        
        # Obtener usuarios
        include_admins = self.is_admin and getattr(self, 'show_admins_var', ctk.BooleanVar(value=False)).get()
        self.users = self.user_controller.get_all(include_admins=include_admins)
        
        if not self.users:
            # Mostrar mensaje si no hay usuarios
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No hay usuarios registrados",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.grid(row=2, column=0, columnspan=5, padx=10, pady=20)
            return
        
        # Mostrar usuarios en la tabla
        for i, user in enumerate(self.users):
            row = i + 2  # +2 porque la fila 0 es la cabecera y la 1 es el separador
            
            # Nombre de usuario
            username_label = ctk.CTkLabel(self.scrollable_frame, text=user.get("username", ""))
            username_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            
            # Rol (con colores)
            role = user.get("role", "basic")
            role_colors = {
                "admin": "#FF5252",
                "manager": "#FFB74D",
                "basic": "#4CAF50",
                "fumigator": "#2196F3"
            }
            role_color = role_colors.get(role, "#4CAF50")
            
            role_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            role_frame.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            
            role_indicator = ctk.CTkFrame(role_frame, width=10, height=10, fg_color=role_color, corner_radius=5)
            role_indicator.pack(side="left", padx=(0, 5))
            
            role_label = ctk.CTkLabel(role_frame, text=role.capitalize())
            role_label.pack(side="left")
            
            # Permisos
            permissions = user.get("permissions", [])
            permissions_text = ", ".join(permissions) if permissions else "Ninguno"
            if "*" in permissions:
                permissions_text = "Todos los permisos"
                
            permissions_label = ctk.CTkLabel(self.scrollable_frame, text=permissions_text)
            permissions_label.grid(row=row, column=2, padx=10, pady=5, sticky="w")
            
            # Último acceso
            last_login = user.get("last_login")
            last_login_text = last_login.strftime("%d/%m/%Y %H:%M") if last_login else "Nunca"
            
            last_login_label = ctk.CTkLabel(self.scrollable_frame, text=last_login_text)
            last_login_label.grid(row=row, column=3, padx=10, pady=5, sticky="w")
            
            # Frame para botones de acción
            action_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            action_frame.grid(row=row, column=4, padx=10, pady=5)
            
            # Verificar si tiene permiso para gestionar usuarios
            if self.auth_controller.has_permission("manage_users"):
                # Botón editar
                edit_button = ctk.CTkButton(
                    action_frame,
                    text="Editar",
                    width=70,
                    height=25,
                    command=lambda uid=user["id"]: self.show_edit_user(uid)
                )
                edit_button.pack(side="left", padx=(0, 5))
                
                # Botón eliminar (no mostrar para el usuario actual)
                if user["id"] != self.current_user.get("id"):
                    delete_button = ctk.CTkButton(
                        action_frame,
                        text="Eliminar",
                        width=70,
                        height=25,
                        fg_color="#FF5252",
                        command=lambda uid=user["id"]: self.confirm_delete(uid)
                    )
                    delete_button.pack(side="left", padx=(0, 5))
                
                # Botón cambiar contraseña
                password_button = ctk.CTkButton(
                    action_frame,
                    text="Contraseña",
                    width=80,
                    height=25,
                    fg_color="#2196F3",
                    command=lambda uid=user["id"]: self.show_change_password(uid)
                )
                password_button.pack(side="left")
            
            # Agregar un separador después de cada fila
            if i < len(self.users) - 1:
                row_separator = ctk.CTkFrame(self.scrollable_frame, height=1, fg_color="gray70")
                row_separator.grid(row=row+1, column=0, columnspan=5, sticky="ew", padx=20)
    
    def search_users(self):
        search_text = self.search_var.get().lower().strip()
        
        # Si no hay texto de búsqueda, mostrar todos
        if not search_text:
            self.load_users()
            return
        
        # Filtrar usuarios
        filtered_users = [
            user for user in self.users 
            if (search_text in user.get("username", "").lower() or 
                search_text in user.get("role", "").lower())
        ]
        
        # Limpiar tabla existente (excepto cabecera y separador)
        for widget in self.scrollable_frame.winfo_children():
            if widget.grid_info()["row"] > 1:  # Solo eliminar filas de datos
                widget.destroy()
        
        if not filtered_users:
            # Mostrar mensaje si no hay resultados
            no_data_label = ctk.CTkLabel(
                self.scrollable_frame,
                text=f"No se encontraron usuarios con '{search_text}'",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.grid(row=2, column=0, columnspan=5, padx=10, pady=20)
            return
        
        # Mostrar usuarios filtrados (reutilizando el código)
        self.users = filtered_users
        self.load_users()
    
    def validate_min_permissions(self, permissions_vars, error_label):
        """Verifica que al menos un permiso esté seleccionado y muestra una indicación visual"""
        has_permission = any(var.get() for var in permissions_vars.values())
        
        if not has_permission:
            error_label.configure(text="El usuario debe tener como mínimo un permiso")
            return False
        else:
            error_label.configure(text="")
            return True
    
    def show_add_user(self):
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agregar Usuario")
        dialog.geometry("500x550")
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
            text="Nuevo Usuario",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20), anchor="w")
        
        # Campos básicos
        username_label = ctk.CTkLabel(form_scroll, text="Nombre de Usuario *", anchor="w")
        username_label.pack(anchor="w", pady=(10, 0))
        
        username_entry = ctk.CTkEntry(form_scroll)
        username_entry.pack(fill="x", pady=(5, 0))
        
        password_label = ctk.CTkLabel(form_scroll, text="Contraseña *", anchor="w")
        password_label.pack(anchor="w", pady=(10, 0))
        
        password_entry = ctk.CTkEntry(form_scroll, show="*")
        password_entry.pack(fill="x", pady=(5, 0))
        
        confirm_password_label = ctk.CTkLabel(form_scroll, text="Confirmar Contraseña *", anchor="w")
        confirm_password_label.pack(anchor="w", pady=(10, 0))
        
        confirm_password_entry = ctk.CTkEntry(form_scroll, show="*")
        confirm_password_entry.pack(fill="x", pady=(5, 0))
        
        # Rol (selector)
        role_label = ctk.CTkLabel(form_scroll, text="Rol *", anchor="w")
        role_label.pack(anchor="w", pady=(10, 0))
        
        role_var = ctk.StringVar(value=self.roles[0])
        role_option = ctk.CTkOptionMenu(
            form_scroll,
            values=self.roles,
            variable=role_var
        )
        role_option.pack(fill="x", pady=(5, 0))
        
        # Permisos (checkboxes)
        permissions_label = ctk.CTkLabel(form_scroll, text="Permisos", anchor="w", font=ctk.CTkFont(weight="bold"))
        permissions_label.pack(anchor="w", pady=(20, 5))
        
        # Agregar nota informativa sobre permisos mínimos
        permissions_info = ctk.CTkLabel(
            form_scroll,
            text="* El usuario debe tener como mínimo un permiso",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        permissions_info.pack(anchor="w", pady=(0, 5))
        
        # Mensaje de error
        error_label = ctk.CTkLabel(form_scroll, text="", text_color="red")
        error_label.pack(pady=(5, 0))
        
        permissions_vars = {}
        
        for permission in self.available_permissions:
            var = ctk.BooleanVar(value=False)
            checkbox = ctk.CTkCheckBox(
                form_scroll,
                text=permission,
                variable=var,
                command=lambda v=permissions_vars, e=error_label: self.validate_min_permissions(v, e)
            )
            checkbox.pack(anchor="w", pady=(5, 0))
            permissions_vars[permission] = var
        
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
        def save_user():
            # Validar campos requeridos
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()
            role = role_var.get()
            
            if not username:
                error_label.configure(text="El nombre de usuario es obligatorio")
                return
            
            if not password:
                error_label.configure(text="La contraseña es obligatoria")
                return
            
            if password != confirm_password:
                error_label.configure(text="Las contraseñas no coinciden")
                return
            
            # Recopilar permisos seleccionados
            permissions = []
            for permission, var in permissions_vars.items():
                if var.get():
                    permissions.append(permission)
            
            # Verificar que el usuario tenga al menos un permiso
            if not permissions:
                error_label.configure(text="El usuario debe tener como mínimo un permiso")
                return
            
            # Crear usuario
            result = self.user_controller.create(username, password, role, permissions)

            if result["success"]:
                dialog.destroy()
                self.load_users()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al guardar"))
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=save_user
        )
        save_button.pack(side="right")
    
    def show_edit_user(self, user_id):
        # Obtener datos del usuario
        user = self.user_controller.get_by_id(user_id)
        if not user:
            return
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar Usuario")
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
            text=f"Editar Usuario: {user.get('username')}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20), anchor="w")
        
        # Campos básicos
        username_label = ctk.CTkLabel(form_scroll, text="Nombre de Usuario *", anchor="w")
        username_label.pack(anchor="w", pady=(10, 0))
        
        username_entry = ctk.CTkEntry(form_scroll)
        username_entry.insert(0, user.get("username", ""))
        username_entry.pack(fill="x", pady=(5, 0))
        
        # Rol (selector)
        role_label = ctk.CTkLabel(form_scroll, text="Rol *", anchor="w")
        role_label.pack(anchor="w", pady=(10, 0))
       
        role_var = ctk.StringVar(value=user.get("role", self.roles[0]))
        role_option = ctk.CTkOptionMenu(
           form_scroll,
           values=self.roles,
           variable=role_var
        )
        role_option.pack(fill="x", pady=(5, 0))
       
        # Permisos (checkboxes)
        permissions_label = ctk.CTkLabel(form_scroll, text="Permisos", anchor="w", font=ctk.CTkFont(weight="bold"))
        permissions_label.pack(anchor="w", pady=(20, 5))
        
        # Agregar nota informativa sobre permisos mínimos
        permissions_info = ctk.CTkLabel(
            form_scroll,
            text="* El usuario debe tener como mínimo un permiso",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        permissions_info.pack(anchor="w", pady=(0, 5))
       
        # Mensaje de error
        error_label = ctk.CTkLabel(form_scroll, text="", text_color="red")
        error_label.pack(pady=(5, 0))
       
        user_permissions = user.get("permissions", [])
        
        # Si tiene permiso "*", marcar todos
        has_all_permissions = "*" in user_permissions
       
        permissions_vars = {}
        for permission in self.available_permissions:
            is_checked = has_all_permissions or permission in user_permissions
            var = ctk.BooleanVar(value=is_checked)
            checkbox = ctk.CTkCheckBox(
                form_scroll,
                text=permission,
                variable=var,
                command=lambda v=permissions_vars, e=error_label: self.validate_min_permissions(v, e)
            )
            checkbox.pack(anchor="w", pady=(5, 0))
            permissions_vars[permission] = var
       
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
        def update_user():
            # Validar campos requeridos
            username = username_entry.get().strip()
            role = role_var.get()
           
            if not username:
                error_label.configure(text="El nombre de usuario es obligatorio")
                return
           
            # Recopilar permisos seleccionados
            permissions = []
            for permission, var in permissions_vars.items():
                if var.get():
                    permissions.append(permission)
           
            # Verificar que el usuario tenga al menos un permiso
            if not permissions:
                error_label.configure(text="El usuario debe tener como mínimo un permiso")
                return
           
            # Datos a actualizar
            update_data = {
                "username": username,
                "role": role,
                "permissions": permissions
            }
           
            # Actualizar usuario
            result = self.user_controller.update(user["id"], update_data)
           
            if result["success"]:
                dialog.destroy()
                self.load_users()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al actualizar"))
       
        save_button = ctk.CTkButton(
           button_frame,
           text="Guardar",
           command=update_user
        )
        save_button.pack(side="right")
   
    def show_change_password(self, user_id):
       # Obtener datos del usuario
       user = self.user_controller.get_by_id(user_id)
       if not user:
           return
       
       # Crear ventana de diálogo
       dialog = ctk.CTkToplevel(self)
       dialog.title("Cambiar Contraseña")
       dialog.geometry("400x250")
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
           text=f"Cambiar contraseña: {user.get('username')}",
           font=ctk.CTkFont(size=16, weight="bold")
       )
       title_label.pack(pady=(0, 20), anchor="w")
       
       # Campos
       password_label = ctk.CTkLabel(form_frame, text="Nueva Contraseña *", anchor="w")
       password_label.pack(anchor="w", pady=(10, 0))
       
       password_entry = ctk.CTkEntry(form_frame, show="*")
       password_entry.pack(fill="x", pady=(5, 0))
       
       confirm_password_label = ctk.CTkLabel(form_frame, text="Confirmar Contraseña *", anchor="w")
       confirm_password_label.pack(anchor="w", pady=(10, 0))
       
       confirm_password_entry = ctk.CTkEntry(form_frame, show="*")
       confirm_password_entry.pack(fill="x", pady=(5, 0))
       
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
       
       # Botón guardar
       def change_password():
           # Validar campos
           password = password_entry.get()
           confirm_password = confirm_password_entry.get()
           
           if not password:
               error_label.configure(text="La contraseña es obligatoria")
               return
           
           if password != confirm_password:
               error_label.configure(text="Las contraseñas no coinciden")
               return
           
           # Cambiar contraseña
           result = self.user_controller.change_password(user["id"], password)
           
           if result["success"]:
               dialog.destroy()
           else:
               error_label.configure(text=result.get("error", "Error al cambiar la contraseña"))
       
       save_button = ctk.CTkButton(
           button_frame,
           text="Cambiar",
           command=change_password
       )
       save_button.pack(side="right")
   
    def confirm_delete(self, user_id):
        # Obtener datos del usuario
        user = self.user_controller.get_by_id(user_id)
        if not user:
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
            text=f"¿Está seguro de eliminar el usuario '{user.get('username')}'?\nEsta acción no se puede deshacer.",
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
        def delete_user():
            result = self.user_controller.delete(user_id)
            
            if result["success"]:
                dialog.destroy()
                self.load_users()  # Recargar lista
            else:
                error_label.configure(text=result.get("error", "Error al eliminar"))
        
        delete_button = ctk.CTkButton(
            button_frame,
            text="Eliminar",
            fg_color="#FF5252",
            command=delete_user
        )
        delete_button.pack(side="right")
