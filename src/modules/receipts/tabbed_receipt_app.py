import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional

# Importaciones del núcleo de la aplicación de pestañas
from .core.tab_session import TabSession, TabSessionFactory
from .core.app_factory import AppFactory

class TabbedReceiptAppConsolidated:
    """
    Contenedor consolidado de múltiples pestañas para la aplicación de generación de recibos.
    Utiliza un sistema de callbacks para una comunicación de estado clara y robusta.
    """
    
    def __init__(self, root: tk.Tk, user_data: Dict[str, Any], mode: str = "standard"):
        self.root = root
        self.root.title("Generador de Recibos - Multi-Pestaña")
        self.root.geometry("1200x800")
        
        self.user_data = user_data
        self.mode = mode
        
        # Gestión de pestañas
        self.tabs: Dict[str, TabSession] = {}
        self.current_tab_id: Optional[str] = None
        self.tab_counter = 0
        
        # Crear la interfaz principal
        self._create_interface()
        self._setup_keyboard_shortcuts()
        
        # Crear la primera pestaña al iniciar
        self._create_new_tab()
        
        # Manejar el cierre de la ventana
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _create_interface(self):
        """Crea la interfaz principal con el control de pestañas."""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        tab_control_frame = ttk.Frame(main_frame)
        tab_control_frame.pack(fill="x", pady=(0, 5))
        
        self.notebook = ttk.Notebook(tab_control_frame)
        self.notebook.pack(fill="both", expand=True, side="left")
        
        self._create_control_buttons(tab_control_frame)
        
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
        self._create_status_bar(main_frame)
    
    def _create_control_buttons(self, parent):
        """Crea los botones para añadir y cerrar pestañas."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(side="right", padx=(10, 0), fill="y")
        
        ttk.Button(
            button_frame, 
            text="+ Nueva Pestaña", 
            command=self._create_new_tab
        ).pack(side="top", pady=(0, 5), ipady=2)
        
        ttk.Button(
            button_frame, 
            text="Cerrar Pestaña", 
            command=self._close_current_tab
        ).pack(side="top", ipady=2)
    
    def _create_status_bar(self, parent):
        """Crea la barra de estado inferior."""
        status_frame = ttk.Frame(parent, padding="5 2")
        status_frame.pack(fill="x", side="bottom", pady=(5, 0))
        
        status_text = f"Modo: {self.mode.capitalize()}"
        ttk.Label(status_frame, text=status_text).pack(side="left")
        
        self.tab_info_label = ttk.Label(status_frame, text="", anchor="e")
        self.tab_info_label.pack(side="right", fill="x", expand=True)
    
    def _setup_keyboard_shortcuts(self):
        """Configura los atajos de teclado para la navegación de pestañas."""
        self.root.bind("<Control-t>", lambda e: self._create_new_tab())
        self.root.bind("<Control-w>", lambda e: self._close_current_tab())
        self.root.bind("<Control-Tab>", lambda e: self._next_tab())
        self.root.bind("<Control-Shift-Tab>", lambda e: self._previous_tab())
        
        for i in range(1, 10):
            self.root.bind(f"<Control-KeyPress-{i}>", lambda e, idx=i-1: self._select_tab_by_index(idx))

    def _create_new_tab(self) -> Optional[str]:
        """Crea y configura una nueva pestaña y su sesión asociada."""
        try:
            tab_session = TabSessionFactory.create_session(self.mode, self.user_data)
            self.tab_counter += 1
            
            tab_frame = ttk.Frame(self.notebook)
            tab_session.tab_frame = tab_frame
            
            # Crear una función de callback que captura la sesión actual.
            # Esto es crucial para que cada pestaña notifique a su propia sesión.
            def state_change_callback():
                self._handle_state_change(tab_session)

            app_instance = AppFactory.create_app_for_mode(
                mode=self.mode,
                root_or_frame=tab_frame,
                user_data=tab_session.user_data,
                tab_id=tab_session.tab_id,
                main_window=self.root,
                on_state_change=state_change_callback
            )
            
            tab_session.app_instance = app_instance
            self.tabs[tab_session.tab_id] = tab_session
            
            self.notebook.add(tab_frame, text=tab_session.get_tab_title())
            self.notebook.select(tab_frame)
            
            self._update_tab_info()
            
            return tab_session.tab_id
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la nueva pestaña: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _handle_state_change(self, tab_session: TabSession):
        """
        Callback que se ejecuta cuando el estado de una aplicación de recibos cambia.
        Actualiza la sesión y la UI del contenedor principal.
        """
        app = tab_session.app_instance
        if not app:
            return

        client_name = app.current_client.nombre_cliente if app.current_client else ""
        cart_count = app.cart_manager.get_cart_count() if app.cart_manager else 0
        
        tab_session.update_status(client_name, cart_count)
        
        self._update_tab_title(tab_session.tab_id)
        if tab_session.tab_id == self.current_tab_id:
            self._update_tab_info()

    def _update_tab_title(self, tab_id: str):
        """Actualiza el texto del título de una pestaña específica."""
        if tab_id not in self.tabs:
            return
        
        try:
            tab_session = self.tabs[tab_id]
            tab_frame = tab_session.tab_frame
            
            if tab_frame and tab_frame.winfo_exists():
                title = tab_session.get_tab_title()
                if tab_session.has_data():
                    title += " •"  # Indicador de cambios no guardados
                
                for i, tab_widget_path in enumerate(self.notebook.tabs()):
                    if str(tab_frame) == tab_widget_path:
                        self.notebook.tab(i, text=title)
                        break
        except Exception as e:
            print(f"Advertencia: No se pudo actualizar el título de la pestaña: {e}")

    def _close_current_tab(self):
        """Cierra la pestaña actualmente seleccionada."""
        if self.current_tab_id:
            self._close_tab(self.current_tab_id)
    
    def _close_tab(self, tab_id: str):
        """Lógica para cerrar una pestaña específica, con confirmaciones."""
        if tab_id not in self.tabs:
            return
            
        tab_session = self.tabs[tab_id]
        
        # Prevenir cerrar la última pestaña sin crear una nueva
        if len(self.tabs) == 1:
            messagebox.showwarning("Acción no permitida", "No se puede cerrar la última pestaña.")
            return

        # Confirmar si hay datos no guardados
        if tab_session.has_data():
            client_info = f" para '{tab_session.client_name}'" if tab_session.client_name else ""
            msg = (f"La pestaña{client_info} tiene {tab_session.cart_count} productos en el carrito.\n\n"
                   "¿Está seguro de que desea cerrarla? Los datos se perderán.")
            if not messagebox.askyesno("Confirmar Cierre", msg, icon="warning"):
                return
        
        # Eliminar la pestaña de la UI
        tab_frame = tab_session.tab_frame
        if tab_frame and tab_frame.winfo_exists():
            for i, tab_widget_path in enumerate(self.notebook.tabs()):
                if str(tab_frame) == tab_widget_path:
                    self.notebook.forget(i)
                    break
        
        # Limpiar recursos y eliminar del diccionario
        tab_session.cleanup()
        del self.tabs[tab_id]
        
        # La selección de pestaña se actualiza automáticamente por el evento <<NotebookTabChanged>>
    
    def _on_tab_changed(self, event=None):
        """Maneja el cambio de selección de pestaña."""
        try:
            if not self.notebook.tabs():
                self.current_tab_id = None
            else:
                current_tab_widget_path = self.notebook.select()
                self.current_tab_id = None
                for tab_id, session in self.tabs.items():
                    if str(session.tab_frame) == current_tab_widget_path:
                        self.current_tab_id = tab_id
                        break
            
            self._update_tab_info()
        except tk.TclError:
            # Ocurre si la pestaña ya no existe, es seguro ignorarlo.
            self.current_tab_id = None
        except Exception as e:
            print(f"Advertencia: Error en el cambio de pestaña: {e}")
    
    def _update_tab_info(self):
        """Actualiza la barra de estado con la información de la pestaña actual."""
        info_text = f"Total: {len(self.tabs)} pestañas"
        if self.current_tab_id and self.current_tab_id in self.tabs:
            tab_session = self.tabs[self.current_tab_id]
            title = tab_session.get_tab_title()
            
            if tab_session.cart_count > 0:
                info_text += f"  |  Activa: '{title}' ({tab_session.cart_count} productos)"
            else:
                info_text += f"  |  Activa: '{title}'"
        
        self.tab_info_label.config(text=info_text)

    def _on_window_close(self):
        """Maneja el evento de cierre de la ventana principal."""
        tabs_with_data = [s for s in self.tabs.values() if s.has_data()]
        
        if tabs_with_data:
            msg = ("Hay pestañas con datos no guardados. "
                   "Si cierra la aplicación, estos datos se perderán.\n\n"
                   "¿Desea cerrar de todos modos?")
            if not messagebox.askyesno("Datos no Guardados", msg, icon="warning"):
                return
        
        for session in self.tabs.values():
            session.cleanup()
        
        self.root.destroy()

    def _next_tab(self):
        """Cambia a la siguiente pestaña."""
        if len(self.tabs) < 2: return
        try:
            current_index = self.notebook.index("current")
            next_index = (current_index + 1) % len(self.tabs)
            self.notebook.select(next_index)
        except tk.TclError: pass

    def _previous_tab(self):
        """Cambia a la pestaña anterior."""
        if len(self.tabs) < 2: return
        try:
            current_index = self.notebook.index("current")
            prev_index = (current_index - 1 + len(self.tabs)) % len(self.tabs)
            self.notebook.select(prev_index)
        except tk.TclError: pass

    def _select_tab_by_index(self, index: int):
        """Selecciona una pestaña por su índice numérico."""
        if 0 <= index < len(self.tabs):
            try:
                self.notebook.select(index)
            except tk.TclError: pass

# Clases de conveniencia para mantener la compatibilidad
class TabbedReceiptApp(TabbedReceiptAppConsolidated):
    def __init__(self, root: tk.Tk, user_data: Dict[str, Any]):
        super().__init__(root, user_data, mode="standard")

class IsolatedTabbedReceiptApp(TabbedReceiptAppConsolidated):
    def __init__(self, root: tk.Tk, user_data: Dict[str, Any]):
        super().__init__(root, user_data, mode="isolated")

if __name__ == "__main__":
    root = tk.Tk()
    # Estilo para una apariencia más moderna
    style = ttk.Style(root)
    style.theme_use("clam") # O 'alt', 'default', 'vista'
    
    user_data = {
        'nombre_completo': 'Usuario de Prueba',
        'rol': 'admin'
    }
    
    app = TabbedReceiptApp(root, user_data)
    root.mainloop()
