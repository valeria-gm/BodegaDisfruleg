import tkinter as tk
from tkinter import ttk, messagebox
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from .receipt_generator_refactored import ReciboAppMejorado


class CleanTabSession:
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


class CleanRootWrapper:
    """A clean wrapper that provides minimal root window interface without conflicts"""
    
    def __init__(self, parent_window: tk.Tk):
        self.parent_window = parent_window
        self.title_text = ""
    
    def title(self, text=None):
        if text is not None:
            self.title_text = text
        return self.title_text
    
    def geometry(self, geom=None):
        # Ignore geometry calls
        pass
    
    def protocol(self, protocol, callback):
        # Ignore protocol calls
        pass
    
    # Essential methods for dialogs - delegate to parent window
    def winfo_toplevel(self):
        return self.parent_window
    
    def winfo_x(self):
        return self.parent_window.winfo_x()
    
    def winfo_y(self):
        return self.parent_window.winfo_y()
    
    def winfo_width(self):
        return self.parent_window.winfo_width()
    
    def winfo_height(self):
        return self.parent_window.winfo_height()
    
    def winfo_screenwidth(self):
        return self.parent_window.winfo_screenwidth()
    
    def winfo_screenheight(self):
        return self.parent_window.winfo_screenheight()
    
    def winfo_rootx(self):
        return self.parent_window.winfo_rootx()
    
    def winfo_rooty(self):
        return self.parent_window.winfo_rooty()
    
    def update(self):
        return self.parent_window.update()
    
    def update_idletasks(self):
        return self.parent_window.update_idletasks()
    
    def after(self, ms, func=None, *args):
        return self.parent_window.after(ms, func, *args)
    
    def after_idle(self, func, *args):
        return self.parent_window.after_idle(func, *args)
    
    def after_cancel(self, id):
        return self.parent_window.after_cancel(id)
    
    def bell(self):
        return self.parent_window.bell()
    
    def report_callback_exception(self, *args):
        return self.parent_window.report_callback_exception(*args)
    
    def iconname(self, name=None):
        return self.parent_window.iconname(name)
    
    def grab_set(self):
        return self.parent_window.grab_set()
    
    def grab_release(self):
        return self.parent_window.grab_release()
    
    def grab_current(self):
        return self.parent_window.grab_current()
    
    @property
    def tk(self):
        return self.parent_window.tk
    
    @property
    def master(self):
        return self.parent_window.master
    
    # Add the missing attribute and other common tkinter attributes
    @property
    def last_child_ids(self):
        return getattr(self.parent_window, 'last_child_ids', None)
    
    def __str__(self):
        return str(self.parent_window)
    
    def __getattr__(self, name):
        """Delegate any missing attributes to the parent window"""
        try:
            return getattr(self.parent_window, name)
        except AttributeError:
            # If the parent doesn't have it either, return None or raise
            if name.startswith('_'):
                return None
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


