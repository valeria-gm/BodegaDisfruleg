import os
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from fpdf import FPDF
from datetime import datetime
import mysql.connector
from conexion import conectar
from decimal import Decimal, InvalidOperation
import hashlib
import json
from auth_manager import AuthManager

# Obtener conexión y cursor
conn = conectar()
cursor = conn.cursor(dictionary=True)

# Obtener clientes con su grupo y descuento
cursor.execute("""
    SELECT c.id_cliente, c.nombre_cliente, c.id_grupo, g.descuento 
    FROM cliente c
    LEFT JOIN grupo g ON c.id_grupo = g.id_grupo
""")
clientes = cursor.fetchall()

# Crear carpeta recibos si no existe
if not os.path.exists("recibos"):
    os.makedirs("recibos")

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Registrar fuentes Unicode (asegúrate de tener la carpeta 'fonts' en tu proyecto)
        self.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
        self.set_font('DejaVu', '', 12)  # Fuente por defecto

class ReciboAppMejorado:
    def __init__(self, root, user_data):
        self.auth_manager = AuthManager()
        self.root = root
        self.root.title("Generador de Recibos - Mejorado")
        self.root.geometry("1000x700")

        self.user_data = user_data if isinstance(user_data, dict) else json.loads(user_data)
        self.es_admin = (self.user_data['rol'] == 'admin')

        self.cliente_seleccionado = tk.StringVar()
        self.cliente_id = None
        self.grupo_nombre_id = None
        self.descuento_cliente = Decimal("0")
        
        # Variable para controlar el guardado automático
        self.guardar_en_bd = tk.BooleanVar(value=True)
        
        # Datos para el carrito de compras
        self.carrito = {}  # {producto_id: {'producto': producto_data, 'cantidad': float}}
        self.todos_productos = []
        
        # Variables para búsqueda
        self.search_var = tk.StringVar()
        self.categoria_var = tk.StringVar(value="Todos")

        self.crear_interfaz()

    def crear_interfaz(self):
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # SECCIÓN 1: Selección de cliente
        self.crear_seccion_cliente(main_frame)
        
        # SECCIÓN 2: Búsqueda y selección de productos
        self.crear_seccion_productos(main_frame)
        
        # SECCIÓN 3: Carrito de compras
        self.crear_seccion_carrito(main_frame)
        
        # SECCIÓN 4: Botones de acción
        self.crear_seccion_acciones(main_frame)
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set(f"Usuario: {self.user_data['nombre_completo']} | Rol: {self.user_data['rol']} | Seleccione un cliente")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def crear_seccion_cliente(self, parent):
        """Sección para seleccionar cliente"""
        cliente_frame = tk.LabelFrame(parent, text="1. Seleccionar Cliente", font=("Arial", 12, "bold"))
        cliente_frame.pack(fill="x", pady=(0, 10))
        
        frame_interno = tk.Frame(cliente_frame)
        frame_interno.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_interno, text="Cliente:", font=("Arial", 12)).pack(side="left", padx=5)
        
        nombres_clientes = [cliente["nombre_cliente"] for cliente in clientes]
        self.cliente_combo = ttk.Combobox(frame_interno, textvariable=self.cliente_seleccionado, 
                                         values=nombres_clientes, state="readonly", width=40)
        self.cliente_combo.pack(side="left", padx=5)
        self.cliente_combo.bind("<<ComboboxSelected>>", self.cargar_productos)
        
        # Checkbox para guardado automático
        self.check_guardar = tk.Checkbutton(frame_interno, 
                                           text="Guardar en base de datos", 
                                           variable=self.guardar_en_bd,
                                           font=("Arial", 10))
        self.check_guardar.pack(side="right", padx=20)

    def crear_seccion_productos(self, parent):
        """Sección para búsqueda y selección de productos"""
        productos_frame = tk.LabelFrame(parent, text="2. Buscar y Seleccionar Productos", font=("Arial", 12, "bold"))
        productos_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Frame de búsqueda
        search_frame = tk.Frame(productos_frame)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(search_frame, text="Buscar:", font=("Arial", 11)).pack(side="left", padx=5)
        
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30, font=("Arial", 11))
        search_entry.pack(side="left", padx=5)
        self.search_var.trace("w", self.filtrar_productos)
        
        tk.Button(search_frame, text="Limpiar Búsqueda", 
                 command=self.limpiar_busqueda, bg="#ff9800", fg="white").pack(side="left", padx=10)
        
        # Frame de la tabla de productos
        tabla_frame = tk.Frame(productos_frame)
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Scrollbar para productos
        scrollbar_prod = tk.Scrollbar(tabla_frame)
        scrollbar_prod.pack(side="right", fill="y")
        
        # Treeview para productos disponibles
        self.productos_tree = ttk.Treeview(tabla_frame, 
                                          columns=("nombre", "unidad", "precio", "accion"),
                                          show="headings", 
                                          yscrollcommand=scrollbar_prod.set,
                                          height=8)
        
        self.productos_tree.heading("nombre", text="Producto")
        self.productos_tree.heading("unidad", text="Unidad")
        self.productos_tree.heading("precio", text="Precio")
        self.productos_tree.heading("accion", text="Cantidad")
        
        self.productos_tree.column("nombre", width=250)
        self.productos_tree.column("unidad", width=80)
        self.productos_tree.column("precio", width=100)
        self.productos_tree.column("accion", width=150)
        
        self.productos_tree.pack(side="left", fill="both", expand=True)
        scrollbar_prod.config(command=self.productos_tree.yview)
        
        # Doble click para agregar al carrito
        self.productos_tree.bind("<Double-1>", self.agregar_producto_rapido)

    def crear_seccion_carrito(self, parent):
        """Sección del carrito de compras"""
        carrito_frame = tk.LabelFrame(parent, text="3. Carrito de Compras", font=("Arial", 12, "bold"))
        carrito_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Frame de la tabla del carrito
        tabla_carrito_frame = tk.Frame(carrito_frame)
        tabla_carrito_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar para carrito
        scrollbar_carrito = tk.Scrollbar(tabla_carrito_frame)
        scrollbar_carrito.pack(side="right", fill="y")
        
        # Treeview para carrito
        self.carrito_tree = ttk.Treeview(
            tabla_carrito_frame,
            columns=("producto", "cantidad", "unidad", "precio_base", "descuento", "precio_final", "subtotal"),
            show="headings",
            yscrollcommand=scrollbar_carrito.set,
            height=6
        )
        
        # Configurar encabezados
        self.carrito_tree.heading("producto", text="Producto")
        self.carrito_tree.heading("cantidad", text="Cantidad")
        self.carrito_tree.heading("unidad", text="Unidad")
        self.carrito_tree.heading("precio_base", text="Precio Base")
        self.carrito_tree.heading("descuento", text="Descuento")
        self.carrito_tree.heading("precio_final", text="Precio Final")
        self.carrito_tree.heading("subtotal", text="Subtotal")
        
        # Configurar anchos de columnas
        self.carrito_tree.column("producto", width=200)
        self.carrito_tree.column("cantidad", width=80)
        self.carrito_tree.column("unidad", width=80)
        self.carrito_tree.column("precio_base", width=100)
        self.carrito_tree.column("descuento", width=80)
        self.carrito_tree.column("precio_final", width=100)
        self.carrito_tree.column("subtotal", width=100)
        
        self.carrito_tree.pack(side="left", fill="both", expand=True)
        scrollbar_carrito.config(command=self.carrito_tree.yview)
        
        # Doble click para editar cantidad
        self.carrito_tree.bind("<Double-1>", self.editar_cantidad_carrito)
        
        # Frame de total
        total_frame = tk.Frame(carrito_frame)
        total_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.total_var = tk.StringVar(value="Total: $0.00")
        total_label = tk.Label(total_frame, textvariable=self.total_var, 
                              font=("Arial", 14, "bold"), fg="#2196F3")
        total_label.pack(side="right", padx=10)
        
        # Botones del carrito
        botones_carrito = tk.Frame(total_frame)
        botones_carrito.pack(side="left")
        
        tk.Button(botones_carrito, text="Eliminar Seleccionado", 
                 command=self.eliminar_del_carrito, bg="#f44336", fg="white").pack(side="left", padx=5)
        tk.Button(botones_carrito, text="Limpiar Carrito", 
                 command=self.limpiar_carrito, bg="#ff5722", fg="white").pack(side="left", padx=5)

    def crear_seccion_acciones(self, parent):
        """Sección de botones de acción"""
        acciones_frame = tk.Frame(parent)
        acciones_frame.pack(fill="x", pady=10)
        
        tk.Button(acciones_frame, text="Generar Recibo", command=self.generar_recibo,
                  bg="#4CAF50", fg="white", padx=20, pady=8, font=("Arial", 12, "bold")).pack(side="right", padx=5)
        
        tk.Button(acciones_frame, text="Vista Previa", command=self.vista_previa,
                  bg="#2196F3", fg="white", padx=15, pady=8, font=("Arial", 11)).pack(side="right", padx=5)

    def cargar_productos(self, event=None):
        """Cargar productos cuando se selecciona un cliente"""
        cliente_nombre = self.cliente_seleccionado.get()
        
        # Buscar el cliente
        for cliente in clientes:
            if cliente["nombre_cliente"] == cliente_nombre:
                self.cliente_id = cliente["id_cliente"]
                self.grupo_cliente_id = cliente["id_grupo"]
                self.descuento_cliente = Decimal(str(cliente["descuento"])) if cliente["descuento"] else Decimal('0')
                break
        
        # MODIFICACIÓN: Ahora cargamos TODOS los productos, incluyendo los especiales
        query = """
            SELECT p.id_producto, p.nombre_producto, p.unidad_producto, 
                   p.precio_base, p.es_especial
            FROM producto p
            ORDER BY p.es_especial ASC, p.nombre_producto ASC
        """
        
        cursor.execute(query)
        self.todos_productos = cursor.fetchall()
        self.mostrar_productos()
        
        # Limpiar carrito al cambiar cliente
        self.limpiar_carrito()
        
        self.status_var.set(
            f"Cliente: {cliente_nombre} | " 
            f"Descuento: {float(self.descuento_cliente)}% | "
            f"{len(self.todos_productos)} productos"
        )

    def mostrar_productos(self, productos=None):
        """Mostrar productos en la tabla"""
        # Limpiar tabla
        for item in self.productos_tree.get_children():
            self.productos_tree.delete(item)
        
        if productos is None:
            productos = self.todos_productos
        
        for producto in productos:
            # Calcular precio con descuento
            precio_base = Decimal(str(producto['precio_base']))
            precio_final = precio_base * (1 - self.descuento_cliente / 100)

            # Verificar si ya está en el carrito
            if producto['id_producto'] in self.carrito:
                en_carrito = "✓ En carrito"
            else:
                en_carrito = "Doble-click para agregar"
            
            # MODIFICACIÓN: Marcar productos especiales de forma más visible
            nombre_producto = producto['nombre_producto']
            if producto['es_especial']:
                nombre_producto = f"🔒 {nombre_producto}"
                en_carrito = "ESPECIAL - " + en_carrito

            self.productos_tree.insert("", "end", 
                                     values=(nombre_producto,
                                            producto['unidad_producto'],
                                            f"${precio_final:.2f}",
                                            en_carrito),
                                     tags=(str(producto['id_producto']),))

    def filtrar_productos(self, *args):
        """Filtrar productos por búsqueda"""
        texto_busqueda = self.search_var.get().lower()
        
        if not texto_busqueda:
            self.mostrar_productos()
            return
        
        productos_filtrados = []
        for producto in self.todos_productos:
            if texto_busqueda in producto['nombre_producto'].lower():
                productos_filtrados.append(producto)
        
        self.mostrar_productos(productos_filtrados)

    def limpiar_busqueda(self):
        """Limpiar búsqueda"""
        self.search_var.set("")
        self.mostrar_productos()

    def verificar_password_admin(self):
        """Verificar contraseña de administrador"""
        class AdminPasswordDialog:
            def __init__(self, parent, app_instance):
                self.parent = parent
                self.app_instance = app_instance
                self.result = None
                self.dialog = tk.Toplevel(parent)
                self.dialog.title("Autenticación de Administrador")
                self.dialog.geometry("400x300")
                self.dialog.transient(parent)
                self.dialog.grab_set()
                
                # Centrar la ventana
                self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
                
                # Marco principal
                main_frame = tk.Frame(self.dialog)
                main_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                # Título
                title_label = tk.Label(main_frame, text="🔒 Producto Especial", 
                                     font=("Arial", 14, "bold"), fg="#f44336")
                title_label.pack(pady=(0, 10))
                
                # Mensaje
                message_label = tk.Label(main_frame, 
                                       text="Este producto requiere permisos de administrador.\nIngrese las credenciales de un administrador:",
                                       font=("Arial", 10), justify="center")
                message_label.pack(pady=(0, 20))
                
                # Usuario
                tk.Label(main_frame, text="Usuario:", font=("Arial", 11)).pack(anchor="w")
                self.username_var = tk.StringVar()
                self.username_entry = tk.Entry(main_frame, textvariable=self.username_var, width=30)
                self.username_entry.pack(fill="x", pady=(0, 10))
                
                # Contraseña
                tk.Label(main_frame, text="Contraseña:", font=("Arial", 11)).pack(anchor="w")
                self.password_var = tk.StringVar()
                self.password_entry = tk.Entry(main_frame, textvariable=self.password_var, show="*", width=30)
                self.password_entry.pack(fill="x", pady=(0, 20))
                
                # Botones
                button_frame = tk.Frame(main_frame)
                button_frame.pack(fill="x")
                
                tk.Button(button_frame, text="Cancelar", command=self.cancelar,
                         bg="#f44336", fg="white", padx=15, pady=5).pack(side="right", padx=5)
                tk.Button(button_frame, text="Verificar", command=self.verificar,
                         bg="#4CAF50", fg="white", padx=15, pady=5).pack(side="right", padx=5)
                
                # Focus y bind
                self.username_entry.focus_set()
                self.password_entry.bind("<Return>", lambda e: self.verificar())
                self.dialog.bind("<Escape>", lambda e: self.cancelar())
                
                # Hacer modal
                self.dialog.wait_window()
            
            def verificar(self):
                username = self.username_var.get().strip()
                password = self.password_var.get().strip()
                
                if not username or not password:
                    messagebox.showerror("Error", "Por favor ingrese usuario y contraseña")
                    return
                
                auth_result = self.app_instance.auth_manager.authenticate(username, password)

                if auth_result['success'] and auth_result['user_data']['rol'] == 'admin':
                    self.result = True
                    self.dialog.destroy()
                    return
                messagebox.showerror("Error", auth_result.get('message', 'Credenciales inválidas'))
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus_set()

            
            def cancelar(self):
                self.result = False
                self.dialog.destroy()
        
        # Crear diálogo y obtener resultado
        dialog = AdminPasswordDialog(self.root, self)
        return dialog.result

    def agregar_producto_rapido(self, event):
        """Agregar producto al carrito con doble click"""
        item_seleccionado = self.productos_tree.focus()
        if not item_seleccionado:
            return
        
        try: 
            # Obtener el ID del producto desde los tags del ítem seleccionado
            item_data = self.productos_tree.item(item_seleccionado)
            producto_id = int(item_data['tags'][0])
            producto = next((p for p in self.todos_productos if p['id_producto'] == producto_id), None)

            if not producto:
                messagebox.showerror("Error", "Producto no encontrado")
                return

            # MODIFICACIÓN: Verificar si es producto especial y el usuario no es admin
            if producto.get('es_especial', False) and not self.es_admin:
                # Solicitar autenticación de administrador
                if not self.verificar_password_admin():
                    return  # Usuario canceló o falló la autenticación
                
                # Si llegamos aquí, la autenticación fue exitosa
                messagebox.showinfo("Autorizado", "Acceso autorizado. Puede agregar el producto especial.")
            
            # Si ya está en carrito, preguntar si quiere editar
            if producto_id in self.carrito:
                if messagebox.askyesno("Producto en carrito", 
                                    "Este producto ya está en el carrito. ¿Desea editar la cantidad?"):
                    self.editar_cantidad_producto(producto_id)
                return
            
            # Crear diálogo después de un pequeño retraso
            self.root.after(100, lambda: self.mostrar_dialogo_seguro(producto))

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

    def mostrar_dialogo_seguro(self, producto):
        """Mostrar diálogo para ingresar cantidad"""
        try:
            # Crear la ventana
            dialogo = tk.Toplevel(self.root)
            dialogo.title("Agregar Producto")
            
            # Configuración inicial
            dialogo.transient(self.root)
            dialogo.resizable(False, False)
            
            # Cálculos con Decimal
            precio_base = Decimal(str(producto['precio_base']))
            descuento = Decimal(str(self.descuento_cliente)) if self.grupo_cliente_id else Decimal('0')
            monto_descuento = precio_base * (descuento / Decimal('100'))
            precio_con_descuento = precio_base - monto_descuento
            
            # Widgets usando solo grid()
            nombre_producto = producto['nombre_producto']
            if producto.get('es_especial', False):
                nombre_producto = f"🔒 {nombre_producto} (ESPECIAL)"
            
            tk.Label(dialogo, text=nombre_producto, 
                font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 5))
        
            tk.Label(dialogo, text=f"Precio base: ${float(precio_base):.2f}", 
                    font=("Arial", 10)).grid(row=1, column=0, columnspan=2, sticky="w", padx=20)
            
            if descuento > 0:
                tk.Label(dialogo, 
                    text=f"Descuento ({float(descuento):.1f}%): -${float(monto_descuento):.2f}",
                    font=("Arial", 10), fg="red").grid(row=2, column=0, columnspan=2, sticky="w", padx=20)
            
            tk.Label(dialogo, text=f"Precio final: ${float(precio_con_descuento):.2f}", 
                    font=("Arial", 11, "bold")).grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=5)
            
            tk.Label(dialogo, text=f"Unidad: {producto['unidad_producto']}",
                    font=("Arial", 10)).grid(row=4, column=0, columnspan=2, sticky="w", padx=20)
            
            # Entrada de cantidad
            tk.Label(dialogo, text="Cantidad:", font=("Arial", 11)).grid(row=5, column=0, sticky="e", padx=20)
            
            cantidad_var = tk.StringVar(value="1.0")
            cantidad_entry = tk.Entry(dialogo, textvariable=cantidad_var, 
                                    width=10, font=("Arial", 11))
            cantidad_entry.grid(row=5, column=1, sticky="w", padx=5)
            cantidad_entry.focus_set()
            cantidad_entry.select_range(0, tk.END)
            
            # Total
            total_var = tk.StringVar(value=f"Total: ${float(precio_con_descuento):.2f}")
            tk.Label(dialogo, textvariable=total_var, 
                    font=("Arial", 11, "bold"), fg="#2196F3").grid(row=6, column=0, columnspan=2, pady=(10, 20))
        
            # Frame para botones
            botones_frame = tk.Frame(dialogo)
            botones_frame.grid(row=7, column=0, columnspan=2, pady=(0, 15))
                
            def agregar_al_carrito():
                try:
                    # Convertir a Decimal de manera segura
                    cantidad = Decimal(cantidad_var.get().strip())
                    if cantidad <= Decimal('0'):
                        messagebox.showerror("Error", "La cantidad debe ser mayor que 0")
                        return
                    
                    self.carrito[producto['id_producto']] = {
                        'producto': producto,
                        'cantidad': cantidad,
                        'precio_base': float(precio_base),
                        'precio_final': float(precio_con_descuento),
                        'monto_descuento': float(monto_descuento)
                    }
                    
                    self.actualizar_carrito()
                    self.mostrar_productos()
                    dialogo.destroy()

                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo agregar: {str(e)}")
            
            tk.Button(botones_frame, text="Agregar", 
                    command=agregar_al_carrito, bg="#4CAF50", fg="white",
                    padx=15, pady=3).pack(side="left", padx=5)
            
            tk.Button(botones_frame, text="Cancelar", 
                    command=dialogo.destroy, bg="#f44336", fg="white",
                    padx=15, pady=3).pack(side="left", padx=5)
            
            # Enter para agregar
            cantidad_entry.bind("<Return>", lambda e: agregar_al_carrito())

            # Función para calcular total
            def calcular_total(*args):
                try:
                    cantidad = Decimal(cantidad_var.get().strip())
                    total = cantidad * precio_con_descuento
                    total_var.set(f"Total: ${float(total):.2f}")
                except (ValueError, InvalidOperation):
                    total_var.set("Total: $0.00")
            
            cantidad_var.trace("w", calcular_total)
            
            # Asegurar que la ventana esté completamente inicializada
            dialogo.update_idletasks()

            # Centrar 
            width = dialogo.winfo_reqwidth()
            height = dialogo.winfo_reqheight()
            x = (dialogo.winfo_screenwidth() // 2) - (width // 2)
            y = (dialogo.winfo_screenheight() // 2) - (height // 2)
            dialogo.geometry(f"+{x}+{y}")

            # Hacer modal al final
            dialogo.grab_set()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar el diálogo: {str(e)}")
            print(f"Error en mostrar_dialogo_cantidad: {e}")
            if 'dialogo' in locals():
                dialogo.destroy()

    def actualizar_carrito(self):
        """Actualizar visualización del carrito"""
        # Limpiar carrito
        for item in self.carrito_tree.get_children():
            self.carrito_tree.delete(item)
        
        total_general = Decimal('0')
        
        for producto_id, item in self.carrito.items():
            producto = item['producto']
            cantidad = Decimal(str(item['cantidad']))
            precio_base = Decimal(str(item['precio_base']))
            precio_final = Decimal(str(item['precio_final']))
            subtotal = cantidad * precio_final
            total_general += subtotal
            
            # Marcar productos especiales en el carrito
            nombre_producto = producto['nombre_producto']
            if producto.get('es_especial', False):
                nombre_producto = f"🔒 {nombre_producto}"
            
            self.carrito_tree.insert("", "end",
                                    values=(
                                        nombre_producto,
                                        f"{float(cantidad):.2f}",
                                        producto['unidad_producto'],
                                        f"${float(precio_base):.2f}",
                                        f"-${float(item['monto_descuento']):.2f}" if self.grupo_cliente_id else "$0.00",
                                        f"${float(precio_final):.2f}",
                                        f"${float(subtotal):.2f}"
                                    ),
                                    tags=(str(producto_id),))
        
        self.carrito_tree.heading("precio_base", text="Precio Base")
        self.carrito_tree.heading("descuento", text="Descuento")
        self.carrito_tree.heading("precio_final", text="Precio Final")
        
        self.total_var.set(f"Total: ${float(total_general):.2f}")
        self.status_var.set(f"Carrito: {len(self.carrito)} productos | Total: ${float(total_general):.2f}")

    def editar_cantidad_carrito(self, event):
        """Editar cantidad desde el carrito"""
        item_seleccionado = self.carrito_tree.focus()
        if not item_seleccionado:
            return
        
        producto_id = int(self.carrito_tree.item(item_seleccionado, "tags")[0])
        self.editar_cantidad_producto(producto_id)

    def editar_cantidad_producto(self, producto_id):
        """Editar cantidad de un producto específico"""
        if producto_id not in self.carrito:
            return
        
        item = self.carrito[producto_id]
        producto = item['producto']
        cantidad_actual = item['cantidad']
        
        # Crear diálogo simple
        nueva_cantidad = simpledialog.askfloat(
            "Editar Cantidad",
            f"Nueva cantidad para {producto['nombre_producto']}:",
            initialvalue=cantidad_actual,
            minvalue=0.01
        )
        
        if nueva_cantidad:
            self.carrito[producto_id]['cantidad'] = Decimal(str(nueva_cantidad))
            self.actualizar_carrito()

    def eliminar_del_carrito(self):
        """Eliminar producto seleccionado del carrito"""
        item_seleccionado = self.carrito_tree.focus()
        if not item_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un producto del carrito para eliminar")
            return
        
        producto_id = int(self.carrito_tree.item(item_seleccionado, "tags")[0])
        producto_nombre = self.carrito[producto_id]['producto']['nombre_producto']
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar {producto_nombre} del carrito?"):
            del self.carrito[producto_id]
            self.actualizar_carrito()
            self.mostrar_productos()

    def limpiar_carrito(self):
        """Limpiar todo el carrito"""
        if self.carrito and not messagebox.askyesno("Confirmar", "¿Limpiar todo el carrito?"):
            return
        
        self.carrito.clear()
        self.actualizar_carrito()
        self.mostrar_productos()

    def vista_previa(self):
        """Mostrar vista previa del recibo"""
        if not self.cliente_seleccionado.get():
            messagebox.showerror("Error", "Debe seleccionar un cliente")
            return
        
        if not self.carrito:
            messagebox.showerror("Error", "El carrito está vacío")
            return
        
        # Crear ventana de vista previa
        preview = tk.Toplevel(self.root)
        preview.title("Vista Previa del Recibo")
        preview.geometry("600x500")
        
        # Contenido de la vista previa
        content = f"RECIBO PARA: {self.cliente_seleccionado.get()}\n"
        content += f"Fecha: {datetime.now().strftime('%Y-%m-%d')}\n"
        content += "="*50 + "\n"
        
        total_general = Decimal('0')
        for item in self.carrito.values():
            producto = item['producto']
            cantidad = float(item['cantidad'])
            precio_final = float(item['precio_final'])
            subtotal = cantidad * precio_final
            total_general += Decimal(str(subtotal))
            
            nombre_producto = producto['nombre_producto']
            if producto.get('es_especial', False):
                nombre_producto = f"🔒 {nombre_producto} (ESPECIAL)"
            
            content += f"{nombre_producto}\n"
            content += f"  {cantidad:.2f} {producto['unidad_producto']} x ${precio_final:.2f} = ${subtotal:.2f}\n\n"
        
        content += "="*50 + "\n"
        content += f"TOTAL: ${total_general:.2f}"
        
        text_widget = tk.Text(preview, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", content)
        text_widget.config(state="disabled")

    def generar_recibo(self):
        """Generar recibo final"""
        if not self.cliente_seleccionado.get():
            messagebox.showerror("Error", "Debe seleccionar un cliente")
            return
        
        if not self.carrito:
            messagebox.showerror("Error", "El carrito está vacío")
            return
        
        # Preparar productos finales correctamente
        productos_finales = []
        for producto_id, item in self.carrito.items():
            productos_finales.append({
                'producto': item['producto'],
                'cantidad': item['cantidad'],
                'unidad': item['producto']['unidad_producto'],
                'precio_final': Decimal(str(item['precio_final'])),
                'subtotal': item['cantidad'] * Decimal(str(item['precio_final']))
            })

        total_general = sum(float(item['subtotal']) for item in productos_finales)
    
        if not messagebox.askyesno("Confirmar", f"¿Generar recibo por ${total_general:.2f}?"):
            return
        
        # Guardar en BD si está activado
        if self.guardar_en_bd.get():
            if self.guardar_factura(productos_finales):
                messagebox.showinfo("Éxito", "Recibo guardado correctamente")
        
        # Generar PDF
        try:
            self.crear_pdf(
                [(item['producto']['nombre_producto'], 
                float(item['cantidad']), 
                item['unidad'], 
                float(item['precio_final']), 
                float(item['subtotal'])) for item in productos_finales],
                total_general
            )
        except Exception as e:
            messagebox.showerror("Error PDF", f"No se pudo generar el PDF: {e}\n\nLa factura SÍ se guardó en la base de datos.")
        
        
        
        # Limpiar carrito después de generar
        if messagebox.askyesno("Limpiar Carrito", "¿Desea limpiar el carrito para un nuevo recibo?"):
            self.limpiar_carrito()

    def crear_pdf(self, productos_finales, total_general):
        """Crear archivo PDF del recibo"""
        cliente = self.cliente_seleccionado.get()
        fecha = datetime.now().strftime("%Y-%m-%d")
        nombre_archivo = f"recibos/recibo_{cliente.lower().replace(' ', '_')}_{fecha}_{datetime.now().strftime('%H%M%S')}.pdf"

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("DejaVu", size=12)

        # Encabezado
        pdf.set_font("DejaVu", "B", 16)
        pdf.cell(200, 10, txt="DISFRULEG", ln=True, align="C")
        pdf.set_font("DejaVu", size=12)
        pdf.cell(200, 10, txt=f"Recibo para: {cliente}", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Fecha: {fecha}", ln=True, align="C")
        pdf.ln(10)

        # Tabla de productos
        pdf.set_font("DejaVu", "B", 10)
        pdf.cell(60, 10, "Producto", 1)
        pdf.cell(30, 10, "Cantidad", 1)
        pdf.cell(30, 10, "Unidad", 1)
        pdf.cell(30, 10, "Precio/Unidad", 1)
        pdf.cell(40, 10, "Subtotal", 1)
        pdf.ln()

        pdf.set_font("DejaVu", size=10)
        for nombre, cantidad, unidad, precio_unitario, total in productos_finales:
            # Limpiar caracteres especiales para PDF
            nombre_limpio = nombre.replace('🔒', '[ESPECIAL]').encode('latin1', 'replace').decode('latin1')
            pdf.cell(60, 10, nombre_limpio, 1)
            pdf.cell(30, 10, f"{cantidad:.2f}", 1)
            pdf.cell(30, 10, f"{unidad}", 1)
            pdf.cell(30, 10, f"${precio_unitario:.2f}", 1)
            pdf.cell(40, 10, f"${total:.2f}", 1)
            pdf.ln()

        # Total
        pdf.ln(5)
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(150, 10, "TOTAL", 1)
        pdf.cell(40, 10, f"${total_general:.2f}", 1)

        pdf.output(nombre_archivo)
        messagebox.showinfo("Éxito", f"Recibo guardado en {nombre_archivo}")

    def guardar_factura(self, productos_finales):
        """Guardar factura en la base de datos"""
        try:
            # Limpiar cualquier resultado pendiente
            while cursor.nextset():
                pass
                
            cursor.execute("START TRANSACTION")
            
            # Insertar factura
            cursor.execute(
                "INSERT INTO factura (fecha_factura, id_cliente) VALUES (%s, %s)",
                (datetime.now().strftime('%Y-%m-%d'), self.cliente_id)
            )
            factura_id = cursor.lastrowid
            
            # Insertar detalles de factura
            for item in productos_finales:
                if isinstance(item, dict):
                    id_producto = item['producto']['id_producto']
                    cantidad = item['cantidad']
                    precio = item['precio_final']
                else:
                    id_producto = item[0]
                    cantidad = item[1]
                    precio = item[3]

                cursor.execute(
                    """INSERT INTO detalle_factura 
                    (id_factura, id_producto, cantidad_factura, precio_unitario_venta) 
                     VALUES (%s, %s, %s, %s)""",
                    (factura_id, id_producto, float(cantidad), float(precio))
                )
            
            conn.commit()
            self.status_var.set(f"Factura #{factura_id} guardada en base de datos")
            return True
        
        except mysql.connector.Error as err:
            conn.rollback()
            messagebox.showerror("Error", f"Error al guardar en la base de datos: {err}")
            return False
        
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
            return False 
        
        finally:
            try:
                while cursor.nextset():
                    pass
            except:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    user_data = {
        'nombre_completo': 'Usuario Prueba',
        'rol': 'usuario'  # Cambiar a 'admin' para probar productos especiales
    }
    app = ReciboAppMejorado(root, user_data)
    root.mainloop()