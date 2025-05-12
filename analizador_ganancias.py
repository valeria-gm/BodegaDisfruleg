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

class AnalisisGananciasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de Ganancias - Disfruleg")
        self.root.geometry("1000x700")
        
        # Connect to database
        self.conn = conectar()
        self.cursor = self.conn.cursor(dictionary=True)
        
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
        
        tk.Button(button_frame, text="Ver Gráfico", command=self.show_chart, 
                  bg="#FF5722", fg="white", padx=10, pady=3).pack(side="left", padx=5)
        
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
                    COALESCE(AVG(df.precio_unitario_compra), 0) as precio_promedio_venta,
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
    
    def show_chart(self):
        """Show charts in a new window"""
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Gráficos de Análisis")
        chart_window.geometry("800x600")
        
        # Create figure
        fig = Figure(figsize=(12, 8))
        
        # Top 10 most profitable products
        ax1 = fig.add_subplot(2, 1, 1)
        profitable_products = sorted([p for p in self.all_products if p['ganancia_total'] > 0],
                                   key=lambda x: x['ganancia_total'], reverse=True)[:10]
        
        if profitable_products:
            names = [p['nombre_producto'][:15] + '...' if len(p['nombre_producto']) > 15 
                    else p['nombre_producto'] for p in profitable_products]
            ganancias = [p['ganancia_total'] for p in profitable_products]
            
            bars = ax1.bar(names, ganancias, color='#4CAF50')
            ax1.set_title('Top 10 Productos Más Rentables')
            ax1.set_ylabel('Ganancia ($)')
            ax1.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, ganancia in zip(bars, ganancias):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'${ganancia:.0f}', ha='center', va='bottom')
        
        # Products with losses
        ax2 = fig.add_subplot(2, 1, 2)
        loss_products = sorted([p for p in self.all_products if p['ganancia_total'] < 0],
                              key=lambda x: x['ganancia_total'])[:10]
        
        if loss_products:
            names = [p['nombre_producto'][:15] + '...' if len(p['nombre_producto']) > 15 
                    else p['nombre_producto'] for p in loss_products]
            perdidas = [abs(p['ganancia_total']) for p in loss_products]
            
            bars = ax2.bar(names, perdidas, color='#f44336')
            ax2.set_title('Top 10 Productos con Mayor Pérdida')
            ax2.set_ylabel('Pérdida ($)')
            ax2.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, perdida in zip(bars, perdidas):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'${perdida:.0f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Embed chart in tkinter window
        canvas = FigureCanvasTkAgg(fig, chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def export_to_pdf(self):
        """Export analysis to PDF"""
        # This would require additional libraries like reportlab
        # For now, just show a message
        messagebox.showinfo("Export", "Función de exportación a PDF pendiente de implementar.\n"
                          "Puedes usar Ctrl+P para imprimir la pantalla actual.")
    
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