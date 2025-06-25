#!/usr/bin/env python3
"""
DISFRULEG - Sistema de Gestión Comercial
Versión progresiva con debug para identificar el problema exacto
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
import subprocess

# Variables de debug - cambiar a True/False para activar/desactivar funcionalidades
DEBUG_MODE = True
USE_LOGIN = True  # Comenzamos sin login
USE_SESSION_MANAGER = True  # Sin session manager
USE_CANVAS_SCROLL = True  # Sin scroll por ahora
USE_HOVER_EFFECTS = True # Sin efectos hover

def debug_print(message):
    """Imprimir mensajes de debug"""
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

class ProgressiveMainApplication:
    def __init__(self):
        self.root = None
        self.user_data = None
        self.status_bar = None
        
    def start(self):
        """Iniciar aplicación"""
        debug_print("Iniciando aplicación...")
        
        if USE_LOGIN:
            # Usar sistema de login
            try:
                debug_print("Importando sistema de login...")
                from login_window import show_login
                success, user_data = show_login(self.on_login_success)
                
                if success and user_data:
                    self.user_data = user_data
                    debug_print(f"Login exitoso: {user_data}")
                else:
                    debug_print("Login cancelado")
                    sys.exit(0)
            except Exception as e:
                debug_print(f"Error en login: {e}")
                messagebox.showerror("Error", f"Error en sistema de login: {e}")
                sys.exit(1)
        else:
            # Usuario simulado
            self.user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test'
            }
            debug_print("Usando usuario simulado")
        
        self.create_main_window()
        self.run_main_loop()
    
    def on_login_success(self, user_data):
        """Callback ejecutado cuando login es exitoso"""
        self.user_data = user_data
        debug_print(f"Callback login exitoso: {user_data['nombre_completo']}")
    
    def create_main_window(self):
        """Crear ventana principal"""
        debug_print("Creando ventana principal...")
        
        try:
            self.root = tk.Tk()
            self.root.title("DISFRULEG - Sistema de Gestión")
            
            # Configurar tamaño de forma muy conservadora
            debug_print("Configurando geometría...")
            self.root.geometry("900x700")
            self.root.configure(bg="#f5f5f5")
            
            # Configurar protocolo de cierre
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            if USE_SESSION_MANAGER:
                try:
                    debug_print("Inicializando session manager...")
                    from session_manager import session_manager
                    session_manager.add_callback(self.handle_session_event)
                    session_manager.start_session(self.user_data)
                except Exception as e:
                    debug_print(f"Error en session manager: {e}")
                    messagebox.showwarning("Advertencia", f"Session manager no disponible: {e}")
            
            # Crear interfaz
            debug_print("Creando interfaz...")
            self.create_interface()
            
            # Centrar ventana
            debug_print("Centrando ventana...")
            self.root.after(100, self.center_window_safe)
            
        except Exception as e:
            debug_print(f"Error creando ventana principal: {e}")
            raise
    
    def center_window_safe(self):
        """Centrar ventana de forma muy segura"""
        try:
            debug_print("Ejecutando centrado seguro...")
            self.root.update_idletasks()
            
            # Valores fijos para evitar problemas
            width = 900
            height = 700
            
            # Obtener dimensiones de pantalla
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            debug_print(f"Pantalla: {screen_width}x{screen_height}")
            debug_print(f"Ventana: {width}x{height}")
            
            # Calcular posición centrada con valores enteros
            x = int((screen_width - width) / 2)
            y = int((screen_height - height) / 2)
            
            # Asegurar valores positivos
            x = max(0, x)
            y = max(0, y)
            
            debug_print(f"Posición calculada: x={x}, y={y}")
            
            # Aplicar geometría
            geometry_string = f"{width}x{height}+{x}+{y}"
            debug_print(f"Aplicando geometría: {geometry_string}")
            
            self.root.geometry(geometry_string)
            debug_print("Centrado completado exitosamente")
            
        except Exception as e:
            debug_print(f"Error en centrado: {e}")
            # No es crítico si falla el centrado
    
    def create_interface(self):
        """Crear interfaz principal"""
        debug_print("Creando componentes de interfaz...")
        
        try:
            # Header
            debug_print("Creando header...")
            self.create_header()
            
            # Main content
            debug_print("Creando contenido principal...")
            self.create_main_content()
            
            # Status bar
            debug_print("Creando status bar...")
            self.create_status_bar()
            
            debug_print("Interfaz creada exitosamente")
            
        except Exception as e:
            debug_print(f"Error creando interfaz: {e}")
            raise
    
    def create_header(self):
        """Crear encabezado"""
        try:
            header_frame = tk.Frame(self.root, bg="#2C3E50", height=120)
            header_frame.pack(fill="x")
            header_frame.pack_propagate(False)
            
            # Container para contenido
            header_content = tk.Frame(header_frame, bg="#2C3E50")
            header_content.pack(expand=True, pady=15)
            
            # Título principal
            title_label = tk.Label(header_content, 
                                  text="DISFRULEG",
                                  font=("Arial", 24, "bold"),
                                  fg="white",
                                  bg="#2C3E50")
            title_label.pack(pady=(5, 0))
            
            # Información del usuario
            user_info = f"Bienvenido, {self.user_data['nombre_completo']} ({self.user_data['rol'].upper()})"
            user_label = tk.Label(header_content,
                                 text=user_info,
                                 font=("Arial", 12),
                                 fg="#BDC3C7",
                                 bg="#2C3E50")
            user_label.pack(pady=(5, 0))
            
            # Botón de cerrar sesión (solo si hay login real)
            if USE_LOGIN:
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
            
            debug_print("Header creado exitosamente")
            
        except Exception as e:
            debug_print(f"Error creando header: {e}")
            raise
    
    def create_main_content(self):
        """Crear contenido principal"""
        try:
            if USE_CANVAS_SCROLL:
                # Versión con canvas y scroll
                debug_print("Usando versión con canvas scroll...")
                self.create_main_content_with_scroll()
            else:
                # Versión simple sin scroll
                debug_print("Usando versión simple sin scroll...")
                self.create_main_content_simple()
                
        except Exception as e:
            debug_print(f"Error creando contenido principal: {e}")
            raise
    
    def create_main_content_simple(self):
        """Crear contenido principal simple"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#f5f5f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Crear módulos directamente
        self.create_modules_grid(main_frame)
    
    def create_main_content_with_scroll(self):
        """Crear contenido principal con scroll"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#f5f5f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Canvas para scroll
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
        
        # Mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_modules_grid(self, parent):
        """Crear cuadrícula de módulos"""
        debug_print("Creando grid de módulos...")
        
        try:
            # Definir módulos
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
            
            # Filtrar módulos según rol
            available_modules = []
            user_role = self.user_data.get('rol', 'usuario')
            
            for module in modules:
                if module['requires_admin'] and user_role != 'admin':
                    continue
                available_modules.append(module)
            
            debug_print(f"Módulos disponibles: {len(available_modules)}")
            
            # Crear tarjetas
            row = 0
            col = 0
            max_cols = 2
            
            for i, module in enumerate(available_modules):
                debug_print(f"Creando módulo {i+1}: {module['title']}")
                self.create_module_card(parent, module, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # Configurar columnas
            for i in range(max_cols):
                parent.grid_columnconfigure(i, weight=1, uniform="column")
                
            debug_print("Grid de módulos creado exitosamente")
            
        except Exception as e:
            debug_print(f"Error creando grid de módulos: {e}")
            raise
    
    def create_module_card(self, parent, module, row, col):
        """Crear tarjeta de módulo"""
        try:
            # Frame principal
            card_frame = tk.Frame(parent, 
                                 bg=module['bg_color'],
                                 relief='raised',
                                 bd=2,
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
            
            # Botón
            access_btn = tk.Button(inner_frame,
                                  text="ABRIR MÓDULO",
                                  font=('Arial', 10, 'bold'),
                                  bg='white',
                                  fg=module['bg_color'],
                                  relief='flat',
                                  cursor='hand2',
                                  command=lambda: self.launch_module(module['file']))
            access_btn.pack(pady=(5, 0), ipadx=10, ipady=5)
            
            # Efectos hover si están habilitados
            if USE_HOVER_EFFECTS:
                self.setup_hover_effects(card_frame, inner_frame, title_label, desc_label, module)
            
        except Exception as e:
            debug_print(f"Error creando tarjeta de módulo: {e}")
            raise
    
    def setup_hover_effects(self, card_frame, inner_frame, title_label, desc_label, module):
        """Configurar efectos hover"""
        def on_enter(event):
            for widget in [card_frame, inner_frame, title_label, desc_label]:
                try:
                    widget.configure(bg=module['hover_color'])
                except:
                    pass
        
        def on_leave(event):
            for widget in [card_frame, inner_frame, title_label, desc_label]:
                try:
                    widget.configure(bg=module['bg_color'])
                except:
                    pass
        
        # Bind eventos
        for widget in [card_frame, inner_frame, title_label, desc_label]:
            try:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                widget.bind("<Button-1>", lambda e: self.launch_module(module['file']))
            except:
                pass
    
    def create_status_bar(self):
        """Crear barra de estado"""
        try:
            if USE_SESSION_MANAGER:
                debug_print("Creando status bar con session manager...")
                from session_manager import SessionStatusBar
                self.status_bar = SessionStatusBar(self.root)
            else:
                debug_print("Creando status bar simple...")
                status_frame = tk.Frame(self.root, relief=tk.SUNKEN, bd=1)
                status_frame.pack(side=tk.BOTTOM, fill=tk.X)
                
                user_info = f"Usuario: {self.user_data['nombre_completo']}"
                status_label = tk.Label(status_frame, text=user_info, anchor=tk.W)
                status_label.pack(side=tk.LEFT, padx=5, pady=2)
                
                # Botón salir
                exit_btn = tk.Button(status_frame,
                                    text="Salir",
                                    command=self.on_closing,
                                    bg="#E74C3C",
                                    fg="white",
                                    relief="flat",
                                    padx=10)
                exit_btn.pack(side=tk.RIGHT, padx=5, pady=2)
                
            debug_print("Status bar creado exitosamente")
            
        except Exception as e:
            debug_print(f"Error creando status bar: {e}")
            # Status bar no es crítico
    
    def launch_module(self, filename):
        """Lanzar módulo"""
        debug_print(f"Lanzando módulo: {filename}")
        
        try:
            if USE_SESSION_MANAGER:
                from session_manager import session_manager
                session_manager.update_activity()
            
            if not os.path.exists(filename):
                messagebox.showerror("Error", f"No se encontró el archivo: {filename}")
                return
            
            # Lanzar módulo
            if sys.platform.startswith('win'):
                subprocess.Popen([sys.executable, filename], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([sys.executable, filename])
                
            debug_print(f"Módulo {filename} lanzado exitosamente")
            
        except Exception as e:
            debug_print(f"Error lanzando módulo: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")
    
    def handle_session_event(self, event_type, user_data):
        """Manejar eventos de sesión"""
        debug_print(f"Evento de sesión: {event_type}")
        
        if event_type == 'session_timeout':
            messagebox.showwarning("Sesión Expirada", 
                                 "Su sesión ha expirado por inactividad.")
            self.force_logout()
        elif event_type == 'session_ended':
            self.close_application()
    
    def logout(self):
        """Cerrar sesión"""
        if messagebox.askyesno("Cerrar Sesión", 
                             "¿Está seguro que desea cerrar su sesión?"):
            self.force_logout()
    
    def force_logout(self):
        """Forzar cierre de sesión"""
        debug_print("Forzando logout...")
        
        if USE_SESSION_MANAGER:
            try:
                from session_manager import session_manager
                session_manager.end_session()
            except:
                pass
        
        if USE_LOGIN:
            try:
                from db_manager import db_manager
                db_manager.close_connection()
            except:
                pass
        
        self.close_application()
    
    def close_application(self):
        """Cerrar aplicación"""
        debug_print("Cerrando aplicación...")
        
        try:
            if self.root:
                self.root.quit()
                self.root.destroy()
        except:
            pass
        
        sys.exit(0)
    
    def on_closing(self):
        """Manejar cierre de ventana"""
        if messagebox.askyesno("Salir", "¿Está seguro que desea salir del sistema?"):
            self.force_logout()
    
    def run_main_loop(self):
        """Ejecutar bucle principal"""
        debug_print("Iniciando bucle principal...")
        
        if self.root:
            self.root.mainloop()

def main():
    """Función principal"""
    try:
        debug_print("=== INICIO DEL PROGRAMA ===")
        debug_print(f"Debug mode: {DEBUG_MODE}")
        debug_print(f"Use login: {USE_LOGIN}")
        debug_print(f"Use session manager: {USE_SESSION_MANAGER}")
        debug_print(f"Use canvas scroll: {USE_CANVAS_SCROLL}")
        debug_print(f"Use hover effects: {USE_HOVER_EFFECTS}")
        
        app = ProgressiveMainApplication()
        app.start()
        
    except Exception as e:
        debug_print(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Error Fatal", f"Error inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()