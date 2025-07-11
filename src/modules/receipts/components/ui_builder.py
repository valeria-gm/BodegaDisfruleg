import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict, Any

class UIBuilder:
    """Handles UI component creation for receipt application"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
    
    def create_group_selection(self, parent: tk.Widget, group_names: List[str], 
                              group_var: tk.StringVar, on_group_change: Callable,
                              save_to_db_var: tk.BooleanVar) -> ttk.Combobox:
        """Create group selection section"""
        grupo_frame = tk.LabelFrame(parent, text="1. Seleccionar Grupo", font=("Arial", 12, "bold"))
        grupo_frame.pack(fill="x", pady=(0, 10))
        
        frame_interno = tk.Frame(grupo_frame)
        frame_interno.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_interno, text="Grupo:", font=("Arial", 12)).pack(side="left", padx=5)
        
        grupo_combo = ttk.Combobox(frame_interno, textvariable=group_var, 
                                   values=group_names, state="readonly", width=40)
        grupo_combo.pack(side="left", padx=5)
        grupo_combo.bind("<<ComboboxSelected>>", on_group_change)
        
        # Checkbox for auto-save
        tk.Checkbutton(frame_interno, 
                      text="Guardar en base de datos", 
                      variable=save_to_db_var,
                      font=("Arial", 10)).pack(side="right", padx=20)
        
        return grupo_combo
    
    def create_client_section(self, parent: tk.Widget, client_names: List[str], 
                             client_var: tk.StringVar, on_client_change: Callable) -> ttk.Combobox:
        """Create client selection section"""
        cliente_frame = tk.LabelFrame(parent, text="2. Seleccionar Restaurante/Cliente", font=("Arial", 12, "bold"))
        cliente_frame.pack(fill="x", pady=(0, 10))
        
        frame_interno = tk.Frame(cliente_frame)
        frame_interno.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_interno, text="Cliente:", font=("Arial", 12)).pack(side="left", padx=5)
        
        cliente_combo = ttk.Combobox(frame_interno, textvariable=client_var, 
                                   values=client_names, state="disabled", width=40)
        cliente_combo.pack(side="left", padx=5)
        cliente_combo.bind("<<ComboboxSelected>>", on_client_change)
        
        # Info label for client type
        type_label = tk.Label(frame_interno, text="(Seleccione un grupo primero)", 
                             font=("Arial", 9), fg="gray")
        type_label.pack(side="left", padx=10)
        
        # Store reference to type label for updates
        cliente_combo.type_label = type_label
        
        return cliente_combo
    
    def create_section_selection(self, parent: tk.Widget, on_sectioning_toggle: Callable, 
                               on_manage_sections: Callable) -> tk.Frame:
        """Create section selection area"""
        section_frame = tk.LabelFrame(parent, text="3. Configuración de Secciones", 
                                    font=("Arial", 12, "bold"))
        section_frame.pack(fill="x", pady=(0, 10))
        
        # Info label
        info_label = tk.Label(section_frame, text="(Seleccione un grupo y cliente primero)", 
                            font=("Arial", 9), fg="gray")
        info_label.pack(pady=5)
        
        # Inner frame for controls
        inner_frame = tk.Frame(section_frame)
        inner_frame.pack(fill="x", padx=10, pady=10)
        
        # Sectioning toggle
        sectioning_var = tk.BooleanVar(value=False)
        sectioning_check = tk.Checkbutton(inner_frame, text="Habilitar Secciones de Factura", 
                                        variable=sectioning_var, command=on_sectioning_toggle,
                                        font=("Arial", 10), state="disabled")
        sectioning_check.pack(side="left", padx=5)
        
        # Section management button (initially hidden)
        section_mgmt_button = tk.Button(inner_frame, text="Gestionar Secciones", 
                                      command=on_manage_sections, bg="#9C27B0", fg="white")
        
        # Store references for later manipulation
        section_frame.sectioning_var = sectioning_var
        section_frame.sectioning_check = sectioning_check
        section_frame.section_mgmt_button = section_mgmt_button
        section_frame.inner_frame = inner_frame
        section_frame.info_label = info_label
        
        return section_frame
    
    def enable_section_controls(self, section_frame: tk.Frame):
        """Enable section controls after client selection"""
        section_frame.sectioning_check.configure(state="normal")
        section_frame.info_label.configure(text="", fg="black")
    
    def enable_client_selection(self, client_combo: ttk.Combobox):
        """Enable client selection after group is selected"""
        client_combo.configure(state="readonly")
        client_combo.type_label.configure(text="(Seleccione un cliente)", fg="gray")
    
    def disable_client_selection(self, client_combo: ttk.Combobox):
        """Disable client selection when no group is selected"""
        client_combo.configure(state="disabled")
        client_combo.type_label.configure(text="(Seleccione un grupo primero)", fg="gray")
    
    def update_client_type_display(self, client_combo: ttk.Combobox, client_type: str, discount: float):
        """Update the client type display"""
        if discount > 0:
            type_text = f"Tipo: {client_type} ({discount}% descuento)"
        else:
            type_text = f"Tipo: {client_type}"
        client_combo.type_label.configure(text=type_text, fg="blue")
    
    def show_section_management_button(self, section_frame: tk.Frame):
        """Show section management button"""
        section_frame.section_mgmt_button.pack(side="left", padx=10)
    
    def hide_section_management_button(self, section_frame: tk.Frame):
        """Hide section management button"""
        section_frame.section_mgmt_button.pack_forget()
    
    def create_products_section(self, parent: tk.Widget, search_var: tk.StringVar,
                               on_search_change: Callable, on_clear_search: Callable,
                               on_product_double_click: Callable) -> ttk.Treeview:
        """Create products search and selection section"""
        productos_frame = tk.LabelFrame(parent, text="4. Buscar y Seleccionar Productos", 
                                      font=("Arial", 12, "bold"))
        productos_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Search frame
        search_frame = tk.Frame(productos_frame)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(search_frame, text="Buscar:", font=("Arial", 11)).pack(side="left", padx=5)
        
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30, font=("Arial", 11))
        search_entry.pack(side="left", padx=5)
        search_var.trace("w", on_search_change)
        
        tk.Button(search_frame, text="Limpiar Búsqueda", 
                 command=on_clear_search, bg="#ff9800", fg="white").pack(side="left", padx=10)
        
        # Products table
        tabla_frame = tk.Frame(productos_frame)
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        scrollbar_prod = tk.Scrollbar(tabla_frame)
        scrollbar_prod.pack(side="right", fill="y")
        
        productos_tree = ttk.Treeview(tabla_frame, 
                                    columns=("nombre", "unidad", "precio", "accion"),
                                    show="headings", 
                                    yscrollcommand=scrollbar_prod.set,
                                    height=8)
        
        productos_tree.heading("nombre", text="Producto")
        productos_tree.heading("unidad", text="Unidad")
        productos_tree.heading("precio", text="Precio")
        productos_tree.heading("accion", text="Cantidad")
        
        productos_tree.column("nombre", width=250)
        productos_tree.column("unidad", width=80)
        productos_tree.column("precio", width=100)
        productos_tree.column("accion", width=150)
        
        productos_tree.pack(side="left", fill="both", expand=True)
        scrollbar_prod.config(command=productos_tree.yview)
        
        productos_tree.bind("<Double-1>", on_product_double_click)
        
        return productos_tree
    
    def create_cart_section(self, parent: tk.Widget, on_cart_double_click: Callable,
                           on_remove_item: Callable, on_clear_cart: Callable) -> tuple:
        """Create shopping cart section"""
        carrito_frame = tk.LabelFrame(parent, text="5. Carrito de Compras", font=("Arial", 12, "bold"))
        carrito_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Cart table
        tabla_carrito_frame = tk.Frame(carrito_frame)
        tabla_carrito_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar_carrito = tk.Scrollbar(tabla_carrito_frame)
        scrollbar_carrito.pack(side="right", fill="y")
        
        carrito_tree = ttk.Treeview(
            tabla_carrito_frame,
            columns=("producto", "cantidad", "unidad", "precio_base", "descuento", "precio_final", "subtotal"),
            show="headings",
            yscrollcommand=scrollbar_carrito.set,
            height=6
        )
        
        # Configure headers
        carrito_tree.heading("producto", text="Producto")
        carrito_tree.heading("cantidad", text="Cantidad")
        carrito_tree.heading("unidad", text="Unidad")
        carrito_tree.heading("precio_base", text="Precio Base")
        carrito_tree.heading("descuento", text="Descuento")
        carrito_tree.heading("precio_final", text="Precio Final")
        carrito_tree.heading("subtotal", text="Subtotal")
        
        # Configure column widths
        carrito_tree.column("producto", width=200)
        carrito_tree.column("cantidad", width=80)
        carrito_tree.column("unidad", width=80)
        carrito_tree.column("precio_base", width=100)
        carrito_tree.column("descuento", width=80)
        carrito_tree.column("precio_final", width=100)
        carrito_tree.column("subtotal", width=100)
        
        carrito_tree.pack(side="left", fill="both", expand=True)
        scrollbar_carrito.config(command=carrito_tree.yview)
        
        carrito_tree.bind("<Double-1>", on_cart_double_click)
        
        # Total frame
        total_frame = tk.Frame(carrito_frame)
        total_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        total_var = tk.StringVar(value="Total: $0.00")
        total_label = tk.Label(total_frame, textvariable=total_var, 
                              font=("Arial", 14, "bold"), fg="#2196F3")
        total_label.pack(side="right", padx=10)
        
        # Cart buttons
        botones_carrito = tk.Frame(total_frame)
        botones_carrito.pack(side="left")
        
        tk.Button(botones_carrito, text="Eliminar Seleccionado", 
                 command=on_remove_item, bg="#f44336", fg="white").pack(side="left", padx=5)
        tk.Button(botones_carrito, text="Limpiar Carrito", 
                 command=on_clear_cart, bg="#ff5722", fg="white").pack(side="left", padx=5)
        
        return carrito_tree, total_var
    
    def add_section_management_button(self, parent_frame: tk.Widget, on_manage_sections: Callable) -> None:
        """Add section management button to existing frame"""
        tk.Button(parent_frame, text="Gestionar Secciones", 
                 command=on_manage_sections, bg="#9C27B0", fg="white").pack(side="left", padx=5)
    
    def create_actions_section(self, parent: tk.Widget, on_generate_receipt: Callable,
                              on_preview: Callable) -> None:
        """Create actions section with buttons"""
        acciones_frame = tk.Frame(parent)
        acciones_frame.pack(fill="x", pady=10)
        
        tk.Button(acciones_frame, text="Generar Recibo", command=on_generate_receipt,
                  bg="#4CAF50", fg="white", padx=20, pady=8, 
                  font=("Arial", 12, "bold")).pack(side="right", padx=5)
        
        tk.Button(acciones_frame, text="Vista Previa", command=on_preview,
                  bg="#2196F3", fg="white", padx=15, pady=8, 
                  font=("Arial", 11)).pack(side="right", padx=5)
    
    def create_status_bar(self, parent: tk.Widget, status_var: tk.StringVar) -> None:
        """Create status bar"""
        status_bar = tk.Label(parent, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_preview_window(self, parent: tk.Widget, content: str) -> None:
        """Create preview window for receipt"""
        preview = tk.Toplevel(parent)
        preview.title("Vista Previa del Recibo")
        preview.geometry("600x500")
        
        text_widget = tk.Text(preview, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", content)
        text_widget.config(state="disabled")
    
    def populate_treeview(self, tree: ttk.Treeview, data: List[Dict[str, Any]], 
                         id_key: str = 'id') -> None:
        """Populate treeview with data"""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        # Add new items
        for item_data in data:
            values = tuple(item_data[col] for col in tree["columns"] if col in item_data)
            tree.insert("", "end", values=values, tags=(str(item_data.get(id_key, "")),))
    
    def populate_combobox(self, combo: ttk.Combobox, values: List[str], clear_selection: bool = True):
        """Populate combobox with values"""
        combo['values'] = values
        if clear_selection:
            combo.set('')
    
    def create_section_management_dialog(self, parent: tk.Widget, get_sections: Callable,
                                       on_add_section: Callable, on_remove_section: Callable,
                                       on_rename_section: Callable, on_refresh: Callable = None) -> None:
        """Create section management dialog"""
        dialog = tk.Toplevel(parent)
        dialog.title("Gestionar Secciones")
        dialog.geometry("400x300")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (200)
        y = (dialog.winfo_screenheight() // 2) - (150)
        dialog.geometry(f"+{x}+{y}")
        
        # Sections list
        tk.Label(dialog, text="Secciones:", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Listbox frame
        listbox_frame = tk.Frame(dialog)
        listbox_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")
        
        sections_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set)
        sections_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=sections_listbox.yview)
        
        # Populate listbox
        def refresh_sections():
            sections_listbox.delete(0, tk.END)
            # Get updated sections from the callback
            sections = get_sections()
            if hasattr(sections, 'items'):
                for section_id, section in sections.items():
                    item_count = getattr(section, 'item_count', 0)
                    sections_listbox.insert(tk.END, f"{section.name} ({item_count} items)")
        
        refresh_sections()
        
        # Buttons frame
        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(pady=10)
        
        def add_section():
            name = tk.simpledialog.askstring("Nueva Sección", "Nombre de la sección:")
            if name and name.strip():
                on_add_section(name.strip())
                refresh_sections()
                if on_refresh:
                    on_refresh()
        
        def remove_section():
            selection = sections_listbox.curselection()
            if selection:
                idx = selection[0]
                section_text = sections_listbox.get(idx)
                section_name = section_text.split(' (')[0]
                
                # Find section ID by name
                sections = get_sections()
                section_id = None
                for sid, section in sections.items():
                    if section.name == section_name:
                        section_id = sid
                        break
                
                if section_id and on_remove_section(section_id):
                    refresh_sections()
                    if on_refresh:
                        on_refresh()
        
        def rename_section():
            selection = sections_listbox.curselection()
            if selection:
                idx = selection[0]
                section_text = sections_listbox.get(idx)
                current_name = section_text.split(' (')[0]
                
                # Find section ID by name
                sections = get_sections()
                section_id = None
                for sid, section in sections.items():
                    if section.name == current_name:
                        section_id = sid
                        break
                
                new_name = tk.simpledialog.askstring("Renombrar Sección", 
                                                   "Nuevo nombre:", initialvalue=current_name)
                if new_name and new_name.strip() and section_id:
                    if on_rename_section(section_id, new_name.strip()):
                        refresh_sections()
                        if on_refresh:
                            on_refresh()
        
        tk.Button(buttons_frame, text="Agregar Sección", command=add_section,
                 bg="#4CAF50", fg="white", padx=10).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Eliminar Sección", command=remove_section,
                 bg="#f44336", fg="white", padx=10).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Renombrar", command=rename_section,
                 bg="#2196F3", fg="white", padx=10).pack(side="left", padx=5)
        
        # Close button
        tk.Button(dialog, text="Cerrar", command=dialog.destroy,
                 bg="#757575", fg="white", padx=15).pack(pady=10)
    
    def populate_sectioned_treeview(self, tree: ttk.Treeview, sectioned_data: Dict,
                                   id_key: str = 'id') -> None:
        """Populate treeview with sectioned data"""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        # Add sections and their items
        for section_id, section_data in sectioned_data.items():
            if section_id == "default":
                # Non-sectioned mode
                for item_data in section_data:
                    values = tuple(item_data[col] for col in tree["columns"] if col in item_data)
                    tree.insert("", "end", values=values, tags=(str(item_data.get(id_key, "")),))
            else:
                # Sectioned mode
                section_name = section_data['name']
                section_subtotal = section_data['subtotal']
                
                # Add section header
                section_header = tree.insert("", "end", values=(
                    f"═══ {section_name} ═══", "", "", "", "", "", f"${section_subtotal:.2f}"
                ), tags=("section_header",))
                
                # Configure section header style
                tree.set(section_header, "producto", f"═══ {section_name} ═══")
                tree.set(section_header, "subtotal", f"${section_subtotal:.2f}")
                
                # Add items in section
                for item_data in section_data['items']:
                    values = tuple(item_data[col] for col in tree["columns"] if col in item_data)
                    tree.insert(section_header, "end", values=values, tags=(str(item_data.get(id_key, "")),))
        
        # Expand all sections
        for item in tree.get_children():
            tree.item(item, open=True)