import os
import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from conexion import conectar
from decimal import Decimal
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
from collections import defaultdict
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime

class AnalisisGananciasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de Ganancias - Disfruleg")
        self.root.geometry("1000x700")
        
        # Connect to database
        try:
            self.conn = conectar()
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as err:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{err}")
            self.root.destroy()
        
        self.create_interface()
        self.load_analysis()
        
    def create_interface(self):
        # Title
        title_frame = tk.Frame(self.root)
        title_frame.pack(fill="x", pady=10)
        
        tk.Label(title_frame, text="ANÁLISIS DE GANANCIAS POR PRODUCTO", 
                font=("Arial", 18, "bold")).pack()
        
        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", pady=5, padx=10)
        
        tk.Button(button_frame, text="Actualizar Análisis", command=self.load_analysis, 
                  bg="#4CAF50", fg="white", padx=10, pady=3).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Exportar PDF", command=self.export_to_pdf, 
                  bg="#2196F3", fg="white", padx=10, pady=3).pack(side="left", padx=5)
        
        #tk.Button(button_frame, text="Ver Gráfico", command=self.show_chart, 
                  #bg="#FF5722", fg="white", padx=10, pady=3).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Estadísticas Avanzadas", command=self.show_advanced_stats,
                  bg="#9C27B0", fg="white", padx=10, pady=3).pack(side="left", padx=5)

        # Create main container with two sections
        main_container = tk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Summary section (top)
        self.create_summary_section(main_container)
        
        # Detail table (bottom)
        self.create_detail_section(main_container)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Listo")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_summary_section(self, parent):
        # Summary frame
        summary_frame = tk.LabelFrame(parent, text="Resumen General", padx=10, pady=10)
        summary_frame.pack(fill="x", pady=(0, 10))
        
        # Create grid for summary cards
        summary_grid = tk.Frame(summary_frame)
        summary_grid.pack(fill="x")
        
        # Variables for summary
        self.total_ventas_var = tk.StringVar(value="$0.00")
        self.total_costos_var = tk.StringVar(value="$0.00")
        self.ganancia_total_var = tk.StringVar(value="$0.00")
        self.margen_promedio_var = tk.StringVar(value="0%")
        
        # Create summary cards
        self.create_summary_card(summary_grid, "Ventas Totales", self.total_ventas_var, "#4CAF50", 0, 0)
        self.create_summary_card(summary_grid, "Costos Totales", self.total_costos_var, "#f44336", 0, 1)
        self.create_summary_card(summary_grid, "Ganancia Total", self.ganancia_total_var, "#2196F3", 0, 2)
        self.create_summary_card(summary_grid, "Margen Promedio", self.margen_promedio_var, "#FF5722", 0, 3)
    
    def create_summary_card(self, parent, title, text_var, color, row, col):
        card = tk.Frame(parent, bg=color, relief=tk.RAISED, bd=2)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        parent.columnconfigure(col, weight=1)
        
        tk.Label(card, text=title, font=("Arial", 10), bg=color, fg="white").pack(pady=5)
        tk.Label(card, textvariable=text_var, font=("Arial", 14, "bold"), 
                bg=color, fg="white").pack(pady=5)
    
    def create_detail_section(self, parent):
        # Detail frame
        detail_frame = tk.LabelFrame(parent, text="Detalles por Producto", padx=10, pady=10)
        detail_frame.pack(fill="both", expand=True)
        
        # Search frame
        search_frame = tk.Frame(detail_frame)
        search_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(search_frame, text="Buscar producto:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        self.search_var.trace("w", self.filter_products)
        
        # Filter buttons
        filter_frame = tk.Frame(search_frame)
        filter_frame.pack(side="right")
        
        tk.Button(filter_frame, text="Solo con Ganancia", command=lambda: self.apply_filter("ganancia"),
                  bg="#4CAF50", fg="white", padx=10, pady=3).pack(side="left", padx=2)
        tk.Button(filter_frame, text="Solo con Pérdida", command=lambda: self.apply_filter("perdida"),
                  bg="#f44336", fg="white", padx=10, pady=3).pack(side="left", padx=2)
        tk.Button(filter_frame, text="Mostrar Todo", command=lambda: self.apply_filter("todos"),
                  bg="#607D8B", fg="white", padx=10, pady=3).pack(side="left", padx=2)
        
        # Create treeview
        self.create_treeview(detail_frame)
    
    def create_treeview(self, parent):
        # Frame for table with scrollbar
        table_frame = tk.Frame(parent)
        table_frame.pack(fill="both", expand=True)
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(table_frame)
        v_scrollbar.pack(side="right", fill="y")
        
        h_scrollbar = tk.Scrollbar(table_frame, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Treeview
        columns = ("id", "producto", "unidad", "vendido", "precio_venta", 
                  "ingresos", "comprado", "precio_compra", "costos", 
                  "ganancia", "margen", "stock")
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                               yscrollcommand=v_scrollbar.set,
                               xscrollcommand=h_scrollbar.set)
        
        # Configure columns
        column_configs = {
            "id": ("ID", 50),
            "producto": ("Producto", 150),
            "unidad": ("Unidad", 70),
            "vendido": ("Cant. Vendida", 80),
            "precio_venta": ("Precio Venta", 90),
            "ingresos": ("Ingresos", 90),
            "comprado": ("Cant. Comprada", 90),
            "precio_compra": ("Precio Compra", 90),
            "costos": ("Costos", 90),
            "ganancia": ("Ganancia", 90),
            "margen": ("Margen %", 80),
            "stock": ("Stock Est.", 80)
        }
        
        for col, (heading, width) in column_configs.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
    
    def load_analysis(self):
        """Load profitability analysis from database"""
        try:
            # Main query for product analysis
            self.cursor.execute("""
                SELECT 
                    p.id_producto,
                    p.nombre_producto,
                    p.unidad,
                    
                    -- Ventas
                    COALESCE(SUM(df.cantidad), 0) as cantidad_vendida,
                    COALESCE(AVG(df.precio_unitario_venta), 0) as precio_promedio_venta,
                    COALESCE(SUM(df.subtotal), 0) as ingresos_totales,
                    
                    -- Compras
                    COALESCE(SUM(c.cantidad), 0) as cantidad_comprada,
                    COALESCE(AVG(c.precio_unitario_compra), 0) as precio_promedio_compra,
                    COALESCE(SUM(c.cantidad * c.precio_unitario_compra), 0) as costos_totales,
                    
                    -- Ganancias
                    COALESCE(SUM(df.subtotal), 0) - COALESCE(SUM(c.cantidad * c.precio_unitario_compra), 0) as ganancia_total,
                    
                    -- Margen
                    CASE 
                        WHEN COALESCE(SUM(c.cantidad * c.precio_unitario_compra), 0) = 0 THEN 0
                        ELSE ROUND(((COALESCE(SUM(df.subtotal), 0) - COALESCE(SUM(c.cantidad * c.precio_unitario_compra), 0)) / 
                                    COALESCE(SUM(c.cantidad * c.precio_unitario_compra), 0)) * 100, 2)
                    END as margen_ganancia_porcentaje
                    
                FROM producto p
                LEFT JOIN detalle_factura df ON p.id_producto = df.id_producto
                LEFT JOIN compra c ON p.id_producto = c.id_producto
                GROUP BY p.id_producto, p.nombre_producto, p.unidad
                ORDER BY ganancia_total DESC
            """)
            
            products = self.cursor.fetchall()
            self.all_products = products
            
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Calculate totals for summary
            total_ventas = sum(p['ingresos_totales'] for p in products)
            total_costos = sum(p['costos_totales'] for p in products)
            ganancia_total = total_ventas - total_costos
            
            # Calculate average margin
            productos_con_margen = [p for p in products if p['margen_ganancia_porcentaje'] != 0]
            margen_promedio = (sum(p['margen_ganancia_porcentaje'] for p in productos_con_margen) / 
                              len(productos_con_margen)) if productos_con_margen else 0
            
            # Update summary
            self.total_ventas_var.set(f"${total_ventas:.2f}")
            self.total_costos_var.set(f"${total_costos:.2f}")
            self.ganancia_total_var.set(f"${ganancia_total:.2f}")
            self.margen_promedio_var.set(f"{margen_promedio:.1f}%")
            
            # Populate tree
            for product in products:
                # Calculate stock
                stock = product['cantidad_comprada'] - product['cantidad_vendida']
                
                # Color coding for ganancia
                ganancia = product['ganancia_total']
                if ganancia > 0:
                    tags = ('positive',)
                elif ganancia < 0:
                    tags = ('negative',)
                else:
                    tags = ('neutral',)
                
                self.tree.insert("", "end", values=(
                    product['id_producto'],
                    product['nombre_producto'],
                    product['unidad'],
                    f"{product['cantidad_vendida']:.2f}",
                    f"${product['precio_promedio_venta']:.2f}",
                    f"${product['ingresos_totales']:.2f}",
                    f"{product['cantidad_comprada']:.2f}",
                    f"${product['precio_promedio_compra']:.2f}",
                    f"${product['costos_totales']:.2f}",
                    f"${product['ganancia_total']:.2f}",
                    f"{product['margen_ganancia_porcentaje']:.1f}%",
                    f"{stock:.2f}"
                ), tags=tags)
            
            # Configure tags for color coding
            self.tree.tag_configure('positive', background='#E8F5E9')
            self.tree.tag_configure('negative', background='#FFEBEE')
            self.tree.tag_configure('neutral', background='#F5F5F5')
            
            self.status_var.set(f"Análisis actualizado - {len(products)} productos analizados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar análisis: {str(e)}")
            print(f"Error: {e}")
    
    def filter_products(self, *args):
        """Filter products based on search text"""
        search_text = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter products
        for product in self.all_products:
            if search_text in product['nombre_producto'].lower():
                stock = product['cantidad_comprada'] - product['cantidad_vendida']
                
                ganancia = product['ganancia_total']
                if ganancia > 0:
                    tags = ('positive',)
                elif ganancia < 0:
                    tags = ('negative',)
                else:
                    tags = ('neutral',)
                
                self.tree.insert("", "end", values=(
                    product['id_producto'],
                    product['nombre_producto'],
                    product['unidad'],
                    f"{product['cantidad_vendida']:.2f}",
                    f"${product['precio_promedio_venta']:.2f}",
                    f"${product['ingresos_totales']:.2f}",
                    f"{product['cantidad_comprada']:.2f}",
                    f"${product['precio_promedio_compra']:.2f}",
                    f"${product['costos_totales']:.2f}",
                    f"${product['ganancia_total']:.2f}",
                    f"{product['margen_ganancia_porcentaje']:.1f}%",
                    f"{stock:.2f}"
                ), tags=tags)
    
    def apply_filter(self, filter_type):
        """Apply specific filters"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter based on type
        for product in self.all_products:
            ganancia = product['ganancia_total']
            
            should_include = False
            if filter_type == "ganancia" and ganancia > 0:
                should_include = True
            elif filter_type == "perdida" and ganancia < 0:
                should_include = True
            elif filter_type == "todos":
                should_include = True
            
            if should_include:
                stock = product['cantidad_comprada'] - product['cantidad_vendida']
                
                if ganancia > 0:
                    tags = ('positive',)
                elif ganancia < 0:
                    tags = ('negative',)
                else:
                    tags = ('neutral',)
                
                self.tree.insert("", "end", values=(
                    product['id_producto'],
                    product['nombre_producto'],
                    product['unidad'],
                    f"{product['cantidad_vendida']:.2f}",
                    f"${product['precio_promedio_venta']:.2f}",
                    f"${product['ingresos_totales']:.2f}",
                    f"{product['cantidad_comprada']:.2f}",
                    f"${product['precio_promedio_compra']:.2f}",
                    f"${product['costos_totales']:.2f}",
                    f"${product['ganancia_total']:.2f}",
                    f"{product['margen_ganancia_porcentaje']:.1f}%",
                    f"{stock:.2f}"
                ), tags=tags)

    def show_advanced_stats(self):
        """Muestra estadísticas avanzadas con visualizaciones interactivas."""
        
        class StatsWindow:
            def __init__(self, parent, db_cursor, db_connection):
                self.parent = parent
                self.cursor = db_cursor
                self.conn = db_connection
                self.window = tk.Toplevel(parent)
                self.window.title("Estadísticas Avanzadas - Disfruleg")
                self.window.geometry("1200x850")
                self.window.protocol("WM_DELETE_WINDOW", self.cleanup)
                
                # Configuración de estilo
                self.style = ttk.Style()
                self.style.configure("TNotebook.Tab", font=('Arial', 10, 'bold'))
                
                self.setup_ui()
                self.load_data()

            def ensure_decimal(self, value):
                """Asegura que el valor sea Decimal, convirtiéndolo si es necesario."""
                if value is None:
                    return Decimal('0.0')
                if isinstance(value, Decimal):
                    return value
                return Decimal(str(value))
                
            def convert_decimal(self, value):
                """Convierte valores Decimal de MySQL a float para matplotlib."""
                if value is None:
                    return 0.0
                return float(value)
                
            def setup_ui(self):
                """Configura la interfaz de usuario principal."""
                self.notebook = ttk.Notebook(self.window)
                self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Pestañas principales
                self.tabs = {
                    "sales": self.create_tab("Ventas y Pérdidas por Producto"),
                    "profits": self.create_tab("Ganancias"),
                    "temporal": self.create_tab("Tendencias Temporales"),
                    "clients": self.create_tab("Clientes")
                }
                
                # Barra de estado
                self.status_var = tk.StringVar()
                self.status_bar = ttk.Label(
                    self.window, 
                    textvariable=self.status_var,
                    relief="sunken",
                    anchor="w"
                )
                self.status_bar.pack(side="bottom", fill="x")
                
            def create_tab(self, name):
                """Crea una pestaña con contenedor para gráficos."""
                frame = ttk.Frame(self.notebook)
                self.notebook.add(frame, text=name)
                
                container = ttk.Frame(frame)
                container.pack(fill="both", expand=True)
                
                return {
                    "frame": frame,
                    "container": container,
                    "current_figure": None
                }
                
            def load_data(self):
                """Carga los datos y genera visualizaciones."""
                self.status_var.set("Cargando datos...")
                self.window.update_idletasks()
                
                try:
                    # Cargar datos en segundo plano para no bloquear la UI
                    self.window.after(100, self.generate_all_charts)
                except Exception as e:
                    messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
                    self.window.destroy()
                    
            def generate_all_charts(self):
                """Genera todas las visualizaciones."""
                try:
                    self.generate_sales_chart()
                    self.generate_profits_chart()
                    self.generate_temporal_chart()
                    self.generate_clients_chart()
                    self.status_var.set("Listo")
                except Exception as e:
                    self.status_var.set(f"Error: {str(e)}")
                    messagebox.showerror("Error", f"No se pudieron generar todos los gráficos: {str(e)}")
                    
            def generate_sales_chart(self):
                 """Genera gráficos de productos rentables y con pérdidas."""
                 try:
                    # Obtener todos los productos con sus ganancias
                    self.cursor.execute("""
                        SELECT 
                            p.nombre_producto,
                            COALESCE(SUM(df.subtotal), 0) - COALESCE(SUM(c.cantidad * c.precio_unitario_compra), 0) AS ganancia_total
                        FROM producto p
                        LEFT JOIN detalle_factura df ON df.id_producto = p.id_producto
                        LEFT JOIN compra c ON c.id_producto = p.id_producto
                        GROUP BY p.id_producto, p.nombre_producto
                        HAVING ganancia_total IS NOT NULL
                        ORDER BY ganancia_total DESC
                    """)
                    all_products = self.cursor.fetchall()
                    
                    # Filtrar productos rentables (top 10)
                    profitable_products = sorted([p for p in all_products if p['ganancia_total'] > 0],
                                            key=lambda x: x['ganancia_total'], reverse=True)[:10]
                    
                    # Filtrar productos con pérdidas (top 10)
                    loss_products = sorted([p for p in all_products if p['ganancia_total'] < 0],
                                        key=lambda x: x['ganancia_total'])[:10]
                    
                    if not profitable_products and not loss_products:
                        self.show_no_data_message(self.tabs["sales"]["container"])
                        return
                    
                    fig = plt.Figure(figsize=(12, 10))
                    
                    # Gráfico de productos rentables
                    if profitable_products:
                        ax1 = fig.add_subplot(2, 1, 1)
                        names = [p['nombre_producto'][:15] + '...' if len(p['nombre_producto']) > 15 
                                else p['nombre_producto'] for p in profitable_products]
                        ganancias = [self.ensure_decimal(p['ganancia_total']) for p in profitable_products]
                        
                        bars = ax1.bar(names, ganancias, color='#4CAF50')
                        ax1.set_title('Top 10 Productos Más Rentables')
                        ax1.set_ylabel('Ganancia ($)')
                        ax1.tick_params(axis='x', rotation=45)
                        
                        # Añadir etiquetas de valor
                        for bar, ganancia in zip(bars, ganancias):
                            height = bar.get_height()
                            ax1.text(bar.get_x() + bar.get_width()/2., height,
                                    f'${float(ganancia):,.0f}', 
                                    ha='center', va='bottom')
                    
                    # Gráfico de productos con pérdidas
                    if loss_products:
                        ax2 = fig.add_subplot(2, 1, 2)
                        names = [p['nombre_producto'][:15] + '...' if len(p['nombre_producto']) > 15 
                                else p['nombre_producto'] for p in loss_products]
                        perdidas = [abs(self.ensure_decimal(p['ganancia_total'])) for p in loss_products]
                        
                        bars = ax2.bar(names, perdidas, color='#f44336')
                        ax2.set_title('Top 10 Productos con Mayor Pérdida')
                        ax2.set_ylabel('Pérdida ($)')
                        ax2.tick_params(axis='x', rotation=45)
                        
                        # Añadir etiquetas de valor
                        for bar, perdida in zip(bars, perdidas):
                            height = bar.get_height()
                            ax2.text(bar.get_x() + bar.get_width()/2., height,
                                    f'${float(perdida):,.0f}', 
                                    ha='center', va='bottom')
                    
                    plt.tight_layout()
                    self.embed_plot(fig, self.tabs["sales"]["container"])
                    
                 except Exception as e:
                    self.show_error_message(self.tabs["sales"]["container"], str(e))

            def generate_profits_chart(self):
                """Genera gráfico de ganancias por producto."""
                try:
                    self.cursor.execute("""
                        SELECT 
                            p.id_producto,
                            p.nombre_producto,
                            COALESCE((
                                SELECT SUM(df.subtotal) 
                                FROM detalle_factura df 
                                WHERE df.id_producto = p.id_producto
                            ), 0) AS total_ventas,
                            COALESCE((
                                SELECT SUM(c.cantidad * c.precio_unitario_compra) 
                                FROM compra c 
                                WHERE c.id_producto = p.id_producto
                            ), 0) AS total_compras,
                            COALESCE((
                                SELECT SUM(df.subtotal) 
                                FROM detalle_factura df 
                                WHERE df.id_producto = p.id_producto
                            ), 0) - COALESCE((
                                SELECT SUM(c.cantidad * c.precio_unitario_compra) 
                                FROM compra c 
                                WHERE c.id_producto = p.id_producto
                            ), 0) AS ganancia
                        FROM producto p
                        HAVING ganancia IS NOT NULL
                        ORDER BY ganancia DESC
                        LIMIT 20
                    """)
                    data = self.cursor.fetchall()
                
                    if not data:
                        self.show_no_data_message(self.tabs["profits"]["container"])
                        return
                    
                    fig, ax = plt.subplots(figsize=(12, 6))
                    
                    # Formateador para valores monetarios
                    formatter = FuncFormatter(lambda x, _: f"${x:,.2f}")
                    ax.xaxis.set_major_formatter(formatter)
                    
                    # Convertir valores usando ensure_decimal
                    ganancias = [self.ensure_decimal(p['ganancia']) for p in data]
                    nombres = [p['nombre_producto'][:20] + ('...' if len(p['nombre_producto']) > 20 else '') 
                            for p in data]
                    
                    # Convertir a float solo para matplotlib
                    ganancias_float = [float(g) for g in ganancias]
                    
                    bars = ax.barh(nombres, ganancias_float, color='#2196F3')
                    ax.set_title("Ganancia por Producto (Top 20)\n(Ventas - Compras)")
                    ax.set_xlabel("Ganancia Total ($)")
                    
                    # Añadir etiquetas de valor
                    max_val = max(abs(g) for g in ganancias_float) if ganancias_float else 0
                    for bar, ganancia in zip(bars, ganancias):
                        width = bar.get_width()
                        ax.text(width + (max_val * 0.02),
                            bar.get_y() + bar.get_height()/2,
                            f"${ganancia:,.2f}",
                            va='center', ha='left', fontsize=8)
                    
                    plt.tight_layout()
                    self.embed_plot(fig, self.tabs["profits"]["container"])
                    
                except Exception as e:
                    self.show_error_message(self.tabs["profits"]["container"], str(e))
                    
            def generate_temporal_chart(self):
                """Genera gráfico temporal con selector de período."""
                try:
                    frame = self.tabs["temporal"]["frame"]
                    
                    # Frame de controles
                    control_frame = ttk.Frame(frame)
                    control_frame.pack(fill="x", padx=10, pady=5)
                    
                    ttk.Label(control_frame, text="Agrupar por:").pack(side="left")
                    
                    self.time_var = tk.StringVar(value="Mes")
                    options = {
                        "Día": "day",
                        "Semana": "week",
                        "Mes": "month",
                        "Trimestre": "quarter",
                        "Año": "year"
                    }
                    
                    combo = ttk.Combobox(
                        control_frame,
                        textvariable=self.time_var,
                        values=list(options.keys()),
                        state="readonly"
                    )
                    combo.pack(side="left", padx=5)
                    combo.bind("<<ComboboxSelected>>", self.update_temporal_chart)
                    
                    # Frame del gráfico
                    self.tabs["temporal"]["graph_frame"] = ttk.Frame(frame)
                    self.tabs["temporal"]["graph_frame"].pack(fill="both", expand=True)
                    
                    self.update_temporal_chart()
                    
                except Exception as e:
                    self.show_error_message(self.tabs["temporal"]["container"], str(e))
                    
            def update_temporal_chart(self, event=None):
                 """Actualiza el gráfico temporal según la selección."""
                 try:
                    period_map = {
                        "Día": ("DATE(factura.fecha)", "Día"),
                        "Semana": ("DATE_FORMAT(factura.fecha, '%Y-%U')", "Semana"),
                        "Mes": ("DATE_FORMAT(factura.fecha, '%Y-%m')", "Mes"),
                        "Trimestre": ("CONCAT(YEAR(factura.fecha), '-Q', QUARTER(factura.fecha))", "Trimestre"),
                        "Año": ("YEAR(factura.fecha)", "Año")
                    }
                    
                    selected = self.time_var.get()
                    period_func, period_label = period_map.get(selected, period_map["Mes"])
                    
                    # Consulta para ventas
                    self.cursor.execute(f"""
                        SELECT 
                            {period_func} AS periodo,
                            SUM(detalle_factura.subtotal) AS ventas
                        FROM factura
                        JOIN detalle_factura ON detalle_factura.id_factura = factura.id_factura
                        GROUP BY {period_func}
                        ORDER BY periodo
                    """)
                    ventas_data = self.cursor.fetchall()
                    
                    # Consulta para compras
                    self.cursor.execute(f"""
                        SELECT 
                            {period_func.replace('factura.', 'compra.')} AS periodo,
                            SUM(compra.cantidad * compra.precio_unitario_compra) AS compras
                        FROM compra
                        GROUP BY {period_func.replace('factura.', 'compra.')}
                        ORDER BY periodo
                    """)
                    compras_data = self.cursor.fetchall()
                    
                    # Convertir a diccionarios para facilitar el procesamiento
                    ventas_dict = {v['periodo']: self.convert_decimal(v['ventas']) for v in ventas_data}
                    compras_dict = {c['periodo']: self.convert_decimal(c['compras']) for c in compras_data}
                    
                    # Obtener todos los periodos únicos
                    all_periods = sorted(set(ventas_dict.keys()).union(set(compras_dict.keys())))
                    
                    if not all_periods:
                        self.show_no_data_message(self.tabs["temporal"]["graph_frame"])
                        return
                    
                    # Preparar datos para el gráfico
                    periods = []
                    ventas = []
                    compras = []
                    ganancias = []
                    
                    for periodo in all_periods:
                        venta = ventas_dict.get(periodo, 0.0)
                        compra = compras_dict.get(periodo, 0.0)
                        ganancia = venta - compra
                        
                        periods.append(str(periodo))
                        ventas.append(venta)
                        compras.append(compra)
                        ganancias.append(ganancia)
                    
                    fig, ax = plt.subplots(figsize=(12, 6))
                    
                    # Formateador para valores monetarios
                    formatter = FuncFormatter(lambda x, _: f"${x:,.2f}")
                    ax.yaxis.set_major_formatter(formatter)
                    
                    # Gráfico de línea para la ganancia neta
                    line = ax.plot(periods, ganancias, marker='o', color='#9C27B0', linewidth=2)
                    ax.set_title(f"Ganancias Netas por {period_label}")
                    ax.set_ylabel("Ganancia Neta ($)")
                    ax.set_xlabel(period_label)
                    ax.grid(True, linestyle='--', alpha=0.6)
                    
                    # Rotar etiquetas si hay muchas
                    if len(periods) > 8:
                        plt.xticks(rotation=45, ha='right')
                    
                    # Añadir etiquetas de valor a los puntos
                    max_val = max(abs(g) for g in ganancias) if ganancias else 0
                    for i, (period, ganancia) in enumerate(zip(periods, ganancias)):
                        ax.text(i, ganancia + (max_val * 0.05), 
                            f"${ganancia:,.2f}", 
                            ha='center', va='bottom', fontsize=8)
                    
                    plt.tight_layout()
                    self.embed_plot(fig, self.tabs["temporal"]["graph_frame"])
                    
                 except Exception as e:
                    self.show_error_message(self.tabs["temporal"]["graph_frame"], str(e))
                    
            def generate_clients_chart(self):
                """Genera gráfico de ventas por cliente."""
                try:
                    self.cursor.execute("""
                        SELECT 
                            c.nombre,
                            SUM(df.subtotal) AS total_vendido
                        FROM cliente c
                        JOIN factura f ON f.id_cliente = c.id_cliente
                        JOIN detalle_factura df ON df.id_factura = f.id_factura
                        GROUP BY c.id_cliente
                        ORDER BY total_vendido DESC
                        LIMIT 15
                    """)
                    data = self.cursor.fetchall()
                    
                    if not data:
                        self.show_no_data_message(self.tabs["clients"]["container"])
                        return
                    
                    fig, ax = plt.subplots(figsize=(12, 6))
                    
                    # Formateador para valores monetarios
                    formatter = FuncFormatter(lambda x, _: f"${x:,.2f}")
                    ax.yaxis.set_major_formatter(formatter)
                    
                    clients = [d['nombre'][:20] + ('...' if len(d['nombre']) > 20 else '') for d in data]
                    # Convertir valores Decimal a float
                    amounts = [self.convert_decimal(d['total_vendido']) for d in data]
                    
                    bars = ax.bar(clients, amounts, color='#FF9800')
                    ax.set_title("Ventas por Cliente (Top 15)")
                    ax.set_ylabel("Total Vendido")
                    
                    # Añadir etiquetas de valor
                    for bar, amount in zip(bars, amounts):
                        height = bar.get_height()
                        ax.text(
                            bar.get_x() + bar.get_width()/2., height,
                            f"${amount:,.2f}",
                            ha='center', va='bottom',
                            fontsize=8
                        )
                    
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    self.embed_plot(fig, self.tabs["clients"]["container"])
                    
                except Exception as e:
                    self.show_error_message(self.tabs["clients"]["container"], str(e))
                    
            def embed_plot(self, fig, container):
                """Inserta un gráfico matplotlib en el frame especificado."""
                for widget in container.winfo_children():
                    widget.destroy()
                    
                try:
                    canvas = FigureCanvasTkAgg(fig, master=container)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill="both", expand=True)
                    
                    # Añadir barra de herramientas
                    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
                    toolbar = NavigationToolbar2Tk(canvas, container)
                    toolbar.update()
                    canvas.get_tk_widget().pack(fill="both", expand=True)
                    
                    # Guardar referencia para evitar garbage collection
                    if hasattr(self, 'current_figure'):
                        # Cerrar la figura anterior si existe
                        old_fig, old_canvas, old_toolbar = self.current_figure
                        plt.close(old_fig)
                    
                    self.current_figure = (fig, canvas, toolbar)
                    
                except Exception as e:
                    self.show_error_message(container, f"Error al mostrar gráfico: {str(e)}")
                    
            def show_no_data_message(self, container):
                """Muestra mensaje cuando no hay datos disponibles."""
                for widget in container.winfo_children():
                    widget.destroy()
                    
                label = ttk.Label(
                    container,
                    text="No hay datos disponibles para esta visualización",
                    font=('Arial', 10, 'italic'),
                    foreground='gray'
                )
                label.pack(expand=True)
                
            def show_error_message(self, container, error):
                """Muestra mensaje de error."""
                for widget in container.winfo_children():
                    widget.destroy()
                    
                label = ttk.Label(
                    container,
                    text=f"Error: {error}",
                    font=('Arial', 10),
                    foreground='red'
                )
                label.pack(expand=True)
                
            def cleanup(self):
                """Limpia recursos antes de cerrar la ventana."""
                try:
                    if hasattr(self, 'current_figure'):
                        fig, canvas, toolbar = self.current_figure
                        plt.close(fig)
                    
                    self.window.destroy()
                except Exception as e:
                    print(f"Error durante cleanup: {e}")
                    self.window.destroy()
        
        # Crear e iniciar la ventana de estadísticas
        StatsWindow(self.root, self.cursor, self.conn)
    
    def export_to_pdf(self):
        """Exporta las estadísticas del día a un archivo PDF"""
        try:
            # Crear la carpeta reportes si no existe
            reportes_dir = "reportes"
            if not os.path.exists(reportes_dir):
                os.makedirs(reportes_dir)

            # Obtener la fecha actual
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            
            # Crear el nombre del archivo PDF
            filename = os.path.join(reportes_dir, f"Reporte_Diario_{fecha_actual}.pdf")
            
            # Crear el documento PDF
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Título del reporte
            title = Paragraph(f"Reporte Diario - {fecha_actual}", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Obtener datos de ventas del día
            self.cursor.execute("""
                SELECT 
                    p.nombre_producto,
                    df.cantidad,
                    p.unidad,
                    df.precio_unitario_venta,
                    df.subtotal,
                    c.nombre as cliente_nombre,
                    tc.nombre as tipo_cliente
                FROM detalle_factura df
                JOIN producto p ON df.id_producto = p.id_producto
                JOIN factura f ON df.id_factura = f.id_factura
                JOIN cliente c ON f.id_cliente = c.id_cliente
                JOIN tipo_cliente tc ON c.id_tipo = tc.id_tipo
                WHERE DATE(f.fecha) = CURDATE()
                ORDER BY f.id_factura
            """)
            ventas = self.cursor.fetchall()
            
            # Obtener datos de compras del día
            self.cursor.execute("""
                SELECT 
                    p.nombre_producto,
                    c.cantidad,
                    p.unidad,
                    c.precio_unitario_compra,
                    (c.cantidad * c.precio_unitario_compra) as subtotal
                FROM compra c
                JOIN producto p ON c.id_producto = p.id_producto
                WHERE DATE(c.fecha) = CURDATE()
                ORDER BY c.id_compra
            """)
            compras = self.cursor.fetchall()
            
            # Calcular totales
            total_ventas = sum(v['subtotal'] for v in ventas)
            total_compras = sum(c['subtotal'] for c in compras)
            ganancia_neta = total_ventas - total_compras
            
            # Sección de Ventas
            story.append(Paragraph("Ventas del Día", styles['Heading2']))
            
            if ventas:
                # Preparar datos para la tabla de ventas
                ventas_data = [["Producto", "Cantidad", "Unidad", "Precio/U", "Subtotal", "Cliente", "Tipo Cliente"]]
                for v in ventas:
                    ventas_data.append([
                        v['nombre_producto'],
                        f"{v['cantidad']:.2f}",
                        v['unidad'],
                        f"${v['precio_unitario_venta']:.2f}",
                        f"${v['subtotal']:.2f}",
                        v['cliente_nombre'],
                        v['tipo_cliente']
                    ])
                
                # Crear tabla de ventas
                ventas_table = Table(ventas_data)
                ventas_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(ventas_table)
                story.append(Spacer(1, 12))
                
                # Total ventas
                story.append(Paragraph(f"Total Ventas: ${total_ventas:.2f}", styles['Heading3']))
                story.append(Spacer(1, 12))
            else:
                story.append(Paragraph("No hubo ventas hoy.", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Sección de Compras
            story.append(Paragraph("Compras del Día", styles['Heading2']))
            
            if compras:
                # Preparar datos para la tabla de compras
                compras_data = [["Producto", "Cantidad", "Unidad", "Precio/U", "Subtotal"]]
                for c in compras:
                    compras_data.append([
                        c['nombre_producto'],
                        f"{c['cantidad']:.2f}",
                        c['unidad'],
                        f"${c['precio_unitario_compra']:.2f}",
                        f"${c['subtotal']:.2f}"
                    ])
                
                # Crear tabla de compras
                compras_table = Table(compras_data)
                compras_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(compras_table)
                story.append(Spacer(1, 12))
                
                # Total compras
                story.append(Paragraph(f"Total Compras: ${total_compras:.2f}", styles['Heading3']))
                story.append(Spacer(1, 12))
            else:
                story.append(Paragraph("No hubo compras hoy.", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Sección de Ganancias Netas
            story.append(Paragraph("Resumen Financiero", styles['Heading2']))
            story.append(Paragraph(f"Total Ventas: ${total_ventas:.2f}", styles['Normal']))
            story.append(Paragraph(f"Total Compras: ${total_compras:.2f}", styles['Normal']))
            story.append(Paragraph(f"Ganancia Neta: ${ganancia_neta:.2f}", 
                                style=styles['Heading3'] if ganancia_neta >= 0 else styles['Heading4']))
            
            # Generar el PDF
            doc.build(story)
            messagebox.showinfo("Éxito", f"Reporte generado exitosamente en: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{str(e)}")
            
    def on_closing(self):
        """Clean up and close connection when closing the app"""
        try:
            self.conn.close()
        except:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AnalisisGananciasApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()