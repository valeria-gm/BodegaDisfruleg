import tkinter as tk
from tkinter import ttk, messagebox
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from .receipt_generator_refactored import ReciboAppMejorado


class TabSession:
    """Manages the state of a single receipt generation session"""
    
    def __init__(self, tab_id: str, user_data: Dict[str, Any]):
        self.tab_id = tab_id
        self.user_data = user_data
        self.app_instance: Optional[ReciboAppMejorado] = None
        self.tab_frame: Optional[ttk.Frame] = None
        self.client_name = ""
        self.has_unsaved_changes = False
        self.cart_count = 0
        self.created_at = datetime.now()
        
    def get_tab_title(self) -> str:
        """Get the display title for this tab"""
        if self.client_name:
            return f"{self.client_name}"
        return "Nueva Sesión"
    
    def get_tab_tooltip(self) -> str:
        """Get tooltip text for this tab"""
        tooltip = f"Sesión creada: {self.created_at.strftime('%H:%M:%S')}\n"
        if self.client_name:
            tooltip += f"Cliente: {self.client_name}\n"
        tooltip += f"Productos en carrito: {self.cart_count}"
        return tooltip
    
    def has_data(self) -> bool:
        """Check if this tab has any data that would be lost on close"""
        return self.cart_count > 0 or self.has_unsaved_changes
    
    def update_status(self, client_name: str = "", cart_count: int = 0, has_changes: bool = False):
        """Update the tab's status"""
        self.client_name = client_name
        self.cart_count = cart_count
        self.has_unsaved_changes = has_changes


