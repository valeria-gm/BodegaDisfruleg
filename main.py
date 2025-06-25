import os
import tkinter as tk
from tkinter import messagebox, ttk
from fpdf import FPDF
from datetime import datetime
import mysql.connector
from conexion import conectar
from decimal import Decimal, InvalidOperation

conn = conectar()
cursor = conn.cursor(dictionary=True)

# Obtener clientes desde la base de datos con su tipo
cursor.execute("SELECT id_cliente, nombre, id_tipo FROM cliente")
clientes = cursor.fetchall()

# Crear carpeta recibos si no existe
if not os.path.exists("recibos"):
    os.makedirs("recibos")

class ReciboAppMejorado:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Recibos - Mejorado")
        self.root.geometry("1000x700")

        self.cliente_seleccionado = tk.StringVar()
        self.cliente_id = None
        self.tipo_cliente_id = None
        
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
        self.status_var.set("Listo - Seleccione un cliente para comenzar")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def crear_seccion_cliente(self, parent):
        """Sección para seleccionar cliente"""
        cliente_frame = tk.LabelFrame(parent, text="1. Seleccionar Cliente", font=("Arial", 12, "bold"))
        cliente_frame.pack(fill="x", pady=(0, 10))
        
        frame_interno = tk.Frame(cliente_frame)
        frame_interno.pack(fill="x", padx=10, pady=10)
        
        tk.Label(frame_interno, text="Cliente:", font=("Arial", 12)).pack(side="left", padx=5)
        
        nombres_clientes = [cliente["nombre"] for cliente in clientes]
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
        self.carrito_tree = ttk.Treeview(tabla_carrito_frame,
                                        columns=("producto", "cantidad", "unidad", "precio", "subtotal"),
                                        show="headings",
                                        yscrollcommand=scrollbar_carrito.set,
                                        height=6)
        
        self.carrito_tree.heading("producto", text="Producto")
        self.carrito_tree.heading("cantidad", text="Cantidad")
        self.carrito_tree.heading("unidad", text="Unidad")
        self.carrito_tree.heading("precio", text="Precio Unit.")
        self.carrito_tree.heading("subtotal", text="Subtotal")
        
        self.carrito_tree.column("producto", width=200)
        self.carrito_tree.column("cantidad", width=80)
        self.carrito_tree.column("unidad", width=80)
        self.carrito_tree.column("precio", width=100)
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
        
        # Buscar el tipo de cliente
        for cliente in clientes:
            if cliente["nombre"] == cliente_nombre:
                self.cliente_id = cliente["id_cliente"]
                self.tipo_cliente_id = cliente["id_tipo"]
                break
        
        if not self.tipo_cliente_id:
            self.tipo_cliente_id = 1
        
        # Obtener productos con precios
        cursor.execute("""
            SELECT p.id_producto, p.nombre_producto, p.unidad, pr.precio 
            FROM producto p
            JOIN precio pr ON p.id_producto = pr.id_producto
            WHERE pr.id_tipo = %s
            ORDER BY p.nombre_producto
        """, (self.tipo_cliente_id,))
        
        self.todos_productos = cursor.fetchall()
        self.mostrar_productos()
        
        # Limpiar carrito al cambiar cliente
        self.limpiar_carrito()
        
        self.status_var.set(f"Cliente: {cliente_nombre} - {len(self.todos_productos)} productos disponibles")

    def mostrar_productos(self, productos=None):
        """Mostrar productos en la tabla"""
        # Limpiar tabla
        for item in self.productos_tree.get_children():
            self.productos_tree.delete(item)
        
        if productos is None:
            productos = self.todos_productos
        
        for producto in productos:
            # Verificar si ya está en el carrito
            en_carrito = "✓ En carrito" if producto['id_producto'] in self.carrito else "Doble-click para agregar"
            
            self.productos_tree.insert("", "end", 
                                     values=(producto['nombre_producto'],
                                            producto['unidad'],
                                            f"${producto['precio']:.2f}",
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

    def agregar_producto_rapido(self, event):
        """Agregar producto al carrito con doble click"""
        item_seleccionado = self.productos_tree.focus()
        if not item_seleccionado:
            return
        
        producto_id = int(self.productos_tree.item(item_seleccionado, "tags")[0])
        
        # Si ya está en carrito, preguntar si quiere editar
        if producto_id in self.carrito:
            if messagebox.askyesno("Producto en carrito", 
                                 "Este producto ya está en el carrito. ¿Desea editar la cantidad?"):
                self.editar_cantidad_producto(producto_id)
            return
        
        # Mostrar diálogo para cantidad
        self.mostrar_dialogo_cantidad(producto_id)

    def mostrar_dialogo_cantidad(self, producto_id):
        """Mostrar diálogo para ingresar cantidad"""
        # Buscar datos del producto
        producto = next((p for p in self.todos_productos if p['id_producto'] == producto_id), None)
        if not producto:
            return
        
        # Crear ventana de diálogo
        dialogo = tk.Toplevel(self.root)
        dialogo.title("Agregar al Carrito")
        dialogo.geometry("400x300")
        dialogo.transient(self.root)
        dialogo.grab_set()
        
        # Centrar diálogo
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (dialogo.winfo_width() // 2)
        y = (dialogo.winfo_screenheight() // 2) - (dialogo.winfo_height() // 2)
        dialogo.geometry(f"+{x}+{y}")
        
        # Información del producto
        info_frame = tk.LabelFrame(dialogo, text="Producto Seleccionado", padx=10, pady=10)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(info_frame, text=f"Producto: {producto['nombre_producto']}", 
                font=("Arial", 12, "bold")).pack(anchor="w")
        tk.Label(info_frame, text=f"Unidad: {producto['unidad']}", 
                font=("Arial", 11)).pack(anchor="w")
        tk.Label(info_frame, text=f"Precio: ${producto['precio']:.2f}", 
                font=("Arial", 11)).pack(anchor="w")
        
        # Entrada de cantidad
        cantidad_frame = tk.Frame(dialogo)
        cantidad_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(cantidad_frame, text="Cantidad:", font=("Arial", 12)).pack(side="left")
        
        cantidad_var = tk.DoubleVar(value=1.0)
        cantidad_entry = tk.Entry(cantidad_frame, textvariable=cantidad_var, 
                                 width=15, font=("Arial", 12))
        cantidad_entry.pack(side="left", padx=10)
        cantidad_entry.focus_set()
        cantidad_entry.select_range(0, tk.END)
        
        # Total calculado
        total_var = tk.StringVar()
        total_label = tk.Label(cantidad_frame, textvariable=total_var, 
                              font=("Arial", 12, "bold"), fg="#2196F3")
        total_label.pack(side="left", padx=20)
        
        def calcular_total(*args):
            try:
                cantidad = Decimal(str(cantidad_var.get()))  # Convertir a Decimal
                precio = Decimal(str(producto['precio']))     # Asegurar que precio sea Decimal
                total = cantidad * precio
                total_var.set(f"Total: ${float(total):.2f}")
            except:
                total_var.set("Total: $0.00")
        
        cantidad_var.trace("w", calcular_total)
        calcular_total()
        
        # Botones
        botones_frame = tk.Frame(dialogo)
        botones_frame.pack(pady=20)
        
        def agregar_al_carrito():
            try:
                cantidad = cantidad_var.get()
                if cantidad <= 0:
                    messagebox.showerror("Error", "La cantidad debe ser mayor que 0")
                    return
                
                # Convertir cantidad a Decimal para consistencia
                self.carrito[producto_id] = {
                    'producto': producto,
                    'cantidad': Decimal(str(cantidad))  # Guardar como Decimal
                }
                
                self.actualizar_carrito()
                self.mostrar_productos()  # Actualizar indicador "en carrito"
                dialogo.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Ingrese una cantidad válida")
        
        tk.Button(botones_frame, text="Agregar al Carrito", 
                 command=agregar_al_carrito, bg="#4CAF50", fg="white", 
                 padx=15, pady=5).pack(side="left", padx=10)
        
        tk.Button(botones_frame, text="Cancelar", 
                 command=dialogo.destroy, bg="#f44336", fg="white", 
                 padx=15, pady=5).pack(side="left", padx=10)
        
        # Enter para agregar
        cantidad_entry.bind("<Return>", lambda e: agregar_al_carrito())

    def actualizar_carrito(self):
        """Actualizar visualización del carrito"""
        # Limpiar carrito
        for item in self.carrito_tree.get_children():
            self.carrito_tree.delete(item)
        
        total_general = Decimal('0')
        
        for producto_id, item in self.carrito.items():
            producto = item['producto']
            cantidad = Decimal(str(item['cantidad']))  # Convertir a Decimal
            precio = Decimal(str(producto['precio']))  # Asegurar que precio sea Decimal
            subtotal = cantidad * precio
            total_general += subtotal
            
            self.carrito_tree.insert("", "end",
                                   values=(producto['nombre_producto'],
                                          f"{float(cantidad):.2f}",
                                          producto['unidad'],
                                          f"${float(precio):.2f}",
                                          f"${float(subtotal):.2f}"),
                                   tags=(str(producto_id),))
        
        self.total_var.set(f"Total: ${float(total_general):.2f}")
        
        # Actualizar status
        items_count = len(self.carrito)
        self.status_var.set(f"Carrito: {items_count} productos - Total: ${float(total_general):.2f}")

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
        nueva_cantidad = tk.simpledialog.askfloat(
            "Editar Cantidad",
            f"Nueva cantidad para {producto['nombre_producto']}:",
            initialvalue=cantidad_actual,
            minvalue=0.01
        )
        
        if nueva_cantidad:
            self.carrito[producto_id]['cantidad'] = Decimal(str(nueva_cantidad))  # Convertir a Decimal
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
            self.mostrar_productos()  # Actualizar indicador "en carrito"

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
        
        total_general = 0
        for item in self.carrito.values():
            producto = item['producto']
            cantidad = float(item['cantidad'])  # Convertir a float
            precio = float(producto['precio'])   # Convertir a float
            subtotal = cantidad * precio
            total_general += subtotal
            
            content += f"{producto['nombre_producto']}\n"
            content += f"  {cantidad:.2f} {producto['unidad']} x ${precio:.2f} = ${subtotal:.2f}\n\n"
        
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
        
        # Confirmar generación
        total_items = len(self.carrito)
        total_general = sum(float(item['cantidad']) * float(item['producto']['precio']) for item in self.carrito.values())
        
        mensaje = f"¿Generar recibo?\n\n"
        mensaje += f"Cliente: {self.cliente_seleccionado.get()}\n"
        mensaje += f"Productos: {total_items}\n"
        mensaje += f"Total: ${total_general:.2f}"
        
        if not messagebox.askyesno("Confirmar Recibo", mensaje):
            return
        
        # Preparar productos finales
        productos_finales = []
        for item in self.carrito.values():
            producto = item['producto']
            cantidad = float(item['cantidad'])  # Convertir Decimal a float para PDF
            precio = float(producto['precio'])  # Convertir Decimal a float para PDF
            total = cantidad * precio
            productos_finales.append((
                producto['nombre_producto'], 
                cantidad, 
                producto['unidad'], 
                precio, 
                total
            ))
        
        # Generar PDF
        self.crear_pdf(productos_finales, total_general)
        
        # Guardar en BD si está activado
        if self.guardar_en_bd.get():
            self.guardar_factura(productos_finales)
        
        # Limpiar carrito después de generar
        if messagebox.askyesno("Limpiar Carrito", "¿Desea limpiar el carrito para un nuevo recibo?"):
            self.limpiar_carrito()

    def crear_pdf(self, productos_finales, total_general):
        """Crear archivo PDF del recibo"""
        cliente = self.cliente_seleccionado.get()
        fecha = datetime.now().strftime("%Y-%m-%d")
        nombre_archivo = f"recibos/recibo_{cliente.lower().replace(' ', '_')}_{fecha}_{datetime.now().strftime('%H%M%S')}.pdf"

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Encabezado
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt="DISFRULEG", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Recibo para: {cliente}", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Fecha: {fecha}", ln=True, align="C")
        pdf.ln(10)

        # Tabla de productos
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 10, "Producto", 1)
        pdf.cell(30, 10, "Cantidad", 1)
        pdf.cell(30, 10, "Unidad", 1)
        pdf.cell(30, 10, "Precio/Unidad", 1)
        pdf.cell(40, 10, "Subtotal", 1)
        pdf.ln()

        pdf.set_font("Arial", size=10)
        for nombre, cantidad, unidad, precio_unitario, total in productos_finales:
            pdf.cell(60, 10, nombre.encode('latin1', 'replace').decode('latin1'), 1)
            pdf.cell(30, 10, f"{cantidad:.2f}", 1)
            pdf.cell(30, 10, f"{unidad}", 1)
            pdf.cell(30, 10, f"${precio_unitario:.2f}", 1)
            pdf.cell(40, 10, f"${total:.2f}", 1)
            pdf.ln()

        # Total
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(150, 10, "TOTAL", 1)
        pdf.cell(40, 10, f"${total_general:.2f}", 1)

        pdf.output(nombre_archivo)
        messagebox.showinfo("Éxito", f"Recibo guardado en {nombre_archivo}")

    def guardar_factura(self, productos_finales):
        """Guardar factura en la base de datos"""
        try:
            cursor.execute("START TRANSACTION")
            
            cursor.execute(
                "INSERT INTO factura (fecha, id_cliente) VALUES (%s, %s)",
                (datetime.now().strftime("%Y-%m-%d"), self.cliente_id)
            )
            factura_id = cursor.lastrowid
            
            for nombre, cantidad, unidad, precio_unitario, total in productos_finales:
                cursor.execute("SELECT id_producto FROM producto WHERE nombre_producto = %s", (nombre,))
                producto = cursor.fetchone()
                if producto:
                    cursor.execute(
                        "INSERT INTO detalle_factura (id_factura, id_producto, cantidad, precio_unitario_venta) VALUES (%s, %s, %s, %s)",
                        (factura_id, producto["id_producto"], cantidad, precio_unitario)
                    )
            
            conn.commit()
            self.status_var.set(f"Factura #{factura_id} guardada en base de datos")
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error al guardar en la base de datos: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReciboAppMejorado(root)
    root.mainloop()