import os
import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from conexion import conectar
from tkinter import simpledialog
import re

class ClientManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrador de Clientes - Disfruleg")
        self.root.geometry("800x600")
        
        # Connect to database
        self.conn = conectar()
        self.cursor = self.conn.cursor(dictionary=True)
        
        # Load client types
        self.load_client_types()
        
        # Variables
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_clients)
        
        self.create_interface()
        self.load_clients()
        
    def load_client_types(self):
        """Load client types from database"""
        self.cursor.execute("SELECT id_tipo, nombre FROM tipo_cliente ORDER BY nombre")
        self.client_types = self.cursor.fetchall()
        
    def create_interface(self):
        """Create the user interface"""
        # Title
        title_frame = tk.Frame(self.root)
        title_frame.pack(fill="x", pady=10)
        
        tk.Label(title_frame, text="ADMINISTRADOR DE CLIENTES", font=("Arial", 18, "bold")).pack()
        
        # Search and actions frame
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill="x", pady=5, padx=10)
        
        # Search section
        search_frame = tk.Frame(action_frame)
        search_frame.pack(side="left", fill="x", expand=True)
        
        tk.Label(search_frame, text="Buscar:", font=("Arial", 12)).pack(side="left", padx=5)
        self.search_entry = tk.Entry(search_frame, width=30, textvariable=self.search_var)
        self.search_entry.pack(side="left", padx=5)
        
        # Buttons section
        buttons_frame = tk.Frame(action_frame)
        buttons_frame.pack(side="right")
        
        tk.Button(buttons_frame, text="Agregar Cliente", command=self.add_client_dialog, 
                  bg="#2196F3", fg="white", padx=10, pady=3).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Editar Cliente", command=self.edit_client_dialog, 
                  bg="#FFA500", fg="white", padx=10, pady=3).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Eliminar Cliente", command=self.delete_client, 
                  bg="#f44336", fg="white", padx=10, pady=3).pack(side="left", padx=5)
        
        # Clients table
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview for clients
        self.client_tree = ttk.Treeview(table_frame, 
                                      columns=("id", "nombre", "telefono", "correo", "tipo"),
                                      show="headings", 
                                      yscrollcommand=scrollbar.set)
        
        # Configure columns
        self.client_tree.heading("id", text="ID")
        self.client_tree.heading("nombre", text="Nombre")
        self.client_tree.heading("telefono", text="Teléfono")
        self.client_tree.heading("correo", text="Correo")
        self.client_tree.heading("tipo", text="Tipo de Cliente")
        
        self.client_tree.column("id", width=50)
        self.client_tree.column("nombre", width=200)
        self.client_tree.column("telefono", width=120)
        self.client_tree.column("correo", width=200)
        self.client_tree.column("tipo", width=150)
        
        self.client_tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.client_tree.yview)
        
        # Double-click to edit
        self.client_tree.bind("<Double-1>", lambda event: self.edit_client_dialog())
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Listo")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Add client type manager button
        type_button_frame = tk.Frame(self.root)
        type_button_frame.pack(fill="x", pady=5, padx=10)
        
        tk.Button(type_button_frame, text="Administrar Tipos de Cliente", 
                 command=self.manage_client_types,
                 bg="#673AB7", fg="white", padx=10, pady=3).pack(side="left")
    
    def load_clients(self):
        """Load clients from database"""
        # Clear existing items
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
            
        # Get clients
        self.cursor.execute("""
            SELECT c.id_cliente, c.nombre, c.telefono, c.correo, t.nombre as tipo_nombre, c.id_tipo
            FROM cliente c
            LEFT JOIN tipo_cliente t ON c.id_tipo = t.id_tipo
            ORDER BY c.nombre
        """)
        
        clients = self.cursor.fetchall()
        
        # Store all clients for reference and filtering
        self.all_clients = clients
        
        # Insert clients into treeview
        for client in clients:
            telefono = client.get('telefono', '') or '---'
            correo = client.get('correo', '') or '---'
            tipo = client.get('tipo_nombre', '') or '---'
            
            self.client_tree.insert("", "end", 
                                  values=(client["id_cliente"], 
                                         client["nombre"], 
                                         telefono,
                                         correo,
                                         tipo),
                                  tags=(str(client.get('id_tipo', '')),))
            
        self.status_var.set(f"Mostrando {len(clients)} clientes")
    
    def filter_clients(self, *args):
        """Filter clients based on search text"""
        search_text = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
        
        # Filter clients
        for client in self.all_clients:
            # Search in name, phone and email
            if (search_text in client["nombre"].lower() or 
                (client.get('telefono') and search_text in client.get('telefono').lower()) or
                (client.get('correo') and search_text in client.get('correo', '').lower()) or
                (client.get('tipo_nombre') and search_text in client.get('tipo_nombre', '').lower())):
                
                telefono = client.get('telefono', '') or '---'
                correo = client.get('correo', '') or '---'
                tipo = client.get('tipo_nombre', '') or '---'
                
                self.client_tree.insert("", "end", 
                                      values=(client["id_cliente"], 
                                             client["nombre"], 
                                             telefono,
                                             correo,
                                             tipo),
                                      tags=(str(client.get('id_tipo', '')),))
    
    def validate_email(self, email):
        """Validate email format"""
        if not email:
            return True  # Email is optional
        
        # Basic email validation pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    def add_client_dialog(self):
        """Open dialog to add a new client"""
        # Create popup
        popup = tk.Toplevel(self.root)
        popup.title("Agregar Nuevo Cliente")
        popup.geometry("500x450")
        popup.transient(self.root)
        popup.grab_set()
        
        # Center popup
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Title
        tk.Label(popup, text="Agregar Nuevo Cliente", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Form frame
        form_frame = tk.Frame(popup)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Name field (REQUIRED)
        name_frame = tk.Frame(form_frame)
        name_frame.pack(fill="x", pady=5)
        name_label = tk.Label(name_frame, text="Nombre: *", width=15, anchor="w", fg="#d32f2f")
        name_label.pack(side="left")
        name_entry = tk.Entry(name_frame, width=30)
        name_entry.pack(side="left", fill="x", expand=True)
        name_entry.focus_set()
        
        # Name validation label
        name_error_label = tk.Label(form_frame, text="", fg="#d32f2f", font=("Arial", 9))
        name_error_label.pack(fill="x")
        
        # Phone field (REQUIRED)
        phone_frame = tk.Frame(form_frame)
        phone_frame.pack(fill="x", pady=5)
        phone_label = tk.Label(phone_frame, text="Teléfono: *", width=15, anchor="w", fg="#d32f2f")
        phone_label.pack(side="left")
        phone_entry = tk.Entry(phone_frame, width=30)
        phone_entry.pack(side="left", fill="x", expand=True)
        
        # Phone validation label
        phone_error_label = tk.Label(form_frame, text="", fg="#d32f2f", font=("Arial", 9))
        phone_error_label.pack(fill="x")
        
        # Email field (OPTIONAL but validated)
        email_frame = tk.Frame(form_frame)
        email_frame.pack(fill="x", pady=5)
        tk.Label(email_frame, text="Correo:", width=15, anchor="w").pack(side="left")
        email_entry = tk.Entry(email_frame, width=30)
        email_entry.pack(side="left", fill="x", expand=True)
        
        # Email validation label
        email_error_label = tk.Label(form_frame, text="", fg="#d32f2f", font=("Arial", 9))
        email_error_label.pack(fill="x")
        
        # Type field (REQUIRED)
        type_frame = tk.Frame(form_frame)
        type_frame.pack(fill="x", pady=5)
        type_label = tk.Label(type_frame, text="Tipo de Cliente: *", width=15, anchor="w", fg="#d32f2f")
        type_label.pack(side="left")
        
        # Combobox for client types
        type_values = [(t['id_tipo'], t['nombre']) for t in self.client_types]
        type_names = [t[1] for t in type_values]
        
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(type_frame, textvariable=type_var, values=type_names, state="readonly")
        type_combo.pack(side="left", fill="x", expand=True)
        if type_names:
            type_combo.current(0)
        
        # Type validation label
        type_error_label = tk.Label(form_frame, text="", fg="#d32f2f", font=("Arial", 9))
        type_error_label.pack(fill="x")
        
        # Required fields note
        required_note = tk.Label(form_frame, text="* Campos obligatorios", font=("Arial", 9), fg="#666")
        required_note.pack(pady=(10, 0))
        
        # Real-time validation bindings
        def validate_name_real_time(*args):
            name = name_entry.get().strip()
            if not name:
                name_error_label.config(text="")
            elif name:
                name_error_label.config(text="")
        
        def validate_phone_real_time(*args):
            phone = phone_entry.get().strip()
            if not phone:
                phone_error_label.config(text="")
            elif phone:
                phone_error_label.config(text="")
        
        def validate_email_real_time(*args):
            email = email_entry.get().strip()
            if not email:
                email_error_label.config(text="")
            elif email and not self.validate_email(email):
                email_error_label.config(text="Formato de correo inválido (debe contener @)")
            else:
                email_error_label.config(text="")
        
        # Bind validation events
        name_entry.bind('<KeyRelease>', validate_name_real_time)
        phone_entry.bind('<KeyRelease>', validate_phone_real_time)
        email_entry.bind('<KeyRelease>', validate_email_real_time)
        
        # Buttons
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=15)
        
        def save_client_with_validation():
            # Clear previous error messages
            name_error_label.config(text="")
            phone_error_label.config(text="")
            email_error_label.config(text="")
            type_error_label.config(text="")
            
            # Get and validate data
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            type_name = type_var.get().strip()
            
            is_valid = True
            
            # Validate name (required)
            if not name:
                name_error_label.config(text="El nombre es obligatorio")
                is_valid = False
            
            # Validate phone (required)
            if not phone:
                phone_error_label.config(text="El teléfono es obligatorio")
                is_valid = False
            
            # Validate email (optional but must be valid if provided)
            if email and not self.validate_email(email):
                email_error_label.config(text="Formato de correo inválido (debe contener @)")
                is_valid = False
            
            # Validate type (required)
            if not type_name:
                type_error_label.config(text="Debe seleccionar un tipo de cliente")
                is_valid = False
            
            if is_valid:
                self.save_client(popup, name, phone, email, type_name, type_values, None)
        
        tk.Button(button_frame, text="Guardar", 
                 command=save_client_with_validation, 
                 bg="#4CAF50", fg="white", padx=10, pady=5).pack(side="left", padx=10)
        
        tk.Button(button_frame, text="Cancelar", 
                 command=popup.destroy, 
                 bg="#f44336", fg="white", padx=10, pady=5).pack(side="left", padx=10)
    
    def edit_client_dialog(self):
        """Open dialog to edit an existing client"""
        # Get selected client
        selected_item = self.client_tree.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor selecciona un cliente para editar")
            return
        
        # Get client data
        values = self.client_tree.item(selected_item, "values")
        client_id = values[0]
        
        # Get client details from database
        self.cursor.execute("""
            SELECT c.id_cliente, c.nombre, c.telefono, c.correo, c.id_tipo
            FROM cliente c
            WHERE c.id_cliente = %s
        """, (client_id,))
        
        client = self.cursor.fetchone()
        if not client:
            messagebox.showerror("Error", "Cliente no encontrado")
            return
        
        # Create popup
        popup = tk.Toplevel(self.root)
        popup.title("Editar Cliente")
        popup.geometry("500x450")
        popup.transient(self.root)
        popup.grab_set()
        
        # Center popup
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Title
        tk.Label(popup, text="Editar Cliente", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Form frame
        form_frame = tk.Frame(popup)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Name field (REQUIRED)
        name_frame = tk.Frame(form_frame)
        name_frame.pack(fill="x", pady=5)
        name_label = tk.Label(name_frame, text="Nombre: *", width=15, anchor="w", fg="#d32f2f")
        name_label.pack(side="left")
        name_entry = tk.Entry(name_frame, width=30)
        name_entry.pack(side="left", fill="x", expand=True)
        name_entry.insert(0, client["nombre"])
        name_entry.focus_set()
        
        # Name validation label
        name_error_label = tk.Label(form_frame, text="", fg="#d32f2f", font=("Arial", 9))
        name_error_label.pack(fill="x")
        
        # Phone field (REQUIRED)
        phone_frame = tk.Frame(form_frame)
        phone_frame.pack(fill="x", pady=5)
        phone_label = tk.Label(phone_frame, text="Teléfono: *", width=15, anchor="w", fg="#d32f2f")
        phone_label.pack(side="left")
        phone_entry = tk.Entry(phone_frame, width=30)
        phone_entry.pack(side="left", fill="x", expand=True)
        if client.get("telefono"):
            phone_entry.insert(0, client["telefono"])
        
        # Phone validation label
        phone_error_label = tk.Label(form_frame, text="", fg="#d32f2f", font=("Arial", 9))
        phone_error_label.pack(fill="x")
        
        # Email field (OPTIONAL but validated)
        email_frame = tk.Frame(form_frame)
        email_frame.pack(fill="x", pady=5)
        tk.Label(email_frame, text="Correo:", width=15, anchor="w").pack(side="left")
        email_entry = tk.Entry(email_frame, width=30)
        email_entry.pack(side="left", fill="x", expand=True)
        if client.get("correo"):
            email_entry.insert(0, client["correo"])
        
        # Email validation label
        email_error_label = tk.Label(form_frame, text="", fg="#d32f2f", font=("Arial", 9))
        email_error_label.pack(fill="x")
        
        # Type field (REQUIRED)
        type_frame = tk.Frame(form_frame)
        type_frame.pack(fill="x", pady=5)
        type_label = tk.Label(type_frame, text="Tipo de Cliente: *", width=15, anchor="w", fg="#d32f2f")
        type_label.pack(side="left")
        
        # Combobox for client types
        type_values = [(t['id_tipo'], t['nombre']) for t in self.client_types]
        type_names = [t[1] for t in type_values]
        
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(type_frame, textvariable=type_var, values=type_names, state="readonly")
        type_combo.pack(side="left", fill="x", expand=True)
        
        # Set current client type
        current_type_index = 0
        for i, (id_tipo, _) in enumerate(type_values):
            if id_tipo == client["id_tipo"]:
                current_type_index = i
                break
                
        if type_names:
            type_combo.current(current_type_index)
        
        # Type validation label
        type_error_label = tk.Label(form_frame, text="", fg="#d32f2f", font=("Arial", 9))
        type_error_label.pack(fill="x")
        
        # Required fields note
        required_note = tk.Label(form_frame, text="* Campos obligatorios", font=("Arial", 9), fg="#666")
        required_note.pack(pady=(10, 0))
        
        # Real-time validation bindings
        def validate_name_real_time(*args):
            name = name_entry.get().strip()
            if not name:
                name_error_label.config(text="")
            elif name:
                name_error_label.config(text="")
        
        def validate_phone_real_time(*args):
            phone = phone_entry.get().strip()
            if not phone:
                phone_error_label.config(text="")
            elif phone:
                phone_error_label.config(text="")
        
        def validate_email_real_time(*args):
            email = email_entry.get().strip()
            if not email:
                email_error_label.config(text="")
            elif email and not self.validate_email(email):
                email_error_label.config(text="Formato de correo inválido (debe contener @)")
            else:
                email_error_label.config(text="")
        
        # Bind validation events
        name_entry.bind('<KeyRelease>', validate_name_real_time)
        phone_entry.bind('<KeyRelease>', validate_phone_real_time)
        email_entry.bind('<KeyRelease>', validate_email_real_time)
        
        # Buttons
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=15)
        
        def save_client_with_validation():
            # Clear previous error messages
            name_error_label.config(text="")
            phone_error_label.config(text="")
            email_error_label.config(text="")
            type_error_label.config(text="")
            
            # Get and validate data
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            type_name = type_var.get().strip()
            
            is_valid = True
            
            # Validate name (required)
            if not name:
                name_error_label.config(text="El nombre es obligatorio")
                is_valid = False
            
            # Validate phone (required)
            if not phone:
                phone_error_label.config(text="El teléfono es obligatorio")
                is_valid = False
            
            # Validate email (optional but must be valid if provided)
            if email and not self.validate_email(email):
                email_error_label.config(text="Formato de correo inválido (debe contener @)")
                is_valid = False
            
            # Validate type (required)
            if not type_name:
                type_error_label.config(text="Debe seleccionar un tipo de cliente")
                is_valid = False
            
            if is_valid:
                self.save_client(popup, name, phone, email, type_name, type_values, client_id)
        
        tk.Button(button_frame, text="Guardar Cambios", 
                 command=save_client_with_validation, 
                 bg="#4CAF50", fg="white", padx=10, pady=5).pack(side="left", padx=10)
        
        tk.Button(button_frame, text="Cancelar", 
                 command=popup.destroy, 
                 bg="#f44336", fg="white", padx=10, pady=5).pack(side="left", padx=10)
    
    def save_client(self, popup, name, phone, email, type_name, type_values, client_id=None):
        """Save client to database (add new or update existing)"""
        # Get type_id from selected type_name
        type_id = None
        for id_tipo, nombre in type_values:
            if nombre == type_name:
                type_id = id_tipo
                break
                
        if type_id is None:
            messagebox.showerror("Error", "Tipo de cliente no válido")
            return
        
        try:
            if client_id:  # Update existing client
                self.cursor.execute("""
                    UPDATE cliente 
                    SET nombre = %s, telefono = %s, correo = %s, id_tipo = %s
                    WHERE id_cliente = %s
                """, (name, phone, email if email else None, type_id, client_id))
                
                action = "actualizado"
            else:  # Add new client
                self.cursor.execute("""
                    INSERT INTO cliente (nombre, telefono, correo, id_tipo)
                    VALUES (%s, %s, %s, %s)
                """, (name, phone, email if email else None, type_id))
                
                action = "agregado"
            
            self.conn.commit()
            self.status_var.set(f"Cliente {action} correctamente")
            messagebox.showinfo("Éxito", f"Cliente {action} correctamente")
            popup.destroy()
            self.load_clients()
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al guardar cliente: {str(e)}")
    
    def delete_client(self):
        """Delete selected client"""
        # Get selected client
        selected_item = self.client_tree.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor selecciona un cliente para eliminar")
            return
        
        # Get client data
        values = self.client_tree.item(selected_item, "values")
        client_id = values[0]
        client_name = values[1]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirmar Eliminación", 
                                 f"¿Estás seguro de eliminar el cliente '{client_name}'?\n\n"
                                 f"Esta acción eliminará todas las facturas asociadas a este cliente."):
            return
        
        # Check if client has invoices
        self.cursor.execute("SELECT COUNT(*) as count FROM factura WHERE id_cliente = %s", (client_id,))
        result = self.cursor.fetchone()
        
        if result and result['count'] > 0:
            if not messagebox.askyesno("Advertencia", 
                                     f"El cliente '{client_name}' tiene {result['count']} facturas asociadas. "
                                     f"Si eliminas este cliente, esas facturas también se eliminarán.\n\n"
                                     f"¿Estás seguro de continuar?"):
                return
        
        try:
            # Start transaction
            self.conn.autocommit = False
            
            # First delete invoice details for all client invoices
            self.cursor.execute("""
                DELETE df FROM detalle_factura df
                JOIN factura f ON df.id_factura = f.id_factura
                WHERE f.id_cliente = %s
            """, (client_id,))
            
            # Then delete invoices
            self.cursor.execute("DELETE FROM factura WHERE id_cliente = %s", (client_id,))
            
            # Finally delete client
            self.cursor.execute("DELETE FROM cliente WHERE id_cliente = %s", (client_id,))
            
            # Commit changes
            self.conn.commit()
            self.conn.autocommit = True
            
            self.status_var.set(f"Cliente '{client_name}' eliminado correctamente")
            messagebox.showinfo("Éxito", f"Cliente '{client_name}' eliminado correctamente")
            self.load_clients()
            
        except Exception as e:
            self.conn.rollback()
            self.conn.autocommit = True
            messagebox.showerror("Error", f"Error al eliminar cliente: {str(e)}")
    
    def manage_client_types(self):
        """Manage client types"""
        # Create popup
        popup = tk.Toplevel(self.root)
        popup.title("Administrar Tipos de Cliente")
        popup.geometry("400x400")
        popup.transient(self.root)
        popup.grab_set()
        
        # Center popup
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Title
        tk.Label(popup, text="Tipos de Cliente", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Listbox for types
        frame = tk.Frame(popup)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        type_listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Arial", 12))
        type_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=type_listbox.yview)
        
        # Load types into listbox
        for type_info in self.client_types:
            type_listbox.insert(tk.END, f"{type_info['nombre']} (ID: {type_info['id_tipo']})")
        
        # Buttons frame
        button_frame = tk.Frame(popup)
        button_frame.pack(fill="x", pady=10, padx=20)
        
        tk.Button(button_frame, text="Agregar Tipo", 
                 command=lambda: self.add_client_type(popup, type_listbox), 
                 bg="#4CAF50", fg="white", padx=10, pady=5).pack(side="left", padx=5)
                 
        tk.Button(button_frame, text="Editar Tipo", 
                 command=lambda: self.edit_client_type(popup, type_listbox), 
                 bg="#FFA500", fg="white", padx=10, pady=5).pack(side="left", padx=5)
                 
        tk.Button(button_frame, text="Eliminar Tipo", 
                 command=lambda: self.delete_client_type(popup, type_listbox), 
                 bg="#f44336", fg="white", padx=10, pady=5).pack(side="left", padx=5)
                 
        tk.Button(button_frame, text="Cerrar", 
                 command=popup.destroy, 
                 bg="#607D8B", fg="white", padx=10, pady=5).pack(side="right", padx=5)
    
    def add_client_type(self, parent_popup, type_listbox):
        """Add a new client type"""
        # Ask for new type name
        type_name = simpledialog.askstring("Nuevo Tipo", "Nombre del nuevo tipo de cliente:", parent=parent_popup)
        
        if not type_name or not type_name.strip():
            return
            
        try:
            # Insert new type
            self.cursor.execute("INSERT INTO tipo_cliente (nombre) VALUES (%s)", (type_name,))
            self.conn.commit()
            
            # Reload client types
            self.load_client_types()
            
            # Update listbox
            type_listbox.delete(0, tk.END)
            for type_info in self.client_types:
                type_listbox.insert(tk.END, f"{type_info['nombre']} (ID: {type_info['id_tipo']})")
                
            self.status_var.set(f"Tipo de cliente '{type_name}' agregado correctamente")
                
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al agregar tipo de cliente: {str(e)}")
    
    def edit_client_type(self, parent_popup, type_listbox):
        """Edit selected client type"""
        # Get selected type
        selection = type_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un tipo de cliente para editar", parent=parent_popup)
            return
            
        # Get type info
        selected_index = selection[0]
        selected_type = self.client_types[selected_index]
        
        # Ask for new name
        new_name = simpledialog.askstring("Editar Tipo", "Nuevo nombre:", 
                                       initialvalue=selected_type['nombre'], 
                                       parent=parent_popup)
        
        if not new_name or not new_name.strip():
            return
            
        try:
            # Update type name
            self.cursor.execute("UPDATE tipo_cliente SET nombre = %s WHERE id_tipo = %s", 
                             (new_name, selected_type['id_tipo']))
            self.conn.commit()
            
            # Reload client types
            self.load_client_types()
            
            # Update listbox
            type_listbox.delete(0, tk.END)
            for type_info in self.client_types:
                type_listbox.insert(tk.END, f"{type_info['nombre']} (ID: {type_info['id_tipo']})")
                
            self.status_var.set(f"Tipo de cliente actualizado correctamente")
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al actualizar tipo de cliente: {str(e)}")
    
    def delete_client_type(self, parent_popup, type_listbox):
        """Delete selected client type"""
        # Get selected type
        selection = type_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un tipo de cliente para eliminar", parent=parent_popup)
            return
            
        # Get type info
        selected_index = selection[0]
        selected_type = self.client_types[selected_index]
        
        # Check if type is in use
        self.cursor.execute("SELECT COUNT(*) as count FROM cliente WHERE id_tipo = %s", (selected_type['id_tipo'],))
        clients_count = self.cursor.fetchone()['count']
        
        self.cursor.execute("SELECT COUNT(*) as count FROM precio WHERE id_tipo = %s", (selected_type['id_tipo'],))
        prices_count = self.cursor.fetchone()['count']
        
        if clients_count > 0 or prices_count > 0:
            messagebox.showerror("Error", 
                              f"No se puede eliminar este tipo de cliente porque está en uso:\n"
                              f"- {clients_count} clientes\n"
                              f"- {prices_count} precios\n\n"
                              f"Debes reasignar o eliminar estos registros primero.", 
                              parent=parent_popup)
            return
            
        # Confirm deletion
        if not messagebox.askyesno("Confirmar Eliminación", 
                                 f"¿Estás seguro de eliminar el tipo de cliente '{selected_type['nombre']}'?",
                                 parent=parent_popup):
            return
            
        try:
            # Delete type
            self.cursor.execute("DELETE FROM tipo_cliente WHERE id_tipo = %s", (selected_type['id_tipo'],))
            self.conn.commit()
            
            # Reload client types
            self.load_client_types()
            
            # Update listbox
            type_listbox.delete(0, tk.END)
            for type_info in self.client_types:
                type_listbox.insert(tk.END, f"{type_info['nombre']} (ID: {type_info['id_tipo']})")
                
            self.status_var.set(f"Tipo de cliente eliminado correctamente")
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al eliminar tipo de cliente: {str(e)}")
    
    def on_closing(self):
        """Clean up and close connection when closing the app"""
        try:
            self.conn.close()
        except:
            pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientManagerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()