class CleanTabbedReceiptApp:
    """Clean multi-tab wrapper for the receipt generator application"""
    
    def __init__(self, root: tk.Tk, user_data: Dict[str, Any]):
        self.root = root
        self.root.title("Generador de Recibos - Multi-Tab")
        self.root.geometry("1200x800")
        self.user_data = user_data
        
        # Tab management
        self.tabs: Dict[str, CleanTabSession] = {}
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
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab control frame
        self.tab_control_frame = ttk.Frame(self.main_frame)
        self.tab_control_frame.pack(fill="x", pady=(0, 5))
        
        # Create notebook for tabs with unique name
        self.notebook = ttk.Notebook(self.tab_control_frame, name="clean_receipt_notebook")
        self.notebook.pack(fill="both", expand=True, side="left")
        
        # Tab control buttons
        self.button_frame = ttk.Frame(self.tab_control_frame)
        self.button_frame.pack(side="right", padx=(5, 0))
        
        # New tab button
        self.new_tab_btn = ttk.Button(
            self.button_frame, 
            text="+ Nueva Pestaña", 
            command=self._create_new_tab,
            width=15
        )
        self.new_tab_btn.pack(side="top", pady=(0, 2))
        
        # Duplicate tab button
        self.duplicate_btn = ttk.Button(
            self.button_frame, 
            text="Duplicar", 
            command=self._duplicate_current_tab,
            width=15
        )
        self.duplicate_btn.pack(side="top", pady=(0, 2))
        
        # Close tab button
        self.close_btn = ttk.Button(
            self.button_frame, 
            text="Cerrar Pestaña", 
            command=self._close_current_tab,
            width=15
        )
        self.close_btn.pack(side="top")
        
        # Bind tab selection event
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame)
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
        try:
            # Generate unique tab ID
            tab_id = str(uuid.uuid4())
            self.tab_counter += 1
            
            # Create tab session
            tab_session = CleanTabSession(tab_id, self.user_data)
            
            # Create tab frame with unique name
            tab_frame = ttk.Frame(self.notebook, name=f"tab_frame_{self.tab_counter}")
            tab_session.tab_frame = tab_frame
            
            # Create a temporary window for the receipt app
            temp_window = tk.Toplevel(self.root)
            temp_window.withdraw()  # Hide it immediately
            
            # Create the app instance with the temporary window
            app_instance = ReciboAppMejorado(temp_window, self.user_data)
            
            # Find the main content frame from the app
            main_content = None
            for child in temp_window.winfo_children():
                if isinstance(child, tk.Frame):
                    main_content = child
                    break
            
            if main_content:
                # Reparent the main content to our tab frame
                main_content.pack_forget()
                main_content.master = tab_frame
                main_content.pack(in_=tab_frame, fill="both", expand=True)
            
            # Destroy the temporary window
            temp_window.destroy()
            
            # Update the app's root reference to use our wrapper for dialogs
            wrapper = CleanRootWrapper(self.root)
            app_instance.root = wrapper
            
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
            import traceback
            traceback.print_exc()
            return None
    
    def _copy_tab_state(self, source_tab_id: str, target_session: CleanTabSession):
        """Copy state from one tab to another"""
        try:
            source_session = self.tabs[source_tab_id]
            source_app = source_session.app_instance
            target_app = target_session.app_instance
            
            if not source_app or not target_app:
                return
            
            # Copy group selection
            if source_app.current_group:
                target_app.grupo_seleccionado.set(source_app.current_group['clave_grupo'])
                target_app.on_group_change()
            
            # Copy client selection
            if source_app.current_client:
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
            
        except Exception as e:
            print(f"Warning: Could not fully copy tab state: {e}")
    
    def _setup_tab_monitoring(self, tab_session: CleanTabSession):
        """Setup monitoring for tab state changes"""
        app = tab_session.app_instance
        if not app:
            return
        
        try:
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
            
        except Exception as e:
            print(f"Warning: Could not setup tab monitoring: {e}")
    
    def _update_tab_title(self, tab_id: str):
        """Update the title of a specific tab"""
        if tab_id not in self.tabs:
            return
        
        try:
            tab_session = self.tabs[tab_id]
            tab_frame = tab_session.tab_frame
            
            if tab_frame:
                title = tab_session.get_tab_title()
                if tab_session.has_data():
                    title += " •"  # Indicate unsaved changes
                
                # Find tab index and update title
                for i in range(self.notebook.index("end")):
                    if self.notebook.nametowidget(self.notebook.tabs()[i]) == tab_frame:
                        self.notebook.tab(i, text=title)
                        break
        except Exception as e:
            print(f"Warning: Could not update tab title: {e}")
    
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
        
        try:
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
            tab_frame = tab_session.tab_frame
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
                
        except Exception as e:
            print(f"Warning: Error closing tab: {e}")
    
    def _next_tab(self):
        """Switch to next tab"""
        try:
            current_index = self.notebook.index("current")
            next_index = (current_index + 1) % self.notebook.index("end")
            self.notebook.select(next_index)
        except:
            pass
    
    def _previous_tab(self):
        """Switch to previous tab"""
        try:
            current_index = self.notebook.index("current")
            prev_index = (current_index - 1) % self.notebook.index("end")
            self.notebook.select(prev_index)
        except:
            pass
    
    def _select_tab_by_index(self, index: int):
        """Select tab by index"""
        try:
            if 0 <= index < self.notebook.index("end"):
                self.notebook.select(index)
        except:
            pass
    
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
            print(f"Warning: Error in tab change handler: {e}")
    
    def _update_tab_info(self):
        """Update the tab information display"""
        try:
            if self.current_tab_id and self.current_tab_id in self.tabs:
                tab_session = self.tabs[self.current_tab_id]
                info_text = f"Pestaña: {tab_session.get_tab_title()} | "
                info_text += f"Total pestañas: {len(self.tabs)}"
                
                if tab_session.cart_count > 0:
                    info_text += f" | Carrito: {tab_session.cart_count} productos"
                
                self.tab_info_label.config(text=info_text)
            else:
                self.tab_info_label.config(text=f"Total pestañas: {len(self.tabs)}")
        except:
            pass
    
    def _on_window_close(self):
        """Handle window close event"""
        try:
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
            
        except Exception as e:
            print(f"Warning: Error during window close: {e}")
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    user_data = {
        'nombre_completo': 'Usuario Prueba',
        'rol': 'admin'
    }
    app = CleanTabbedReceiptApp(root, user_data)
    root.mainloop()