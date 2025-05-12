import os
import tkinter as tk
from tkinter import messagebox, ttk
from fpdf import FPDF
from datetime import datetime
import mysql.connector
from conexion import conectar
from decimal import Decimal

conn = conectar()
cursor = conn.cursor(dictionary=True)

# Obtener clientes desde la base de datos con su tipo
cursor.execute("SELECT id_cliente, nombre, id_tipo FROM cliente")
clientes = cursor.fetchall()

# Crear carpeta recibos si no existe
if not os.path.exists("recibos"):
    os.makedirs("recibos")

class ReciboApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Recibos")
        self.root.geometry("700x650")  # Aumenté un poco la altura

        self.cliente_seleccionado = tk.StringVar()
        self.entries_cantidades = {}
        self.frame_productos = None
        self.cliente_id = None
        self.tipo_cliente_id = None
        
        # Variable para controlar el guardado automático
        self.guardar_en_bd = tk.BooleanVar(value=True)  # Por defecto activado

        self.crear_interfaz()

    def crear_interfaz(self):
        tk.Label(self.root, text="Selecciona el Cliente:", font=("Arial", 14)).pack(pady=10)

        # Crear combobox con nombres de clientes
        nombres_clientes = [cliente["nombre"] for cliente in clientes]
        self.cliente_combo = ttk.Combobox(self.root, textvariable=self.cliente_seleccionado, 
                                         values=nombres_clientes, state="readonly")
        self.cliente_combo.pack(pady=5)
        self.cliente_combo.bind("<<ComboboxSelected>>", self.actualizar_precios)

        # Checkbox para el guardado automático
        check_frame = tk.Frame(self.root)
        check_frame.pack(pady=5)
        
        self.check_guardar = tk.Checkbutton(check_frame, 
                                           text="Guardar automáticamente en base de datos", 
                                           variable=self.guardar_en_bd,
                                           font=("Arial", 10))
        self.check_guardar.pack()

        tk.Label(self.root, text="Ingresa las unidades de cada producto:", font=("Arial", 14)).pack(pady=10)

        # Crear frame para productos con scrollbar
        container_frame = tk.Frame(self.root)
        container_frame.pack(pady=5, fill="both", expand=True)
        
        # Canvas y scrollbar para el área de productos
        canvas = tk.Canvas(container_frame)
        scrollbar = tk.Scrollbar(container_frame, orient="vertical", command=canvas.yview)
        self.frame_productos = tk.Frame(canvas)
        
        self.frame_productos.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.frame_productos, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botones
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Generar Recibo", command=self.generar_recibo,
                  bg="#4CAF50", fg="white", padx=15, pady=5, font=("Arial", 12)).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Limpiar Todo", command=self.limpiar_todo,
                  bg="#ff9800", fg="white", padx=15, pady=5, font=("Arial", 12)).pack(side="left", padx=5)
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo - Seleccione un cliente para comenzar")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def actualizar_precios(self, event=None):
        # Limpiar productos anteriores
        for widget in self.frame_productos.winfo_children():
            widget.destroy()
        
        # Obtener el cliente seleccionado
        cliente_nombre = self.cliente_seleccionado.get()
        
        # Buscar el tipo de cliente
        for cliente in clientes:
            if cliente["nombre"] == cliente_nombre:
                self.cliente_id = cliente["id_cliente"]
                self.tipo_cliente_id = cliente["id_tipo"]
                break
        
        # Si no se encontró el tipo de cliente, usar el tipo 1 por defecto
        if not self.tipo_cliente_id:
            self.tipo_cliente_id = 1
        
        # Obtener productos con precios para este tipo de cliente
        cursor.execute("""
            SELECT p.id_producto, p.nombre_producto, p.unidad, pr.precio 
            FROM producto p
            JOIN precio pr ON p.id_producto = pr.id_producto
            WHERE pr.id_tipo = %s
            ORDER BY p.nombre_producto
        """, (self.tipo_cliente_id,))
        productos = cursor.fetchall()
        
        # Reiniciar diccionario de entradas
        self.entries_cantidades = {}
        
        # Crear entradas para cada producto con los precios actualizados
        for i, producto in enumerate(productos):
            fila = tk.Frame(self.frame_productos)
            fila.pack(fill="x", pady=2, padx=5)

            # Color alternante para mejor legibilidad
            bg_color = "#f0f0f0" if i % 2 == 0 else "#ffffff"
            fila.configure(bg=bg_color)

            tk.Label(fila, text=f"{producto['nombre_producto']}", 
                    width=35, anchor="w", bg=bg_color).pack(side="left")
            tk.Label(fila, text=f"{producto['unidad']}", 
                    width=15, anchor="center", bg=bg_color).pack(side="left")
            tk.Label(fila, text=f"${producto['precio']:.2f}", 
                    width=15, anchor="e", bg=bg_color, font=("Arial", 9, "bold")).pack(side="left")
            
            # Frame para cantidad y total
            cantidad_frame = tk.Frame(fila, bg=bg_color)
            cantidad_frame.pack(side="right", fill="x", expand=True)
            
            entry = tk.Entry(cantidad_frame, width=10, justify="center")
            entry.pack(side="left", padx=5)
            
            # Label para mostrar subtotal
            subtotal_label = tk.Label(cantidad_frame, text="$0.00", width=15, anchor="e", 
                                    bg=bg_color, font=("Arial", 9, "bold"), fg="#2196F3")
            subtotal_label.pack(side="right", padx=5)
            
            # Guardar referencia con subtotal label
            self.entries_cantidades[producto["id_producto"]] = (producto, entry, subtotal_label)
            
            # Conectar evento para calcular subtotal automáticamente
            entry.bind("<KeyRelease>", lambda e, p=producto, l=subtotal_label: self.calcular_subtotal(e, p, l))
        
        self.status_var.set(f"Cliente seleccionado: {cliente_nombre} - {len(productos)} productos disponibles")

    def calcular_subtotal(self, event, producto, subtotal_label):
        """Calcular subtotal para un producto"""
        try:
            cantidad = float(event.widget.get()) if event.widget.get() else 0
            subtotal = cantidad * producto["precio"]
            subtotal_label.config(text=f"${subtotal:.2f}")
            
            # Actualizar total general
            self.calcular_total_general()
        except ValueError:
            subtotal_label.config(text="$0.00")

    def calcular_total_general(self):
        """Calcular y mostrar total general"""
        total_general = 0
        productos_con_cantidad = 0
        
        for producto_id, (producto, entry, subtotal_label) in self.entries_cantidades.items():
            try:
                cantidad = float(entry.get()) if entry.get() else 0
                if cantidad > 0:
                    productos_con_cantidad += 1
                    total_general += cantidad * producto["precio"]
            except ValueError:
                continue
        
        self.status_var.set(f"Total: ${total_general:.2f} - {productos_con_cantidad} productos con cantidad")

    def limpiar_todo(self):
        """Limpiar todos los campos"""
        for producto_id, (producto, entry, subtotal_label) in self.entries_cantidades.items():
            entry.delete(0, tk.END)
            subtotal_label.config(text="$0.00")
        self.status_var.set("Campos limpiados")

    def generar_recibo(self):
        if not self.cliente_seleccionado.get():
            messagebox.showerror("Error", "Debes seleccionar un cliente.")
            return

        productos_finales = []
        total_general = 0

        for producto_id, (producto, entry, subtotal_label) in self.entries_cantidades.items():
            try:
                cantidad = float(entry.get())
            except ValueError:
                cantidad = 0

            if cantidad > 0:
                total = Decimal(str(cantidad)) * producto["precio"]
                productos_finales.append((producto["nombre_producto"], cantidad, producto["unidad"], producto["precio"], total))
                total_general += total

        if not productos_finales:
            messagebox.showerror("Error", "Debes ingresar al menos un producto con cantidad mayor a 0.")
            return

        # Generar PDF
        self.crear_pdf(productos_finales, total_general)
        
        # Guardar en base de datos si está activado
        if self.guardar_en_bd.get():
            self.guardar_factura(productos_finales)

    def crear_pdf(self, productos_finales, total_general):
        cliente = self.cliente_seleccionado.get()
        fecha = datetime.now().strftime("%Y-%m-%d")
        nombre_archivo = f"recibos/recibo_{cliente.lower().replace(' ', '_')}_{fecha}_{datetime.now().strftime('%H%M%S')}.pdf"

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Encabezado mejorado
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
            # Iniciar transacción
            cursor.execute("START TRANSACTION")
            
            # Insertar factura
            cursor.execute(
                "INSERT INTO factura (fecha, id_cliente) VALUES (%s, %s)",
                (datetime.now().strftime("%Y-%m-%d"), self.cliente_id)
            )
            factura_id = cursor.lastrowid
            
            # Insertar detalles de factura
            for nombre, cantidad, unidad, precio_unitario, total in productos_finales:
                # Buscar id del producto por nombre
                cursor.execute("SELECT id_producto FROM producto WHERE nombre_producto = %s", (nombre,))
                producto = cursor.fetchone()
                if producto:
                    cursor.execute(
                        "INSERT INTO detalle_factura (id_factura, id_producto, cantidad, precio_unitario_compra) VALUES (%s, %s, %s, %s)",
                        (factura_id, producto["id_producto"], cantidad, precio_unitario)
                    )
            
            # Confirmar transacción
            conn.commit()
            self.status_var.set(f"Factura #{factura_id} guardada en base de datos exitosamente")
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error al guardar en la base de datos: {str(e)}")
            print(f"Error detallado: {e}")  # Para debugging

if __name__ == "__main__":
    root = tk.Tk()
    app = ReciboApp(root)
    root.mainloop()