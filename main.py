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
        self.root.geometry("700x600")

        self.cliente_seleccionado = tk.StringVar()
        self.entries_cantidades = {}
        self.frame_productos = None
        self.cliente_id = None
        self.tipo_cliente_id = None

        self.crear_interfaz()

    def crear_interfaz(self):
        tk.Label(self.root, text="Selecciona el Cliente:", font=("Arial", 14)).pack(pady=10)

        # Crear combobox con nombres de clientes
        nombres_clientes = [cliente["nombre"] for cliente in clientes]
        self.cliente_combo = ttk.Combobox(self.root, textvariable=self.cliente_seleccionado, 
                                         values=nombres_clientes, state="readonly")
        self.cliente_combo.pack(pady=5)
        self.cliente_combo.bind("<<ComboboxSelected>>", self.actualizar_precios)

        tk.Label(self.root, text="Ingresa las unidades de cada producto:", font=("Arial", 14)).pack(pady=10)

        # Crear frame para productos
        self.frame_productos = tk.Frame(self.root)
        self.frame_productos.pack(pady=5, fill="both", expand=True)

        # Botón para generar recibo
        tk.Button(self.root, text="Generar Recibo", command=self.generar_recibo).pack(pady=20)

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
        """, (self.tipo_cliente_id,))
        productos = cursor.fetchall()
        
        # Reiniciar diccionario de entradas
        self.entries_cantidades = {}
        
        # Crear entradas para cada producto con los precios actualizados
        for producto in productos:
            fila = tk.Frame(self.frame_productos)
            fila.pack(fill="x", pady=2)

            tk.Label(fila, text=f"{producto['nombre_producto']} - {producto['unidad']} - ${producto['precio']:.2f} por unidad", 
                    width=50, anchor="w").pack(side="left")
            entry = tk.Entry(fila, width=10)
            entry.pack(side="right", padx=5)
            self.entries_cantidades[producto["id_producto"]] = (producto, entry)

    def generar_recibo(self):
        if not self.cliente_seleccionado.get():
            messagebox.showerror("Error", "Debes seleccionar un cliente.")
            return

        productos_finales = []
        total_general = 0

        for producto_id, (producto, entry) in self.entries_cantidades.items():
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

        self.crear_pdf(productos_finales, total_general)

    def crear_pdf(self, productos_finales, total_general):
        cliente = self.cliente_seleccionado.get()
        fecha = datetime.now().strftime("%Y-%m-%d")
        nombre_archivo = f"recibos/recibo_{cliente.lower().replace(' ', '_')}_{fecha}.pdf"

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt=f"Recibo para: {cliente}", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=10)
        pdf.cell(60, 10, "Producto", 1)
        pdf.cell(30, 10, "Cantidad", 1)
        pdf.cell(30, 10, "Unidad", 1)
        pdf.cell(30, 10, "Precio/Unidad", 1)
        pdf.cell(30, 10, "Total", 1)
        pdf.ln()

        for nombre, cantidad, unidad, precio_unitario, total in productos_finales:
            pdf.cell(60, 10, nombre, 1)
            pdf.cell(30, 10, f"{cantidad:.2f}", 1)
            pdf.cell(30, 10, f"{unidad}", 1)
            pdf.cell(30, 10, f"${precio_unitario:.2f}", 1)
            pdf.cell(30, 10, f"${total:.2f}", 1)
            pdf.ln()

        pdf.ln(5)
        pdf.cell(150, 10, "TOTAL", 1)
        pdf.cell(30, 10, f"${total_general:.2f}", 1)

        # Guardar factura en la base de datos si se desea implementar en el futuro
        self.guardar_factura(productos_finales)

        pdf.output(nombre_archivo)

        messagebox.showinfo("Éxito", f"Recibo guardado en {nombre_archivo}")
    
    # Método opcional para guardar la factura en la base de datos
    def guardar_factura(self, productos_finales):
        try:
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
            
            conn.commit()
            messagebox.showinfo("Base de datos", "Factura guardada en la base de datos")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error al guardar en la base de datos: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReciboApp(root)
    root.mainloop()