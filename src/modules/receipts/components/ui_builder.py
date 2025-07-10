import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict, Any

class UIBuilder:
    """Handles UI component creation for receipt application"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
    
    def create_client_section(self, parent: tk.Widget, client_names: List[str], 
                             client_var: tk.StringVar, on_client_change: Callable,
                             save_to_db_var: tk.BooleanVar) -> ttk.Combobox:
        """Create client selection section"""
        cliente_frame = tk.LabelFrame(parent, text="1. Seleccionar Cliente", font=("Arial", 12, "bold"))
        cliente_frame.pack(fill="x", pady=(0, 10))
        
        frame_interno = tk.Frame(cliente_frame)
        frame_interno.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_interno, text="Cliente:", font=("Arial", 12)).pack(side="left", padx=5)
        
        cliente_combo = ttk.Combobox(frame_interno, textvariable=client_var, 
                                   values=client_names, state="readonly", width=40)
        cliente_combo.pack(side="left", padx=5)
        cliente_combo.bind("<<ComboboxSelected>>", on_client_change)
        
        # Checkbox for auto-save
        tk.Checkbutton(frame_interno, 
                      text="Guardar en base de datos", 
                      variable=save_to_db_var,
                      font=("Arial", 10)).pack(side="right", padx=20)
        
        return cliente_combo
    
    def create_products_section(self, parent: tk.Widget, search_var: tk.StringVar,
                               on_search_change: Callable, on_clear_search: Callable,
                               on_product_double_click: Callable) -> ttk.Treeview:
        """Create products search and selection section"""
        productos_frame = tk.LabelFrame(parent, text="2. Buscar y Seleccionar Productos", 
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
        carrito_frame = tk.LabelFrame(parent, text="3. Carrito de Compras", font=("Arial", 12, "bold"))
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