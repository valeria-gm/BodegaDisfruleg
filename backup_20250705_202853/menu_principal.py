import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from conexion import conectar
import subprocess
import sys
import os
from PIL import Image, ImageTk  # Para iconos (opcional)

class MenuPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("DISFRULEG - Sistema de Gestión")
        self.root.geometry("900x700")
        self.root.configure(bg="#f5f5f5")
        
        # Verificar conexión a la base de datos
        self.verificar_conexion()
        
        # Configurar el estilo
        self.setup_styles()
        
        # Crear la interfaz
        self.create_interface()
        
        # Centrar la ventana
        self.center_window()
    
    def verificar_conexion(self):
        """Verificar que la conexión a la base de datos funcione"""
        try:
            conn = conectar()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error de Conexión", 
                               f"No se pudo conectar a la base de datos:\n{str(e)}\n\n"
                               f"Verifique que MySQL esté ejecutándose y que las credenciales sean correctas.")
            sys.exit(1)
    
    def setup_styles(self):
        """Configurar estilos personalizados"""
        self.style = ttk.Style()
        
        # Configurar tema
        self.style.theme_use('clam')
        
        # Estilo para botones principales
        self.style.configure("Main.TButton",
                           font=('Arial', 12, 'bold'),
                           padding=(10, 15))
        
        # Estilo para el título
        self.title_font = ('Arial', 24, 'bold')
        self.subtitle_font = ('Arial', 12)
        self.button_font = ('Arial', 11, 'bold')
    
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_interface(self):
        """Crear la interfaz principal"""
        # Header
        self.create_header()
        
        # Main content area
        self.create_main_content()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Crear el encabezado"""
        header_frame = tk.Frame(self.root, bg="#2C3E50", height=120)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Título principal
        title_label = tk.Label(header_frame, 
                              text="DISFRULEG",
                              font=self.title_font,
                              fg="white",
                              bg="#2C3E50")
        title_label.pack(pady=20)
        
        # Subtítulo
        subtitle_label = tk.Label(header_frame,
                                 text="Sistema Integral de Gestión Comercial",
                                 font=self.subtitle_font,
                                 fg="#BDC3C7",
                                 bg="#2C3E50")
        subtitle_label.pack()
    
    def create_main_content(self):
        """Crear el contenido principal con los módulos"""
        # Frame principal con scrollbar
        main_frame = tk.Frame(self.root, bg="#f5f5f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_frame, bg="#f5f5f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configurar grid del contenido
        self.content_frame = scrollable_frame
        
        # Crear secciones de módulos
        self.create_modules_grid()
        
        # Pack canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_modules_grid(self):
        """Crear la cuadrícula de módulos"""
        # Definir módulos con sus configuraciones
        modules = [
            {
                'title': 'Generar Recibos',
                'description': 'Crear recibos para clientes\ny gestionar facturación',
                'file': 'main.py',
                'bg_color': '#3498DB',
                'hover_color': '#2980B9'
            },
            {
                'title': 'Editor de Precios',
                'description': 'Gestionar productos\ny precios por tipo de cliente',
                'file': 'price_editor.py',
                'bg_color': '#E74C3C',
                'hover_color': '#C0392B'
            },
            {
                'title': 'Registro de Compras',
                'description': 'Registrar compras\ny gestionar inventario',
                'file': 'registro_compras.py',
                'bg_color': '#2ECC71',
                'hover_color': '#27AE60'
            },
            {
                'title': 'Análisis de Ganancias',
                'description': 'Ver reportes detallados\nde ganancias y pérdidas',
                'file': 'analizador_ganancias.py',
                'bg_color': '#9B59B6',
                'hover_color': '#8E44AD'
            },
            {
                'title': 'Administrar Clientes',
                'description': 'Gestionar clientes\ny tipos de cliente',
                'file': 'client_manager.py',
                'bg_color': '#F39C12',
                'hover_color': '#E67E22'
            }
        ]
        
        # Crear tarjetas de módulos
        row = 0
        col = 0
        max_cols = 2
        
        for module in modules:
            self.create_module_card(self.content_frame, module, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configurar pesos de columnas para centrado
        for i in range(max_cols):
            self.content_frame.grid_columnconfigure(i, weight=1, uniform="column")
    
    def create_module_card(self, parent, module, row, col):
        """Crear una tarjeta para un módulo"""
        # Frame principal de la tarjeta
        card_frame = tk.Frame(parent, 
                             bg=module['bg_color'],
                             relief='raised',
                             bd=0,
                             cursor='hand2')
        card_frame.grid(row=row, column=col, padx=15, pady=15, sticky="ew")
        
        # Configurar padding interno
        inner_frame = tk.Frame(card_frame, bg=module['bg_color'])
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título del módulo
        title_label = tk.Label(inner_frame,
                              text=module['title'],
                              font=('Arial', 16, 'bold'),
                              fg='white',
                              bg=module['bg_color'])
        title_label.pack(pady=(0, 10))
        
        # Descripción
        desc_label = tk.Label(inner_frame,
                             text=module['description'],
                             font=('Arial', 10),
                             fg='white',
                             bg=module['bg_color'],
                             justify='center')
        desc_label.pack(pady=(0, 15))
        
        # Botón de acceso
        access_btn = tk.Button(inner_frame,
                              text="ABRIR MÓDULO",
                              font=('Arial', 10, 'bold'),
                              bg='white',
                              fg=module['bg_color'],
                              relief='flat',
                              cursor='hand2',
                              command=lambda: self.launch_module(module['file']))
        access_btn.pack(pady=(5, 0), ipadx=10, ipady=5)
        
        # Efectos hover
        def on_enter(event):
            card_frame.configure(bg=module['hover_color'])
            inner_frame.configure(bg=module['hover_color'])
            title_label.configure(bg=module['hover_color'])
            desc_label.configure(bg=module['hover_color'])
        
        def on_leave(event):
            card_frame.configure(bg=module['bg_color'])
            inner_frame.configure(bg=module['bg_color'])
            title_label.configure(bg=module['bg_color'])
            desc_label.configure(bg=module['bg_color'])
        
        # Bind eventos hover a todos los widgets de la tarjeta
        for widget in [card_frame, inner_frame, title_label, desc_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e: self.launch_module(module['file']))
    
    def create_footer(self):
        """Crear el pie de página"""
        footer_frame = tk.Frame(self.root, bg="#34495E", height=60)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        # Botón de salir
        exit_btn = tk.Button(footer_frame,
                            text="Salir del Sistema",
                            font=('Arial', 11),
                            bg="#E74C3C",
                            fg="white",
                            relief='flat',
                            cursor='hand2',
                            command=self.on_closing,
                            padx=20,
                            pady=5)
        exit_btn.pack(side="right", padx=20, pady=15)
        
        # Información del sistema
        info_label = tk.Label(footer_frame,
                             text="DISFRULEG v1.0 - Sistema de Gestión Comercial",
                             font=('Arial', 9),
                             fg="#BDC3C7",
                             bg="#34495E")
        info_label.pack(side="left", padx=20, pady=20)
    
    def launch_module(self, filename):
        """Lanzar un módulo específico"""
        try:
            # Verificar que el archivo existe
            if not os.path.exists(filename):
                messagebox.showerror("Error", f"No se pudo encontrar el archivo: {filename}")
                return
            
            # Cambiar el cursor mientras se carga
            self.root.configure(cursor="wait")
            self.root.update()
            
            # Lanzar el módulo en un proceso separado
            if sys.platform.startswith('win'):
                subprocess.Popen([sys.executable, filename], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([sys.executable, filename])
            
            # Restaurar cursor
            self.root.configure(cursor="")
            
        except Exception as e:
            self.root.configure(cursor="")
            messagebox.showerror("Error", f"No se pudo abrir el módulo:\n{str(e)}")
    
    def on_closing(self):
        """Manejar el cierre de la aplicación"""
        if messagebox.askyesno("Salir", "¿Está seguro que desea salir del sistema?"):
            self.root.quit()

def main():
    """Función principal"""
    root = tk.Tk()
    app = MenuPrincipal(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()