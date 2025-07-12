import tkinter as tk
from tkinter import ttk, messagebox
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from .receipt_generator_refactored import ReciboAppMejorado


class SimpleTabSession:
    """Simple tab session management"""
    
    def __init__(self, tab_id: str, user_data: Dict[str, Any]):
        self.tab_id = tab_id
        self.user_data = user_data
        self.app_instance: Optional[ReciboAppMejorado] = None
        self.tab_frame: Optional[ttk.Frame] = None
        self.client_name = ""
        self.cart_count = 0
        self.created_at = datetime.now()
        
    def get_tab_title(self) -> str:
        if self.client_name:
            return f"{self.client_name}"
        return "Nueva Sesión"
    
    def has_data(self) -> bool:
        return self.cart_count > 0
    
    def update_status(self, client_name: str = "", cart_count: int = 0):
        self.client_name = client_name
        self.cart_count = cart_count


class SimpleTabbedReceiptApp:
    """Simple multi-tab wrapper for the receipt generator application"""
    
    def __init__(self, root: tk.Tk, user_data: Dict[str, Any]):
        self.root = root
        self.root.title("Generador de Recibos - Multi-Tab")
        self.root.geometry("1200x800")
        self.user_data = user_data
        
        # Tab management
        self.tabs: Dict[str, SimpleTabSession] = {}
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
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.tab_control_frame)
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
    
    def _create_new_tab(self) -> str:
        """Create a new tab"""
        try:
            # Generate unique tab ID
            tab_id = str(uuid.uuid4())
            self.tab_counter += 1
            
            # Create tab session
            tab_session = SimpleTabSession(tab_id, self.user_data)
            
            # Create tab frame
            tab_frame = ttk.Frame(self.notebook)
            tab_session.tab_frame = tab_frame
            
            # Create the receipt app instance directly in the tab frame
            # Use a custom root-like object that handles the title attribute
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
                
                def __getattr__(self, name):
                    # For any missing attributes, delegate to main window
                    try:
                        return getattr(self.main_window, name)
                    except AttributeError:
                        # If main window doesn't have it, try frame
                        try:
                            return getattr(self.frame, name)
                        except AttributeError:
                            return None
            
            # Create the wrapper and pass it to ReciboAppMejorado
            tab_root = TabFrameRoot(tab_frame, self.root)
            # Create a deep copy of user_data to ensure complete isolation
            import copy
            isolated_user_data = copy.deepcopy(self.user_data)
            
            # Add unique identifier to prevent any potential sharing
            isolated_user_data['_tab_id'] = tab_id
            isolated_user_data['_tab_instance'] = self.tab_counter
            
            app_instance = ReciboAppMejorado(tab_root, isolated_user_data)
            tab_session.app_instance = app_instance
            
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
    
    def _setup_tab_monitoring(self, tab_session: SimpleTabSession):
        """Setup monitoring for tab state changes"""
        app = tab_session.app_instance
        if not app:
            return
        
        try:
            # Monitor cart changes
            if hasattr(app, '_update_cart_display'):
                original_update_cart = app._update_cart_display
                
                def monitored_update_cart():
                    original_update_cart()
                    # Update tab session status
                    cart_count = app.cart_manager.get_cart_count() if hasattr(app, 'cart_manager') else 0
                    client_name = app.current_client.nombre_cliente if hasattr(app, 'current_client') and app.current_client else ""
                    tab_session.update_status(client_name, cart_count)
                    
                    # Update tab title
                    self._update_tab_title(tab_session.tab_id)
                    
                    # Update tab info
                    if self.current_tab_id == tab_session.tab_id:
                        self._update_tab_info()
                
                app._update_cart_display = monitored_update_cart
            
            # Monitor client changes
            if hasattr(app, 'on_client_change'):
                original_client_change = app.on_client_change
                
                def monitored_client_change(event=None):
                    original_client_change(event)
                    # Update tab session status
                    client_name = app.current_client.nombre_cliente if hasattr(app, 'current_client') and app.current_client else ""
                    tab_session.update_status(client_name, tab_session.cart_count)
                    
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
    app = SimpleTabbedReceiptApp(root, user_data)
    root.mainloop()