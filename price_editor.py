import os
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import mysql.connector
from conexion import conectar
from decimal import Decimal
from auth_manager import AuthManager

class PriceEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Precios - Disfruleg")
        self.root.geometry("900x650")
        
        # Connect to database
        self.conn = conectar()
        self.cursor = self.conn.cursor(dictionary=True)
        self.auth_manager = AuthManager()
        
        # Variables
        self.current_group = tk.IntVar(value=1)
        self.changes_made = False
        
        self.create_interface()
        self.load_groups()
        self.load_products()
    
    def create_interface(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_frame = tk.Frame(main_frame, bg="#2C3E50", relief="raised", bd=2)
        title_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(title_frame, 
                text="EDITOR DE PRECIOS", 
                font=("Arial", 18, "bold"),
                fg="white", bg="#2C3E50").pack(pady=10)
        
        # Groups frame
        group_frame = tk.Frame(main_frame, bg="#f0f0f0")
        group_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(group_frame, 
                text="Grupo de Cliente:", 
                font=("Arial", 12, "bold"),
                bg="#f0f0f0").pack(side="left", padx=5)
        
        self.group_buttons_frame = tk.Frame(group_frame, bg="#f0f0f0")
        self.group_buttons_frame.pack(side="left")
        
        # Edit discount button
        tk.Button(group_frame, 
                 text="Editar Descuento", 
                 command=self.edit_group_discount,
                 bg="#3498DB", fg="white").pack(side="left", padx=10)
        
        # Search and actions frame
        action_frame = tk.Frame(main_frame, bg="#f0f0f0")
        action_frame.pack(fill="x", pady=10)
        
        # Search
        tk.Label(action_frame, 
                text="Buscar:", 
                font=("Arial", 12),
                bg="#f0f0f0").pack(side="left")
        
        self.search_entry = tk.Entry(action_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_products)
        
        # Buttons
        btn_frame = tk.Frame(action_frame, bg="#f0f0f0")
        btn_frame.pack(side="right")
        
        tk.Button(btn_frame, 
                 text="Agregar Producto", 
                 command=self.add_product_dialog,
                 bg="#2ECC71", fg="white").pack(side="left", padx=5)
        
        tk.Button(btn_frame, 
                 text="Eliminar Producto", 
                 command=self.delete_product,
                 bg="#E74C3C", fg="white").pack(side="left", padx=5)
        
        # Products table
        table_frame = tk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)
        
        scroll_y = tk.Scrollbar(table_frame)
        scroll_y.pack(side="right", fill="y")
        
        self.product_tree = ttk.Treeview(
            table_frame,
            columns=("id", "nombre", "unidad", "precio_base", "descuento", "precio_final", "especial"),
            yscrollcommand=scroll_y.set
        )
        
        # Configure columns
        self.product_tree.heading("id", text="ID")
        self.product_tree.heading("nombre", text="Producto")
        self.product_tree.heading("unidad", text="Unidad")
        self.product_tree.heading("precio_base", text="Precio Base")
        self.product_tree.heading("descuento", text="Descuento %")
        self.product_tree.heading("precio_final", text="Precio Final")
        self.product_tree.heading("especial", text="Especial")
        
        self.product_tree.column("id", width=50, anchor="center")
        self.product_tree.column("nombre", width=250)
        self.product_tree.column("unidad", width=80, anchor="center")
        self.product_tree.column("precio_base", width=100, anchor="e")
        self.product_tree.column("descuento", width=80, anchor="center")
        self.product_tree.column("precio_final", width=100, anchor="e")
        self.product_tree.column("especial", width=80, anchor="center")
        
        self.product_tree.pack(fill="both", expand=True)
        scroll_y.config(command=self.product_tree.yview)
        
        # Bind events
        self.product_tree.bind("<Double-1>", self.edit_base_price)
        
        # Bottom buttons
        bottom_frame = tk.Frame(main_frame, bg="#f0f0f0")
        bottom_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(bottom_frame, 
                 text="Cancelar Cambios", 
                 command=self.cancel_changes,
                 bg="#E67E22", fg="white").pack(side="left", padx=5)
        
        tk.Button(bottom_frame, 
                 text="Guardar Cambios", 
                 command=self.save_all_changes,
                 bg="#27AE60", fg="white").pack(side="right", padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Listo")
        status_bar = tk.Label(self.root, 
                            textvariable=self.status_var,
                            bd=1, relief=tk.SUNKEN, 
                            anchor=tk.W,
                            font=("Arial", 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_groups(self):
        """Cargar grupos de clientes desde la base de datos"""
        for widget in self.group_buttons_frame.winfo_children():
            widget.destroy()
        
        self.cursor.execute("SELECT id_grupo, clave_grupo, descuento FROM grupo ORDER BY id_grupo")
        self.groups = self.cursor.fetchall()
        
        for group in self.groups:
            rb = tk.Radiobutton(
                self.group_buttons_frame,
                text=f"{group['clave_grupo']} ({group['descuento']}%)",
                variable=self.current_group,
                value=group['id_grupo'],
                command=self.load_products,
                bg="#f0f0f0"
            )
            rb.pack(side="left", padx=5)
    
    def load_products(self):
        """Cargar productos desde la base de datos"""
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
            
        group_id = self.current_group.get()
        group_discount = next((g['descuento'] for g in self.groups if g['id_grupo'] == group_id), 0)
        
        self.cursor.execute("""
            SELECT id_producto, nombre_producto, unidad_producto, precio_base, es_especial
            FROM producto ORDER BY nombre_producto
        """)
        self.all_products = self.cursor.fetchall()
        
        for product in self.all_products:
            final_price = product['precio_base'] * (1 - Decimal(group_discount)/100)
            
            self.product_tree.insert("", "end",
                values=(
                    product["id_producto"],
                    product["nombre_producto"],
                    product["unidad_producto"],
                    f"${product['precio_base']:.2f}",
                    f"{group_discount}%",
                    f"${final_price:.2f}",
                    "Sí" if product['es_especial'] else "No"
                ),
                tags=(str(product['es_especial']),)
            )
        
        self.status_var.set(f"Mostrando {len(self.all_products)} productos")
    
    def filter_products(self, event=None):
        search_text = self.search_entry.get().lower()
        
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        for product in self.all_products:
            if search_text in product["nombre_producto"].lower():
                group_id = self.current_group.get()
                group_discount = next((g['descuento'] for g in self.groups if g['id_grupo'] == group_id), 0)
                final_price = product['precio_base'] * (1 - Decimal(group_discount)/100)
                
                self.product_tree.insert("", "end",
                    values=(
                        product["id_producto"],
                        product["nombre_producto"],
                        product["unidad_producto"],
                        f"${product['precio_base']:.2f}",
                        f"{group_discount}%",
                        f"${final_price:.2f}",
                        "Sí" if product['es_especial'] else "No"
                    ),
                    tags=(str(product['es_especial']),)
                )
    
    def add_product_dialog(self):
        """Mostrar popup para agregar nuevo producto"""
        popup = tk.Toplevel(self.root)
        popup.title("Agregar Producto")
        popup.transient(self.root)
        popup.grab_set()
        
        # Variables
        name_var = tk.StringVar()
        unit_var = tk.StringVar()
        price_var = tk.StringVar()
        stock_var = tk.StringVar(value="0")
        special_var = tk.BooleanVar(value=False)
        
        # Frame principal
        main_frame = tk.Frame(popup, padx=20, pady=20)
        main_frame.pack()
        
        # Campos del formulario
        tk.Label(main_frame, text="Nombre del Producto:").grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(main_frame, textvariable=name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(main_frame, text="Unidad de Medida:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Combobox(main_frame, textvariable=unit_var, width=27,
                    values=["kg", "g", "lb", "unidad", "L", "ml", "docena", "paquete"]).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(main_frame, text="Precio Base:").grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(main_frame, textvariable=price_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(main_frame, text="Stock Inicial:").grid(row=3, column=0, sticky="w", pady=5)
        tk.Entry(main_frame, textvariable=stock_var, width=30).grid(row=3, column=1, padx=5, pady=5)

        # Checkbox para producto especial
        tk.Checkbutton(main_frame, 
                     text="Producto Especial",
                     variable=special_var).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Botones
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        tk.Button(button_frame, 
                text="Guardar", 
                command=lambda: self.save_new_product(popup, name_var.get(), unit_var.get(), price_var.get(), special_var.get()),
                bg="#4CAF50", fg="white", width=10).pack(side="left", padx=10)
        
        tk.Button(button_frame, 
                text="Cancelar", 
                command=popup.destroy,
                bg="#F44336", fg="white", width=10).pack(side="left", padx=10)
        
        # Configuración inicial
        popup.resizable(False, False)
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'+{x}+{y}')
    
    def save_new_product(self, popup, name, unit, price, is_special):
        """Guardar nuevo producto en la base de datos"""
        if not name.strip():
            messagebox.showerror("Error", "El nombre del producto es obligatorio", parent=popup)
            return
            
        if not unit.strip():
            messagebox.showerror("Error", "La unidad de medida es obligatoria", parent=popup)
            return
        
        try:
            price = Decimal(price)
            if price <= 0:
                messagebox.showerror("Error", "El precio debe ser mayor que 0", parent=popup)
                return
        except:
            messagebox.showerror("Error", "Ingrese un precio válido", parent=popup)
            return
        
        try:
            stock = Decimal(stock)
            if stock < 0:
                messagebox.showerror("Error", "El stock no puede ser negativo", parent=popup)
                return
        except:
            messagebox.showerror("Error", "Ingrese un valor de stock válido", parent=popup)
            return
        
        if is_special and not self.verify_admin_password("crear producto especial"):
            messagebox.showerror("Permiso denegado", 
                               "No tiene permisos para crear productos especiales", 
                               parent=popup)
            return
        
        try:
            self.cursor.execute("""
                INSERT INTO producto (nombre_producto, unidad_producto, precio_base, stock, es_especial)
                VALUES (%s, %s, %s, %s, %s)
            """, (name.strip(), unit.strip(), price, stock, is_special))
            
            self.conn.commit()
            self.changes_made = True
            popup.destroy()
            self.load_products()
            self.status_var.set(f"Producto '{name}' agregado correctamente")
            
        except mysql.connector.Error as err:
            self.conn.rollback()
            if err.errno == 1062:  # Duplicate entry
                messagebox.showerror("Error", "Ya existe un producto con ese nombre", parent=popup)
            else:
                messagebox.showerror("Error", f"Error al guardar producto: {err}", parent=popup)
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error inesperado: {str(e)}", parent=popup)
    
    def edit_base_price(self, event):
        """Editar el precio base de un producto"""
        item = self.product_tree.focus()
        if not item:
            return
            
        values = self.product_tree.item(item, "values")
        product_id = values[0]
        product_name = values[1]
        is_special = self.product_tree.item(item, "tags")[0] == "1"
        current_price = values[3].replace("$", "")
        
        popup = tk.Toplevel(self.root)
        popup.title(f"Editar Precio - {product_name}")
        popup.transient(self.root)
        popup.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(popup, padx=20, pady=20)
        main_frame.pack()
        
        tk.Label(main_frame, text=f"Producto: {product_name}").pack(pady=5)
        tk.Label(main_frame, text=f"Unidad: {values[2]}").pack(pady=5)
        
        # Precio
        price_frame = tk.Frame(main_frame)
        price_frame.pack(pady=10)
        
        tk.Label(price_frame, text="Nuevo Precio Base:").pack(side="left")
        price_entry = tk.Entry(price_frame)
        price_entry.pack(side="left", padx=5)
        price_entry.insert(0, current_price)
        price_entry.select_range(0, tk.END)
        price_entry.focus_set()
        
        # Botones
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        def save_changes():
            if is_special and not self.verify_admin_password(f"editar {product_name}"):
                popup.lift()
                return
                
            new_price = price_entry.get()
            try:
                new_price = Decimal(new_price)
                if new_price <= 0:
                    messagebox.showerror("Error", "El precio debe ser mayor que 0", parent=popup)
                    return
                    
                self.cursor.execute("""
                    UPDATE producto SET precio_base = %s WHERE id_producto = %s
                """, (new_price, product_id))
                
                self.conn.commit()
                self.changes_made = True
                popup.destroy()
                self.load_products()
                self.status_var.set(f"Precio de '{product_name}' actualizado")
                
            except ValueError:
                messagebox.showerror("Error", "Ingrese un precio válido", parent=popup)
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Error", f"Error al actualizar: {str(e)}", parent=popup)
        
        tk.Button(button_frame, 
                text="Guardar", 
                command=save_changes,
                bg="#4CAF50", fg="white").pack(side="left", padx=10)
        
        tk.Button(button_frame, 
                text="Cancelar", 
                command=popup.destroy,
                bg="#F44336", fg="white").pack(side="left", padx=10)
        
        popup.resizable(False, False)
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'+{x}+{y}')
    
    def save_base_price(self, popup, product_id, product_name, new_price):
        """Guardar el precio base editado"""
        try:
            new_price = Decimal(new_price)
            if new_price <= 0:
                messagebox.showerror("Error", "El precio debe ser mayor que 0", parent=popup)
                return
                
            self.cursor.execute("""
                UPDATE producto SET precio_base = %s WHERE id_producto = %s
            """, (new_price, product_id))
            
            self.conn.commit()
            self.changes_made = True
            popup.destroy()
            self.load_products()
            self.status_var.set(f"Precio de '{product_name}' actualizado")
            
        except ValueError:
            messagebox.showerror("Error", "Ingrese un precio válido", parent=popup)
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}", parent=popup)
    
    def edit_group_discount(self):
        """Editar el descuento de un grupo"""
        group_id = self.current_group.get()
        group = next((g for g in self.groups if g['id_grupo'] == group_id), None)
        
        if not group:
            return
            
        # Primero crea el popup    
        popup = tk.Toplevel(self.root)
        popup.title(f"Editar Descuento - {group['clave_grupo']}")
        popup.transient(self.root)
        popup.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(popup, padx=20, pady=20)
        main_frame.pack()
        
        tk.Label(main_frame, text=f"Grupo: {group['clave_grupo']}").pack(pady=5)
        
        # Descuento
        discount_frame = tk.Frame(main_frame)
        discount_frame.pack(pady=10)
        
        tk.Label(discount_frame, text="Nuevo Descuento (%):").pack(side="left")
        discount_entry = tk.Entry(discount_frame, width=10)
        discount_entry.pack(side="left", padx=5)
        discount_entry.insert(0, group['descuento'])
        discount_entry.select_range(0, tk.END)
        discount_entry.focus_set()
        
        # Botones
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        def save_changes():
            if group['clave_grupo'] != "STANDARD" and not self.verify_admin_password("editar descuentos"):
                popup.lift()
                return
                
            new_discount = discount_entry.get()
            try:
                new_discount = Decimal(new_discount)
                if new_discount < 0 or new_discount >= 100:
                    messagebox.showerror("Error", "El descuento debe estar entre 0 y 100", parent=popup)
                    return
                    
                self.cursor.execute("""
                    UPDATE grupo SET descuento = %s WHERE id_grupo = %s
                """, (new_discount, group_id))
                
                self.conn.commit()
                self.changes_made = True
                popup.destroy()
                self.load_groups()
                self.load_products()
                self.status_var.set("Descuento actualizado correctamente")
                
            except ValueError:
                messagebox.showerror("Error", "Ingrese un porcentaje válido", parent=popup)
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Error", f"Error al actualizar: {str(e)}", parent=popup)

        tk.Button(button_frame, 
            text="Guardar", 
            command=save_changes,
            bg="#4CAF50", fg="white").pack(side="left", padx=10)
    
        tk.Button(button_frame, 
                text="Cancelar", 
                command=popup.destroy,
                bg="#F44336", fg="white").pack(side="left", padx=10)
        
        popup.resizable(False, False)
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'+{x}+{y}')
    
    def save_group_discount(self, popup, group_id, new_discount):
        """Guardar el descuento editado"""
        try:
            new_discount = Decimal(new_discount)
            if new_discount < 0 or new_discount >= 100:
                messagebox.showerror("Error", "El descuento debe estar entre 0 y 100", parent=popup)
                return
                
            self.cursor.execute("""
                UPDATE grupo SET descuento = %s WHERE id_grupo = %s
            """, (new_discount, group_id))
            
            self.conn.commit()
            self.changes_made = True
            popup.destroy()
            self.load_groups()
            self.load_products()
            self.status_var.set("Descuento actualizado correctamente")
            
        except ValueError:
            messagebox.showerror("Error", "Ingrese un porcentaje válido", parent=popup)
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}", parent=popup)
    
    def delete_product(self):
        """Eliminar un producto"""
        item = self.product_tree.focus()
        if not item:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
            
        values = self.product_tree.item(item, "values")
        product_id = values[0]
        product_name = values[1]
        is_special = self.product_tree.item(item, "tags")[0] == "1"
        
        if is_special and not self.verify_admin_password(f"eliminar {product_name}"):
            return
        
        if not messagebox.askyesno("Confirmar", f"¿Eliminar el producto '{product_name}'?"):
            return
            
        try:
            # Verificar si el producto está en facturas
            self.cursor.execute("""
                SELECT COUNT(*) as count FROM detalle_factura WHERE id_producto = %s
            """, (product_id,))
            result = self.cursor.fetchone()
            
            if result['count'] > 0:
                confirm = messagebox.askyesno(
                    "Advertencia", 
                    f"Este producto aparece en {result['count']} facturas. ¿Eliminar de todos modos?"
                )
                if not confirm:
                    return
            
            # Eliminar producto
            self.cursor.execute("DELETE FROM producto WHERE id_producto = %s", (product_id,))
            self.conn.commit()
            self.changes_made = True
            self.load_products()
            self.status_var.set(f"Producto '{product_name}' eliminado")
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")
    
    def cancel_changes(self):
        """Cancelar todos los cambios no guardados"""
        if self.changes_made:
            if messagebox.askyesno("Cancelar Cambios", "¿Descartar todos los cambios no guardados?"):
                self.conn.rollback()
                self.changes_made = False
                self.load_groups()
                self.load_products()
                self.status_var.set("Cambios cancelados")
        else:
            self.status_var.set("No hay cambios pendientes")
    
    def save_all_changes(self):
        """Guardar todos los cambios en la base de datos"""
        try:
            self.conn.commit()
            self.changes_made = False
            self.status_var.set("Todos los cambios guardados")
            messagebox.showinfo("Éxito", "Cambios guardados correctamente")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"No se pudieron guardar los cambios: {str(e)}")
    
    def verify_admin_password(self, action):
        """Verificar contraseña de administrador"""
        password = simpledialog.askstring(
            "Autenticación Requerida",
            f"Para {action} se requiere contraseña de administrador:",
            show="*",
            parent=self.root
        )
        
        if not password:
            return False
            
        try:
            auth_result = self.auth_manager.authenticate("admin", password)
            return auth_result['success']
        except:
            return False
    
    def on_closing(self):
        """Manejar el cierre de la ventana"""
        if self.changes_made:
            if messagebox.askyesno("Cambios sin guardar", "¿Guardar cambios antes de salir?"):
                self.save_all_changes()
        
        self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PriceEditorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()