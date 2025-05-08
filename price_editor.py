import os
import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from conexion import conectar
from decimal import Decimal

class PriceEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Precios y Productos - Disfruleg")
        self.root.geometry("800x600")
        
        # Connect to database
        self.conn = conectar()
        self.cursor = self.conn.cursor(dictionary=True)
        
        # Variables
        self.current_tipo_cliente = tk.IntVar(value=1)  # Default to Regular
        self.changes_made = False  # Track if changes have been made
        
        self.create_interface()
        self.load_products()
        
    def create_interface(self):
        # Main frame to contain all elements
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_frame = tk.Frame(main_frame)
        title_frame.pack(fill="x", pady=10)
        
        tk.Label(title_frame, text="EDITOR DE PRECIOS Y PRODUCTOS", font=("Arial", 18, "bold")).pack()
        
        # Customer type selection
        tipo_frame = tk.Frame(main_frame)
        tipo_frame.pack(fill="x", pady=5)
        
        tk.Label(tipo_frame, text="Tipo de Cliente:", font=("Arial", 12)).pack(side="left", padx=10)
        
        # Get customer types from database
        self.cursor.execute("SELECT id_tipo, nombre FROM tipo_cliente")
        tipos_cliente = self.cursor.fetchall()
        
        for tipo in tipos_cliente:
            rb = tk.Radiobutton(tipo_frame, text=tipo["nombre"], variable=self.current_tipo_cliente, 
                               value=tipo["id_tipo"], command=self.load_products)
            rb.pack(side="left", padx=10)
        
        # Search and action buttons frame
        action_frame = tk.Frame(main_frame)
        action_frame.pack(fill="x", pady=5, padx=10)
        
        # Search section
        search_frame = tk.Frame(action_frame)
        search_frame.pack(side="left", fill="x", expand=True)
        
        tk.Label(search_frame, text="Buscar:", font=("Arial", 12)).pack(side="left", padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_products)
        
        # Add/Delete product buttons
        buttons_frame = tk.Frame(action_frame)
        buttons_frame.pack(side="right")
        
        tk.Button(buttons_frame, text="Agregar Producto", command=self.add_product_dialog, 
                  bg="#2196F3", fg="white", padx=10, pady=3).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Eliminar Producto", command=self.delete_product, 
                  bg="#f44336", fg="white", padx=10, pady=3).pack(side="left", padx=5)
        
        # Create a frame that will contain the scrollable table
        # This is the key improvement: using a fixed height for the table container
        table_container = tk.Frame(main_frame)
        table_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Products table with scrollbar
        table_frame = tk.Frame(table_container)
        table_frame.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview for products
        self.product_tree = ttk.Treeview(table_frame, columns=("id", "nombre", "unidad", "precio"), 
                                        show="headings", yscrollcommand=scrollbar.set)
        
        # Configure columns
        self.product_tree.heading("id", text="ID")
        self.product_tree.heading("nombre", text="Producto")
        self.product_tree.heading("unidad", text="Unidad")
        self.product_tree.heading("precio", text="Precio")
        
        self.product_tree.column("id", width=50)
        self.product_tree.column("nombre", width=300)
        self.product_tree.column("unidad", width=100)
        self.product_tree.column("precio", width=100)
        
        self.product_tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.product_tree.yview)
        
        # Double-click to edit price
        self.product_tree.bind("<Double-1>", self.edit_price)
        
        # Fixed bottom frame for buttons - always visible
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10, padx=10)
        
        save_button = tk.Button(button_frame, text="Guardar Cambios", font=("Arial", 12), 
                 command=self.save_all_changes, bg="#4CAF50", fg="white", padx=15, pady=5)
        save_button.pack(side="right")
        
        cancel_button = tk.Button(button_frame, text="Cancelar Cambios", font=("Arial", 12), 
                 command=self.load_products, bg="#f44336", fg="white", padx=15, pady=5)
        cancel_button.pack(side="right", padx=10)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Listo")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_products(self):
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
            
        tipo_id = self.current_tipo_cliente.get()
        
        # Get products with prices for selected customer type
        self.cursor.execute("""
            SELECT p.id_producto, p.nombre_producto, p.unidad, pr.precio, pr.id_precio 
            FROM producto p
            LEFT JOIN precio pr ON p.id_producto = pr.id_producto AND pr.id_tipo = %s
            ORDER BY p.nombre_producto
        """, (tipo_id,))
        
        productos = self.cursor.fetchall()
        
        # Store all products for reference and filtering
        self.all_products = productos
        
        # Insert products into treeview
        for producto in productos:
            precio = producto.get('precio')
            precio_str = f"${precio:.2f}" if precio is not None else "No establecido"
            id_precio = str(producto.get('id_precio', '')) if producto.get('id_precio') is not None else ""
            
            self.product_tree.insert("", "end", 
                                   values=(producto["id_producto"], 
                                          producto["nombre_producto"], 
                                          producto["unidad"], 
                                          precio_str),
                                   tags=(id_precio,))
            
        self.status_var.set(f"Mostrando {len(productos)} productos para tipo de cliente: {self.get_tipo_name(tipo_id)}")
    
    def get_tipo_name(self, tipo_id):
        self.cursor.execute("SELECT nombre FROM tipo_cliente WHERE id_tipo = %s", (tipo_id,))
        result = self.cursor.fetchone()
        return result["nombre"] if result else "Desconocido"
    
    def filter_products(self, event=None):
        search_text = self.search_entry.get().lower()
        
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Filter products
        for producto in self.all_products:
            if search_text in producto["nombre_producto"].lower():
                precio = producto.get('precio')
                precio_str = f"${precio:.2f}" if precio is not None else "No establecido"
                id_precio = str(producto.get('id_precio', '')) if producto.get('id_precio') is not None else ""
                
                self.product_tree.insert("", "end", 
                                       values=(producto["id_producto"], 
                                              producto["nombre_producto"], 
                                              producto["unidad"], 
                                              precio_str),
                                       tags=(id_precio,))
    
    def edit_price(self, event):
        # Get selected item
        item_id = self.product_tree.focus()
        if not item_id:
            return
            
        # Get current values
        values = self.product_tree.item(item_id, "values")
        price_id = self.product_tree.item(item_id, "tags")[0]
        
        # If price is not set yet
        if values[3] == "No establecido":
            self.set_new_price(values[0])
            return
        
        # Create popup for editing existing price
        popup = tk.Toplevel(self.root)
        popup.title("Editar Precio")
        popup.geometry("400x200")
        popup.transient(self.root)
        popup.grab_set()
        
        # Center popup
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Producto info
        tk.Label(popup, text=f"Producto: {values[1]}", font=("Arial", 12)).pack(pady=5)
        tk.Label(popup, text=f"Unidad: {values[2]}", font=("Arial", 12)).pack(pady=5)
        
        # Current price without $ sign
        current_price = values[3].replace("$", "")
        
        # Price entry
        price_frame = tk.Frame(popup)
        price_frame.pack(pady=10)
        
        tk.Label(price_frame, text="Nuevo Precio: $", font=("Arial", 12)).pack(side="left")
        price_entry = tk.Entry(price_frame, width=10, font=("Arial", 12))
        price_entry.pack(side="left")
        price_entry.insert(0, current_price)
        price_entry.select_range(0, tk.END)
        price_entry.focus_set()
        
        # Buttons
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Guardar", 
                 command=lambda: self.update_price(popup, price_id, price_entry.get(), item_id, values), 
                 bg="#4CAF50", fg="white", padx=15, pady=5).pack(side="left", padx=10)
        
        tk.Button(button_frame, text="Cancelar", 
                 command=popup.destroy, 
                 bg="#f44336", fg="white", padx=15, pady=5).pack(side="left", padx=10)
    
    def set_new_price(self, product_id):
        # Get product info
        self.cursor.execute("SELECT nombre_producto, unidad FROM producto WHERE id_producto = %s", (product_id,))
        product = self.cursor.fetchone()
        
        if not product:
            messagebox.showerror("Error", "Producto no encontrado")
            return
        
        # Create popup for setting new price
        popup = tk.Toplevel(self.root)
        popup.title("Establecer Precio")
        popup.geometry("400x300")
        popup.transient(self.root)
        popup.grab_set()
        
        # Center popup
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Create a main container frame
        main_frame = tk.Frame(popup)
        main_frame.pack(fill="both", expand=True)
        
        # Product info
        tk.Label(main_frame, text=f"Producto: {product['nombre_producto']}", font=("Arial", 12)).pack(pady=5)
        tk.Label(main_frame, text=f"Unidad: {product['unidad']}", font=("Arial", 12)).pack(pady=5)
        
        # Get all customer types
        self.cursor.execute("SELECT id_tipo, nombre FROM tipo_cliente")
        tipos = self.cursor.fetchall()
        
        # Price entries for all customer types
        entries = {}
        
        # Create a frame with fixed height for prices
        price_container = tk.Frame(main_frame)
        price_container.pack(fill="x", padx=10, pady=5)
        
        # Create price entries in a simple frame
        price_frame = tk.Frame(price_container)
        price_frame.pack(fill="x")
        
        for tipo in tipos:
            tipo_frame = tk.Frame(price_frame)
            tipo_frame.pack(pady=3, fill="x")
            
            tk.Label(tipo_frame, text=f"Precio para {tipo['nombre']}:", width=18, anchor="w").pack(side="left")
            tk.Label(tipo_frame, text="$").pack(side="left")
            entry = tk.Entry(tipo_frame, width=10)
            entry.pack(side="left")
            entries[tipo['id_tipo']] = entry
        
        # Focus on current customer type price
        entries[self.current_tipo_cliente.get()].focus_set()
        
        # Buttons - always at the bottom
        button_frame = tk.Frame(popup)
        button_frame.pack(side="bottom", fill="x", pady=10)
        
        tk.Button(button_frame, text="Guardar", 
                 command=lambda: self.insert_new_prices(popup, product_id, entries), 
                 bg="#4CAF50", fg="white", padx=15, pady=5).pack(side="left", padx=10)
        
        tk.Button(button_frame, text="Cancelar", 
                 command=popup.destroy, 
                 bg="#f44336", fg="white", padx=15, pady=5).pack(side="left", padx=10)
    
    def insert_new_prices(self, popup, product_id, entries):
        try:
            for tipo_id, entry in entries.items():
                price_text = entry.get().strip()
                if price_text:
                    try:
                        price = Decimal(price_text)
                        if price <= 0:
                            messagebox.showerror("Error", "Los precios deben ser mayores que 0")
                            return
                            
                        # Check if price exists
                        self.cursor.execute(
                            "SELECT id_precio FROM precio WHERE id_producto = %s AND id_tipo = %s", 
                            (product_id, tipo_id)
                        )
                        result = self.cursor.fetchone()
                        
                        if result:
                            # Update existing price
                            self.cursor.execute(
                                "UPDATE precio SET precio = %s WHERE id_producto = %s AND id_tipo = %s",
                                (price, product_id, tipo_id)
                            )
                        else:
                            # Insert new price
                            self.cursor.execute(
                                "INSERT INTO precio (id_producto, id_tipo, precio) VALUES (%s, %s, %s)",
                                (product_id, tipo_id, price)
                            )
                    except ValueError:
                        messagebox.showerror("Error", f"Precio inválido para {self.get_tipo_name(tipo_id)}")
                        return
            
            self.conn.commit()
            self.changes_made = False  # Reset changes flag after successful save
            self.status_var.set("Precios establecidos correctamente")
            popup.destroy()
            self.load_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar precios: {str(e)}")
            self.conn.rollback()
        
    def update_price(self, popup, price_id, new_price, item_id, values):
        try:
            # Convert price to decimal
            new_price = Decimal(new_price)
            
            if new_price <= 0:
                messagebox.showerror("Error", "El precio debe ser mayor que 0")
                return
                
            # Update treeview
            self.product_tree.item(item_id, values=(values[0], values[1], values[2], f"${new_price:.2f}"))
            
            # Update in database
            self.cursor.execute("UPDATE precio SET precio = %s WHERE id_precio = %s", (new_price, price_id))
            self.conn.commit()
            
            self.changes_made = False  # Reset changes flag after successful save
            self.status_var.set(f"Precio actualizado para {values[1]}")
            popup.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa un precio válido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
            self.conn.rollback()
    
    def add_product_dialog(self):
        # Create popup for adding new product
        popup = tk.Toplevel(self.root)
        popup.title("Agregar Nuevo Producto")
        popup.geometry("450x400")
        popup.transient(self.root)
        popup.grab_set()
        
        # Center popup
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Create main frame to organize content
        main_frame = tk.Frame(popup)
        main_frame.pack(fill="both", expand=True)
        
        # Product info fields
        tk.Label(main_frame, text="Agregar Nuevo Producto", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Name field
        name_frame = tk.Frame(main_frame)
        name_frame.pack(fill="x", pady=5, padx=20)
        tk.Label(name_frame, text="Nombre del Producto:", width=20, anchor="w").pack(side="left")
        name_entry = tk.Entry(name_frame, width=30)
        name_entry.pack(side="left", padx=5, fill="x", expand=True)
        name_entry.focus_set()
        
        # Unit field
        unit_frame = tk.Frame(main_frame)
        unit_frame.pack(fill="x", pady=5, padx=20)
        tk.Label(unit_frame, text="Unidad:", width=20, anchor="w").pack(side="left")
        
        # Get common units for dropdown
        common_units = ["kg", "pz", "manojo", "caja", "litro", "docena"]
        unit_var = tk.StringVar()
        unit_combo = ttk.Combobox(unit_frame, textvariable=unit_var, values=common_units)
        unit_combo.pack(side="left", padx=5, fill="x", expand=True)
        
        # Create a frame with fixed height for price entries
        price_container = tk.Frame(main_frame)
        price_container.pack(fill="x", padx=20, pady=5)
        
        # Label frame for prices with fixed height
        price_label_frame = tk.LabelFrame(price_container, text="Precios por Tipo de Cliente", padx=10, pady=5)
        price_label_frame.pack(fill="x")
        
        # Get all customer types
        self.cursor.execute("SELECT id_tipo, nombre FROM tipo_cliente")
        tipos = self.cursor.fetchall()
        
        # Create price entries
        price_entries = {}
        for tipo in tipos:
            price_frame = tk.Frame(price_label_frame)
            price_frame.pack(fill="x", pady=2)
            
            tk.Label(price_frame, text=f"Precio {tipo['nombre']}:", width=15, anchor="w").pack(side="left")
            tk.Label(price_frame, text="$").pack(side="left")
            price_entry = tk.Entry(price_frame, width=10)
            price_entry.pack(side="left", padx=5)
            price_entries[tipo['id_tipo']] = price_entry
        
        # Buttons - in a separate frame that's packed at the bottom
        # This is key to ensure buttons are always visible
        button_frame = tk.Frame(popup)
        button_frame.pack(side="bottom", fill="x", pady=15)
        
        tk.Button(button_frame, text="Guardar Producto", 
                 command=lambda: self.save_new_product(popup, name_entry.get(), unit_var.get(), price_entries), 
                 bg="#4CAF50", fg="white", padx=10, pady=5).pack(side="left", padx=10)
        
        tk.Button(button_frame, text="Cancelar", 
                 command=popup.destroy, 
                 bg="#f44336", fg="white", padx=10, pady=5).pack(side="left", padx=10)
    
    def save_new_product(self, popup, name, unit, price_entries):
        # Validate fields
        if not name.strip():
            messagebox.showerror("Error", "El nombre del producto es obligatorio")
            return
            
        if not unit.strip():
            messagebox.showerror("Error", "La unidad de medida es obligatoria")
            return
        
        # Start transaction
        try:
            # Insert new product
            self.cursor.execute(
                "INSERT INTO producto (nombre_producto, unidad) VALUES (%s, %s)",
                (name, unit)
            )
            
            # Get product ID
            new_product_id = self.cursor.lastrowid
            
            # Insert prices for each customer type
            for tipo_id, entry in price_entries.items():
                price_text = entry.get().strip()
                if price_text:
                    try:
                        price = Decimal(price_text)
                        if price <= 0:
                            raise ValueError("Precio debe ser mayor que 0")
                            
                        self.cursor.execute(
                            "INSERT INTO precio (id_producto, id_tipo, precio) VALUES (%s, %s, %s)",
                            (new_product_id, tipo_id, price)
                        )
                    except ValueError:
                        messagebox.showerror("Error", f"Precio inválido para {self.get_tipo_name(tipo_id)}")
                        self.conn.rollback()
                        return
            
            # Commit changes
            self.conn.commit()
            self.changes_made = False  # Reset changes flag after successful save
            
            messagebox.showinfo("Éxito", f"Producto '{name}' agregado correctamente")
            self.status_var.set(f"Producto '{name}' agregado correctamente")
            popup.destroy()
            
            # Refresh product list
            self.load_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar producto: {str(e)}")
            self.conn.rollback()
    
    def delete_product(self):
        # Get selected product
        item_id = self.product_tree.focus()
        if not item_id:
            messagebox.showwarning("Advertencia", "Por favor selecciona un producto para eliminar")
            return
            
        # Get product info
        values = self.product_tree.item(item_id, "values")
        product_id = values[0]
        product_name = values[1]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirmar Eliminación", 
                                 f"¿Estás seguro de eliminar el producto '{product_name}'?\n\n"
                                 f"Esta acción eliminará todas las referencias al producto, "
                                 f"incluyendo los precios y detalles de facturas existentes."):
            return
            
        # Check if product is referenced in any invoice
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM detalle_factura WHERE id_producto = %s", 
            (product_id,)
        )
        result = self.cursor.fetchone()
        
        if result and result['count'] > 0:
            if not messagebox.askyesno("Advertencia", 
                                     f"El producto '{product_name}' está siendo utilizado en {result['count']} "
                                     f"facturas existentes. Si eliminas este producto, esas facturas "
                                     f"pueden quedar inconsistentes.\n\n¿Estás seguro de continuar?"):
                return
        
        # Delete product and related records
        try:
            # First delete price records
            self.cursor.execute("DELETE FROM precio WHERE id_producto = %s", (product_id,))
            
            # Then delete any detalle_factura records (if user confirmed)
            self.cursor.execute("DELETE FROM detalle_factura WHERE id_producto = %s", (product_id,))
            
            # Finally delete the product
            self.cursor.execute("DELETE FROM producto WHERE id_producto = %s", (product_id,))
            
            # Commit changes
            self.conn.commit()
            self.changes_made = False  # Reset changes flag after successful save
            
            messagebox.showinfo("Éxito", f"Producto '{product_name}' eliminado correctamente")
            self.status_var.set(f"Producto '{product_name}' eliminado correctamente")
            
            # Refresh product list
            self.load_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar producto: {str(e)}")
            self.conn.rollback()
    
    def save_all_changes(self):
        try:
            self.conn.commit()
            self.changes_made = False  # Reset changes flag after successful save
            messagebox.showinfo("Éxito", "Todos los cambios han sido guardados")
            self.status_var.set("Todos los cambios guardados exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cambios: {str(e)}")
            self.conn.rollback()
            
    def on_closing(self):
        try:
            # Only ask if there are unsaved changes
            if self.changes_made:
                if messagebox.askyesno("Salir", "¿Hay cambios sin guardar. ¿Deseas guardarlos antes de salir?"):
                    self.save_all_changes()
        except:
            pass
            
        self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PriceEditorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()