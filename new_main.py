#!/usr/bin/env python3
"""
DISFRULEG - Sistema de Gestión Comercial
Punto de entrada principal con autenticación

Este archivo reemplaza menu_principal.py como punto de entrada único
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
from login_window import show_login
from session_manager import session_manager, SessionStatusBar
from db_manager import db_manager
import subprocess

class MainApplication:
    def __init__(self):
        self.root = None
        self.user_data = None
        self.status_bar = None
        
    def start(self):
        """Iniciar aplicación"""
        # Mostrar ventana de login
        success, user_data = show_login(self.on_login_success)
        
        if success and user_data:
            self.user_data = user_data
            self.create_main_window()
            self.run_main_loop()
        else:
            # Usuario canceló login o falló
            sys.exit(0)
    
    def on_login_success(self, user_data):
        """Callback ejecutado cuando login es exitoso"""
        self.user_data = user_data
        print(f"Login exitoso: {user_data['nombre_completo']}")
    
    def create_main_window(self):
        """Crear ventana principal"""
        self.root = tk.Tk()
        self.root.title("DISFRULEG - Sistema de Gestión")
        self.root.geometry("900x700")
        self.root.configure(bg="#f5f5f5")
        
        # Configurar protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Registrar callback de sesión
        session_manager.add_callback(self.handle_session_event)
        
        # Crear interfaz
        self.create_interface()
        
        # Centrar ventana
        self.center_window()
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_interface(self):
        """Crear interfaz principal"""
        # Header con información de usuario
        self.create_header()
        
        # Main content area
        self.create_main_content()
        
        # Status bar con información de sesión
        self.create_status_bar()
    
    def create_header(self):
        """Crear encabezado con información de usuario"""
        header_frame = tk.Frame(self.root, bg="#2C3E50", height=120)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Container para centrar contenido
        header_content = tk.Frame(header_frame, bg="#2C3E50")
        header_content.pack(expand=True)
        
        # Título principal
        title_label = tk.Label(header_content, 
                              text="DISFRULEG",
                              font=("Arial", 24, "bold"),
                              fg="white",
                              bg="#2C3E50")
        title_label.pack(pady=(15, 5))
        
        # Información del usuario
        user_info = f"Bienvenido, {self.user_data['nombre_completo']} ({self.user_data['rol'].upper()})"
        user_label = tk.Label(header_content,
                             text=user_info,
                             font=("Arial", 12),
                             fg="#BDC3C7",
                             bg="#2C3E50")
        user_label.pack()
        
        # Botón de cerrar sesión
        logout_btn = tk.Button(header_content,
                              text="Cerrar Sesión",
                              command=self.logout,
                              font=("Arial", 10),
                              bg="#E74C3C",
                              fg="white",
                              relief="flat",
                              cursor="hand2",
                              padx=15,
                              pady=5)
        logout_btn.pack(pady=(10, 0))
    
    def create_main_content(self):
        """Crear contenido principal con módulos"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#f5f5f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Canvas para scroll si es necesario
        canvas = tk.Canvas(main_frame, bg="#f5f5f5", highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Crear módulos
        self.create_modules_grid(scrollable_frame)
        
        # Pack canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_modules_grid(self, parent):
        """Crear cuadrícula de módulos"""
        # Definir módulos disponibles
        modules = [
            {
                'title': 'Generar Recibos',
                'description': 'Crear recibos para clientes\ny gestionar facturación',
                'file': 'main.py',
                'bg_color': '#3498DB',
                'hover_color': '#2980B9',
                'requires_admin': False
            },
            {
                'title': 'Editor de Precios',
                'description': 'Gestionar productos\ny precios por tipo de cliente',
                'file': 'price_editor.py',
                'bg_color': '#E74C3C',
                'hover_color': '#C0392B',
                'requires_admin': True
            },
            {
                'title': 'Registro de Compras',
                'description': 'Registrar compras\ny gestionar inventario',
                'file': 'registro_compras.py',
                'bg_color': '#2ECC71',
                'hover_color': '#27AE60',
                'requires_admin': False
            },
            {
                'title': 'Análisis de Ganancias',
                'description': 'Ver reportes detallados\nde ganancias y pérdidas',
                'file': 'analizador_ganancias.py',
                'bg_color': '#9B59B6',
                'hover_color': '#8E44AD',
                'requires_admin': False
            },
            {
                'title': 'Administrar Clientes',
                'description': 'Gestionar clientes\ny tipos de cliente',
                'file': 'client_manager.py',
                'bg_color': '#F39C12',
                'hover_color': '#E67E22',
                'requires_admin': True
            }
        ]
        
        # Filtrar módulos según rol del usuario
        available_modules = []
        user_role = self.user_data.get('rol', 'usuario')
        
        for module in modules:
            if module['requires_admin'] and user_role != 'admin':
                # Skip admin modules for non-admin users
                continue
            available_modules.append(module)
        
        # Crear tarjetas de módulos
        row = 0
        col = 0
        max_cols = 2
        
        for module in available_modules:
            self.create_module_card(parent, module, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configurar pesos de columnas
        for i in range(max_cols):
            parent.grid_columnconfigure(i, weight=1, uniform="column")
    
    def create_module_card(self, parent, module, row, col):
        """Crear tarjeta de módulo"""
        # Frame principal de la tarjeta
        card_frame = tk.Frame(parent, 
                             bg=module['bg_color'],
                             relief='raised',
                             bd=0,
                             cursor='hand2')
        card_frame.grid(row=row, column=col, padx=15, pady=15, sticky="ew")
        
        # Frame interno
        inner_frame = tk.Frame(card_frame, bg=module['bg_color'])
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
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
            for widget in [card_frame, inner_frame, title_label, desc_label]:
                widget.configure(bg=module['hover_color'])
        
        def on_leave(event):
            for widget in [card_frame, inner_frame, title_label, desc_label]:
                widget.configure(bg=module['bg_color'])
        
        # Bind eventos
        for widget in [card_frame, inner_frame, title_label, desc_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e: self.launch_module(module['file']))
    
    def create_status_bar(self):
        """Crear barra de estado con información de sesión"""
        self.status_bar = SessionStatusBar(self.root)
    
    def launch_module(self, filename):
        """Lanzar módulo específico"""
        try:
            # Actualizar actividad de sesión
            session_manager.update_activity()
            
            # Verificar que el archivo existe
            if not os.path.exists(filename):
                messagebox.showerror("Error", f"No se pudo encontrar el archivo: {filename}")
                return
            
            # Cambiar cursor mientras se carga
            self.root.configure(cursor="wait")
            self.root.update()
            
            # Lanzar el módulo
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
    
    def handle_session_event(self, event_type, user_data):
        """Manejar eventos de sesión"""
        if event_type == 'session_timeout':
            # Sesión expirada
            messagebox.showwarning("Sesión Expirada", 
                                 "Su sesión ha expirado por inactividad.\n"
                                 "Por favor, inicie sesión nuevamente.")
            self.force_logout()
        elif event_type == 'session_ended':
            # Sesión terminada manualmente
            self.close_application()
    
    def logout(self):
        """Cerrar sesión del usuario"""
        if messagebox.askyesno("Cerrar Sesión", 
                             "¿Está seguro que desea cerrar su sesión?"):
            self.force_logout()
    
    def force_logout(self):
        """Forzar cierre de sesión"""
        # Cerrar sesión
        session_manager.end_session()
        db_manager.close_connection()
        
        # Cerrar aplicación
        self.close_application()
    
    def close_application(self):
        """Cerrar aplicación completamente"""
        try:
            if self.root:
                self.root.quit()
                self.root.destroy()
        except:
            pass
        
        sys.exit(0)
    
    def on_closing(self):
        """Manejar cierre de ventana"""
        if messagebox.askyesno("Salir", 
                             "¿Está seguro que desea salir del sistema?\n"
                             "Esto cerrará su sesión."):
            self.force_logout()
    
    def run_main_loop(self):
        """Ejecutar bucle principal"""
        if self.root:
            self.root.mainloop()

def main():
    """Función principal"""
    try:
        # Verificar dependencias críticas
        import bcrypt
        import mysql.connector
        
        # Crear y ejecutar aplicación
        app = MainApplication()
        app.start()
        
    except ImportError as e:
        messagebox.showerror("Error de Dependencias", 
                           f"Falta una dependencia crítica:\n{e}\n\n"
                           f"Por favor, instale las dependencias requeridas.")
        sys.exit(1)
    except Exception as e:
        messagebox.showerror("Error Fatal", 
                           f"Error inesperado al iniciar la aplicación:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()