class TabbedReceiptApp:
    """Multi-tab wrapper for the receipt generator application"""
    
    def __init__(self, root: tk.Tk, user_data: Dict[str, Any]):
        self.root = root
        self.root.title("Generador de Recibos - Multi-Tab")
        self.root.geometry("1200x800")
        self.user_data = user_data
        
        # Tab management
        self.tabs: Dict[str, TabSession] = {}
        self.current_tab_id: Optional[str] = None
        self.tab_counter = 0
        
        # Create main interface
        self._create_interface()
        self._setup_keyboard_shortcuts()
        
        # Create first tab
        self._create_new_tab()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _create_interface(self):
        """Create the main tabbed interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab control frame
        tab_control_frame = ttk.Frame(main_frame)
        tab_control_frame.pack(fill="x", pady=(0, 5))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(tab_control_frame)
        self.notebook.pack(fill="both", expand=True, side="left")
        
        # Tab control buttons
        button_frame = ttk.Frame(tab_control_frame)
        button_frame.pack(side="right", padx=(5, 0))
        
        # New tab button
        new_tab_btn = ttk.Button(
            button_frame, 
            text="+ Nueva Pestaña", 
            command=self._create_new_tab,
            width=15
        )
        new_tab_btn.pack(side="top", pady=(0, 2))
        
        # Duplicate tab button
        duplicate_btn = ttk.Button(
            button_frame, 
            text="Duplicar", 
            command=self._duplicate_current_tab,
            width=15
        )
        duplicate_btn.pack(side="top", pady=(0, 2))
        
        # Close tab button
        close_btn = ttk.Button(
            button_frame, 
            text="Cerrar Pestaña", 
            command=self._close_current_tab,
            width=15
        )
        close_btn.pack(side="top")
        
        # Bind tab selection event
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
        # Status bar
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.pack(fill="x", side="bottom", pady=(5, 0))
        
        self.status_label = ttk.Label(self.status_frame, text="Listo")
        self.status_label.pack(side="left")
        
        # Tab info label
        self.tab_info_label = ttk.Label(self.status_frame, text="")
        self.tab_info_label.pack(side="right")
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for tab navigation"""
        self.root.bind("<Control-t>", lambda e: self._create_new_tab())
        self.root.bind("<Control-w>", lambda e: self._close_current_tab())
        self.root.bind("<Control-Tab>", lambda e: self._next_tab())
        self.root.bind("<Control-Shift-Tab>", lambda e: self._previous_tab())
        self.root.bind("<Control-d>", lambda e: self._duplicate_current_tab())
        
        # Number keys for direct tab access (Ctrl+1, Ctrl+2, etc.)
        for i in range(1, 10):
            self.root.bind(f"<Control-{i}>", lambda e, idx=i-1: self._select_tab_by_index(idx))
    
    def _create_new_tab(self, duplicate_from: Optional[str] = None) -> str:
        """Create a new tab"""
        # Generate unique tab ID
        tab_id = str(uuid.uuid4())
        self.tab_counter += 1
        
        # Create tab session
        tab_session = TabSession(tab_id, self.user_data)
        
        # Create tab frame
        tab_frame = ttk.Frame(self.notebook)
        tab_session.tab_frame = tab_frame
        
        # Create receipt app instance in this tab
        try:
            # Create a custom root-like object that handles the title attribute
            class TabFrameRoot:
                def __init__(self, frame, main_window):
                    self.frame = frame
                    self.main_window = main_window
                    self.title_text = ""
                
                def title(self, text=None):
                    if text is not None:
                        self.title_text = text
                    return self.title_text
                
                def geometry(self, geom=None):
                    # Ignore geometry calls for tabs
                    pass
                
                def protocol(self, protocol, callback):
                    # Ignore protocol calls for tabs
                    pass
                
                def winfo_toplevel(self):
                    # Return the main window for dialog creation
                    return self.main_window
                
                def __str__(self):
                    # When used as a parent for dialogs, return the main window path
                    return str(self.main_window)
                
                # Override special methods to make this work with tk.Toplevel
                def _register(self, func, subst=None, needcleanup=1):
                    return self.main_window._register(func, subst, needcleanup)
                
                def _root(self):
                    return self.main_window._root()
                
                @property
                def _w(self):
                    return self.main_window._w
                
                @property
                def tk(self):
                    return self.main_window.tk
                
                @property
                def master(self):
                    return self.main_window.master
                
                def call(self, *args):
                    # Delegate tcl/tk calls to main window
                    return self.main_window.call(*args)
                
                def report_callback_exception(self, *args):
                    # Delegate exception reporting to main window
                    return self.main_window.report_callback_exception(*args)
                
                def iconname(self, name=None):
                    # Delegate icon name to main window
                    return self.main_window.iconname(name)
                
                def wm_iconname(self, name=None):
                    # Delegate window manager icon name
                    return self.main_window.wm_iconname(name)
                
                def after(self, ms, func=None, *args):
                    # Delegate after calls to main window
                    return self.main_window.after(ms, func, *args)
                
                def after_idle(self, func, *args):
                    # Delegate after_idle calls to main window
                    return self.main_window.after_idle(func, *args)
                
                def after_cancel(self, id):
                    # Delegate after_cancel calls to main window
                    return self.main_window.after_cancel(id)
                
                def bell(self):
                    # Delegate bell to main window
                    return self.main_window.bell()
                
                def clipboard_get(self):
                    # Delegate clipboard operations to main window
                    return self.main_window.clipboard_get()
                
                def clipboard_clear(self):
                    # Delegate clipboard operations to main window
                    return self.main_window.clipboard_clear()
                
                def grab_set(self):
                    # Delegate grab operations to main window
                    return self.main_window.grab_set()
                
                def grab_release(self):
                    # Delegate grab operations to main window
                    return self.main_window.grab_release()
                
                def grab_current(self):
                    # Delegate grab operations to main window
                    return self.main_window.grab_current()
                
                def __getattr__(self, name):
                    # For main window related attributes, delegate to main window
                    main_window_attrs = [
                        'winfo_x', 'winfo_y', 'winfo_width', 'winfo_height', 
                        'winfo_screenwidth', 'winfo_screenheight', 'winfo_rootx', 'winfo_rooty',
                        'winfo_reqwidth', 'winfo_reqheight', 'winfo_parent', 'winfo_pathname',
                        'winfo_class', 'winfo_toplevel', 'children', 'update', 'update_idletasks',
                        'nametowidget', 'winfo_name', 'winfo_id', 'winfo_children', 'winfo_exists',
                        'winfo_fpixels', 'winfo_pixels', 'winfo_rgb', 'winfo_server', 'winfo_visual',
                        'winfo_visualid', 'winfo_vrootheight', 'winfo_vrootwidth', 'winfo_vrootx',
                        'winfo_vrooty', 'focus_set', 'focus_get', 'focus_force', 'focus_lastfor',
                        'selection_clear', 'selection_get', 'selection_handle', 'selection_own',
                        'selection_own_get', 'send', 'tkraise', 'lower', 'colormodel', 'getvar',
                        'setvar', 'globalgetvar', 'globalsetvar', 'getboolean', 'getdouble', 'getint',
                        'image_names', 'image_types', 'mainloop', 'quit', 'tk_bisque', 'tk_focusNext',
                        'tk_focusPrev', 'tk_focusFollowsMouse', 'tk_strictMotif', 'tk_setPalette',
                        'wait_variable', 'wait_window', 'wait_visibility', 'event_add', 'event_delete',
                        'event_generate', 'event_info', 'bind', 'bind_all', 'bind_class', 'unbind',
                        'unbind_all', 'unbind_class', 'bindtags', 'unbind_all', 'bindtags'
                    ]
                    
                    if name in main_window_attrs:
                        return getattr(self.main_window, name)
                    
                    # For frame-related attributes, delegate to frame
                    try:
                        return getattr(self.frame, name)
                    except AttributeError:
                        # If frame doesn't have it, try main window as fallback
                        return getattr(self.main_window, name)
            
            # Create the wrapper and pass it to ReciboAppMejorado
            tab_root = TabFrameRoot(tab_frame, self.root)
            app_instance = ReciboAppMejorado(tab_root, self.user_data)
            tab_session.app_instance = app_instance
            
            # If duplicating from another tab, copy its state
            if duplicate_from and duplicate_from in self.tabs:
                self._copy_tab_state(duplicate_from, tab_session)
            
            # Store tab session
            self.tabs[tab_id] = tab_session
            
            # Add tab to notebook
            initial_title = tab_session.get_tab_title()
            self.notebook.add(tab_frame, text=initial_title)
            
            # Select the new tab
            self.notebook.select(tab_frame)
            self.current_tab_id = tab_id
            
            # Setup monitoring for this tab
            self._setup_tab_monitoring(tab_session)
            
            # Update UI
            self._update_tab_info()
            
            return tab_id
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear nueva pestaña: {str(e)}")
            return None
    
    def _copy_tab_state(self, source_tab_id: str, target_session: TabSession):
        """Copy state from one tab to another"""
        source_session = self.tabs[source_tab_id]
        source_app = source_session.app_instance
        target_app = target_session.app_instance
        
        if not source_app or not target_app:
            return
        
        try:
            # Copy group selection
            if source_app.current_group:
                target_app.grupo_seleccionado.set(source_app.current_group['clave_grupo'])
                target_app.on_group_change()
            
            # Copy client selection
            if source_app.current_client:
                # Find the client display name
                client_type = source_app.db_manager.get_client_type_name(source_app.current_client.id_tipo_cliente)
                display_name = f"{source_app.current_client.nombre_cliente} ({client_type})"
                target_app.cliente_seleccionado.set(display_name)
                target_app.on_client_change()
            
            # Copy sectioning state
            if source_app.sectioning_var and target_app.sectioning_var:
                target_app.sectioning_var.set(source_app.sectioning_var.get())
                target_app.on_sectioning_toggle()
            
            # Copy database save preference
            target_app.guardar_en_bd.set(source_app.guardar_en_bd.get())
            
            # Note: Cart contents are intentionally not copied for a fresh start
            
        except Exception as e:
            print(f"Warning: Could not fully copy tab state: {e}")
    
    def _setup_tab_monitoring(self, tab_session: TabSession):
        """Setup monitoring for tab state changes"""
        app = tab_session.app_instance
        if not app:
            return
        
        # Monitor cart changes
        original_update_cart = app._update_cart_display
        
        def monitored_update_cart():
            original_update_cart()
            # Update tab session status
            cart_count = app.cart_manager.get_cart_count()
            client_name = app.current_client.nombre_cliente if app.current_client else ""
            tab_session.update_status(client_name, cart_count, cart_count > 0)
            
            # Update tab title
            self._update_tab_title(tab_session.tab_id)
            
            # Update tab info
            if self.current_tab_id == tab_session.tab_id:
                self._update_tab_info()
        
        app._update_cart_display = monitored_update_cart
        
        # Monitor client changes
        original_client_change = app.on_client_change
        
        def monitored_client_change(event=None):
            original_client_change(event)
            # Update tab session status
            client_name = app.current_client.nombre_cliente if app.current_client else ""
            tab_session.update_status(client_name, tab_session.cart_count, tab_session.has_unsaved_changes)
            
            # Update tab title
            self._update_tab_title(tab_session.tab_id)
            
            # Update tab info
            if self.current_tab_id == tab_session.tab_id:
                self._update_tab_info()
        
        app.on_client_change = monitored_client_change
    
    def _update_tab_title(self, tab_id: str):
        """Update the title of a specific tab"""
        if tab_id not in self.tabs:
            return
        
        tab_session = self.tabs[tab_id]
        tab_frame = self._get_tab_frame(tab_id)
        
        if tab_frame:
            title = tab_session.get_tab_title()
            if tab_session.has_data():
                title += " •"  # Indicate unsaved changes
            
            # Find tab index and update title
            for i in range(self.notebook.index("end")):
                if self.notebook.nametowidget(self.notebook.tabs()[i]) == tab_frame:
                    self.notebook.tab(i, text=title)
                    break
    
    def _get_tab_frame(self, tab_id: str) -> Optional[ttk.Frame]:
        """Get the frame widget for a specific tab"""
        if tab_id not in self.tabs:
            return None
        
        return self.tabs[tab_id].tab_frame
    
    def _duplicate_current_tab(self):
        """Duplicate the current tab"""
        if self.current_tab_id:
            self._create_new_tab(duplicate_from=self.current_tab_id)
    
    def _close_current_tab(self):
        """Close the current tab"""
        if self.current_tab_id:
            self._close_tab(self.current_tab_id)
    
    def _close_tab(self, tab_id: str):
        """Close a specific tab"""
        if tab_id not in self.tabs:
            return
        
        tab_session = self.tabs[tab_id]
        
        # Check if tab has unsaved data
        if tab_session.has_data():
            client_info = f" para {tab_session.client_name}" if tab_session.client_name else ""
            if not messagebox.askyesno(
                "Confirmar cierre",
                f"La pestaña{client_info} tiene {tab_session.cart_count} productos en el carrito.\n\n"
                "¿Está seguro que desea cerrarla? Se perderán los datos no guardados.",
                icon="warning"
            ):
                return
        
        # Don't allow closing the last tab
        if len(self.tabs) == 1:
            if messagebox.askyesno(
                "Última pestaña",
                "Esta es la última pestaña. ¿Desea crear una nueva pestaña antes de cerrar esta?",
                icon="question"
            ):
                self._create_new_tab()
            else:
                return
        
        # Find and remove tab from notebook
        tab_frame = self._get_tab_frame(tab_id)
        if tab_frame:
            for i in range(self.notebook.index("end")):
                if self.notebook.nametowidget(self.notebook.tabs()[i]) == tab_frame:
                    self.notebook.forget(i)
                    break
        
        # Cleanup tab session
        if tab_session.app_instance:
            try:
                # Cleanup database connections
                if hasattr(tab_session.app_instance, 'db_manager'):
                    tab_session.app_instance.db_manager.close()
            except:
                pass
        
        # Remove from tabs dictionary
        del self.tabs[tab_id]
        
        # Update current tab
        if self.current_tab_id == tab_id:
            self.current_tab_id = None
            self._on_tab_changed(None)
    
    def _next_tab(self):
        """Switch to next tab"""
        current_index = self.notebook.index("current")
        next_index = (current_index + 1) % self.notebook.index("end")
        self.notebook.select(next_index)
    
    def _previous_tab(self):
        """Switch to previous tab"""
        current_index = self.notebook.index("current")
        prev_index = (current_index - 1) % self.notebook.index("end")
        self.notebook.select(prev_index)
    
    def _select_tab_by_index(self, index: int):
        """Select tab by index"""
        if 0 <= index < self.notebook.index("end"):
            self.notebook.select(index)
    
    def _on_tab_changed(self, event):
        """Handle tab selection change"""
        try:
            current_tab_widget = self.notebook.nametowidget(self.notebook.select())
            
            # Find which tab session corresponds to this widget
            self.current_tab_id = None
            for tab_id, tab_session in self.tabs.items():
                if tab_session.tab_frame == current_tab_widget:
                    self.current_tab_id = tab_id
                    break
            
            self._update_tab_info()
            
        except Exception as e:
            print(f"Error in tab change handler: {e}")
    
    def _update_tab_info(self):
        """Update the tab information display"""
        if self.current_tab_id and self.current_tab_id in self.tabs:
            tab_session = self.tabs[self.current_tab_id]
            info_text = f"Pestaña: {tab_session.get_tab_title()} | "
            info_text += f"Total pestañas: {len(self.tabs)}"
            
            if tab_session.cart_count > 0:
                info_text += f" | Carrito: {tab_session.cart_count} productos"
            
            self.tab_info_label.config(text=info_text)
        else:
            self.tab_info_label.config(text=f"Total pestañas: {len(self.tabs)}")
    
    def _on_window_close(self):
        """Handle window close event"""
        # Check for unsaved changes in any tab
        tabs_with_data = []
        for tab_id, tab_session in self.tabs.items():
            if tab_session.has_data():
                tabs_with_data.append(tab_session)
        
        if tabs_with_data:
            tab_names = [tab.get_tab_title() for tab in tabs_with_data]
            message = f"Las siguientes pestañas tienen datos no guardados:\n\n"
            message += "\n".join(f"• {name}" for name in tab_names)
            message += "\n\n¿Está seguro que desea cerrar la aplicación?"
            
            if not messagebox.askyesno(
                "Datos no guardados",
                message,
                icon="warning"
            ):
                return
        
        # Cleanup all tabs
        for tab_session in self.tabs.values():
            if tab_session.app_instance:
                try:
                    if hasattr(tab_session.app_instance, 'db_manager'):
                        tab_session.app_instance.db_manager.close()
                except:
                    pass
        
        # Close the application
        self.root.destroy()
    
    def get_current_tab_session(self) -> Optional[TabSession]:
        """Get the current active tab session"""
        if self.current_tab_id and self.current_tab_id in self.tabs:
            return self.tabs[self.current_tab_id]
        return None
    
    def get_tab_count(self) -> int:
        """Get the number of open tabs"""
        return len(self.tabs)


if __name__ == "__main__":
    root = tk.Tk()
    user_data = {
        'nombre_completo': 'Usuario Prueba',
        'rol': 'admin'
    }
    app = TabbedReceiptApp(root, user_data)
    root.mainloop()