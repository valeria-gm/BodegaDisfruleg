import os
import tkinter as tk
from tkinter import messagebox, ttk
from fpdf import FPDF
from datetime import datetime
import mysql.connector
from conexion import conectar
from decimal import Decimal



"""
# Datos simulados
clientes = [
    {"id": 1, "nombre": "Valentina"},
    {"id": 2, "nombre": "Carlos"},
    {"id": 3, "nombre": "Mariana"}
]

productos = [
    {"id": 1, "nombre": "Col morado", "precio": 50.00},
    {"id": 2, "nombre": "Huevo", "precio": 42.00},
    {"id": 3, "nombre": "Jitomate bola", "precio": 43.00},
    {"id": 4, "nombre": "Chile habanero", "precio": 75.00},
    {"id": 5, "nombre": "Rábano rojo", "precio": 45.00},
    {"id": 6, "nombre": "Frijol", "precio": 32.50},
    {"id": 7, "nombre": "Jitomate", "precio": 22.00},
    {"id": 8, "nombre": "Apio", "precio": 18.00},
    {"id": 9, "nombre": "Chorizo", "precio": 95.00},
    {"id": 10, "nombre": "Bistec de puerco", "precio": 109.00},
    {"id": 11, "nombre": "Tocino", "precio": 145.00},
    {"id": 12, "nombre": "Queso Oaxaca", "precio": 145.00},
    {"id": 13, "nombre": "Sandía", "precio": 17.00},
    {"id": 14, "nombre": "Frambuesa", "precio": 49.00}
]
"""
conn = conectar()
cursor = conn.cursor(dictionary=True)

# Obtener clientes desde la base de datos
cursor.execute("SELECT id_cliente, nombre FROM cliente")
clientes = cursor.fetchall()

# Obtener productos con precio, considerando el tipo de cliente (aquí asumo el tipo de cliente 1 para obtener los precios por defecto)
tipo_cliente_id = 1  # Aquí podrías permitir que el usuario seleccione el tipo de cliente, si es necesario.
cursor.execute("""
    SELECT p.id_producto, p.nombre_producto, p.unidad, pr.precio 
    FROM producto p
    JOIN precio pr ON p.id_producto = pr.id_producto
    WHERE pr.id_tipo = %s
""", (tipo_cliente_id,))
productos = cursor.fetchall()

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

        self.crear_interfaz()

    def crear_interfaz(self):
        tk.Label(self.root, text="Selecciona el Cliente:", font=("Arial", 14)).pack(pady=10)

        nombres_clientes = [cliente["nombre"] for cliente in clientes]
        self.cliente_combo = ttk.Combobox(self.root, textvariable=self.cliente_seleccionado, values=nombres_clientes, state="readonly")
        self.cliente_combo.pack(pady=5)

        tk.Label(self.root, text="Ingresa las unidades de cada producto:", font=("Arial", 14)).pack(pady=10)

        frame_productos = tk.Frame(self.root)
        frame_productos.pack(pady=5)

        for producto in productos:
            fila = tk.Frame(frame_productos)
            fila.pack(fill="x", pady=2)

            tk.Label(fila, text=f"{producto['nombre_producto']} - {producto['unidad']} - ${producto['precio']:.2f} por unidad", width=50, anchor="w").pack(side="left")
            entry = tk.Entry(fila, width=10)
            entry.pack(side="right", padx=5)
            self.entries_cantidades[producto["id_producto"]] = (producto, entry)

        tk.Button(self.root, text="Generar Recibo", command=self.generar_recibo).pack(pady=20)

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
        nombre_archivo = f"recibos/recibo_{cliente.lower()}_{fecha}.pdf"

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt=f"Recibo para: {cliente}", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=10)
        pdf.cell(60, 10, "Producto", 1)
        pdf.cell(30, 10, "Cantidad", 1)
        pdf.cell(40, 10, "Precio/Unidad", 1)
        pdf.cell(40, 10, "Unidad", 1)
        pdf.cell(40, 10, "Total", 1)
        pdf.ln()

        for nombre, cantidad, unidad, precio_unitario, total in productos_finales:
            pdf.cell(60, 10, nombre, 1)
            pdf.cell(30, 10, f"{cantidad:.2f} {unidad}", 1)
            pdf.cell(40, 10, f"${precio_unitario:.2f}", 1)
            pdf.cell(40, 10, f"${total:.2f}", 1)
            pdf.ln()

        pdf.ln(5)
        pdf.cell(130, 10, "TOTAL", 1)
        pdf.cell(40, 10, f"${total_general:.2f}", 1)

        pdf.output(nombre_archivo)

        messagebox.showinfo("Éxito", f"Recibo guardado en {nombre_archivo}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReciboApp(root)
    root.mainloop()
