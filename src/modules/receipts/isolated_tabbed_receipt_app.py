import tkinter as tk
from tkinter import ttk, messagebox
import json
import uuid
import copy
from typing import Dict, List, Optional, Any
from datetime import datetime

from .receipt_generator_refactored import ReciboAppMejorado


class IsolatedTabSession:
    """Completely isolated tab session management"""
    
    def __init__(self, tab_id: str, user_data: Dict[str, Any]):
        self.tab_id = tab_id
        # Deep copy user data to prevent any reference sharing
        self.user_data = copy.deepcopy(user_data)
        self.app_instance: Optional[ReciboAppMejorado] = None
        self.tab_frame: Optional[ttk.Frame] = None
        self.client_name = ""
        self.cart_count = 0
        self.created_at = datetime.now()
        
    def get_tab_title(self) -> str:
        if self.client_name:
            return f"{self.client_name}"
        return f"Sesión #{self.tab_id[-4:]}"  # Show last 4 chars of UUID for uniqueness
    
    def has_data(self) -> bool:
        return self.cart_count > 0
    
    def update_status(self, client_name: str = "", cart_count: int = 0):
        self.client_name = client_name
        self.cart_count = cart_count


class IsolatedRootWrapper:
    """Completely isolated root wrapper for each tab"""
    
    def __init__(self, tab_frame: ttk.Frame, main_window: tk.Tk, tab_id: str):
        self.tab_frame = tab_frame
        self.main_window = main_window
        self.tab_id = tab_id
        self.title_text = f"Tab {tab_id[-4:]}"
        # Store widget references specific to this tab
        self._tab_widgets = {}
    
    def title(self, text=None):
        if text is not None:
            self.title_text = text
        return self.title_text
    
    def geometry(self, geom=None):
        # Ignore geometry calls for tabs
        pass
    
    def protocol(self, protocol, callback):
        # Store protocol callbacks per tab if needed
        pass
    
    # Essential delegation methods for dialog creation
    def winfo_toplevel(self):
        return self.main_window
    
    def winfo_x(self):
        return self.main_window.winfo_x()
    
    def winfo_y(self):
        return self.main_window.winfo_y()
    
    def winfo_width(self):
        return self.main_window.winfo_width()
    
    def winfo_height(self):
        return self.main_window.winfo_height()
    
    def winfo_screenwidth(self):
        return self.main_window.winfo_screenwidth()
    
    def winfo_screenheight(self):
        return self.main_window.winfo_screenheight()
    
    def winfo_rootx(self):
        return self.main_window.winfo_rootx()
    
    def winfo_rooty(self):
        return self.main_window.winfo_rooty()
    
    def update(self):
        return self.main_window.update()
    
    def update_idletasks(self):
        return self.main_window.update_idletasks()
    
    def after(self, ms, func=None, *args):
        return self.main_window.after(ms, func, *args)
    
    def after_idle(self, func, *args):
        return self.main_window.after_idle(func, *args)
    
    def after_cancel(self, id):
        return self.main_window.after_cancel(id)
    
    def bell(self):
        return self.main_window.bell()
    
    def report_callback_exception(self, *args):
        return self.main_window.report_callback_exception(*args)
    
    def grab_set(self):
        return self.main_window.grab_set()
    
    def grab_release(self):
        return self.main_window.grab_release()
    
    def grab_current(self):
        return self.main_window.grab_current()
    
    @property
    def tk(self):
        return self.main_window.tk
    
    @property
    def master(self):
        return self.main_window.master
    
    def __str__(self):
        return str(self.main_window)
    
    def __getattr__(self, name):
        """Delegate missing attributes carefully"""
        # For attributes that should come from the main window
        main_window_attrs = {
            'winfo_reqwidth', 'winfo_reqheight', 'winfo_parent', 'winfo_pathname',
            'winfo_class', 'children', 'nametowidget', 'winfo_name', 'winfo_id', 
            'winfo_children', 'winfo_exists', 'winfo_fpixels', 'winfo_pixels', 
            'winfo_rgb', 'winfo_server', 'winfo_visual', 'winfo_visualid', 
            'winfo_vrootheight', 'winfo_vrootwidth', 'winfo_vrootx', 'winfo_vrooty',
            'focus_set', 'focus_get', 'focus_force', 'focus_lastfor', 'selection_clear',
            'selection_get', 'selection_handle', 'selection_own', 'selection_own_get',
            'send', 'tkraise', 'lower', 'colormodel', 'getvar', 'setvar', 
            'globalgetvar', 'globalsetvar', 'getboolean', 'getdouble', 'getint',
            'image_names', 'image_types', 'mainloop', 'quit', 'wait_variable', 
            'wait_window', 'wait_visibility', 'event_add', 'event_delete', 
            'event_generate', 'event_info', 'bind', 'bind_all', 'bind_class', 
            'unbind', 'unbind_all', 'unbind_class', 'bindtags'
        }
        
        if name in main_window_attrs:
            return getattr(self.main_window, name)
        
        # For frame-related attributes
        try:
            return getattr(self.tab_frame, name)
        except AttributeError:
            # Fallback to main window for compatibility
            try:
                return getattr(self.main_window, name)
            except AttributeError:
                # Return None for missing attributes to prevent crashes
                return None


class IsolatedTabbedReceiptApp:
    """Completely isolated multi-tab wrapper for the receipt generator application"""
    
    def __init__(self, root: tk.Tk, user_data: Dict[str, Any]):
        self.root = root
        self.root.title("Generador de Recibos - Multi-Tab (Aislado)")
        self.root.geometry("1200x800")
        # Deep copy user data to prevent any reference sharing
        self.user_data = copy.deepcopy(user_data)
        
        # Tab management
        self.tabs: Dict[str, IsolatedTabSession] = {}
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
        
        self.status_label = ttk.Label(self.status_frame, text="Aplicación iniciada - Estado aislado")
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
        
        # Number keys for direct tab access
        for i in range(1, 10):
            self.root.bind(f"<Control-{i}>", lambda e, idx=i-1: self._select_tab_by_index(idx))
    
    def _create_new_tab(self) -> str:
        """Create a completely isolated new tab"""
        try:
            # Generate unique tab ID
            tab_id = str(uuid.uuid4())
            self.tab_counter += 1
            
            print(f"Creating isolated tab {self.tab_counter} with ID: {tab_id[-8:]}")
            
            # Create tab session with deep copied data
            tab_session = IsolatedTabSession(tab_id, self.user_data)
            
            # Create tab frame without custom name to avoid widget path conflicts
            tab_frame = ttk.Frame(self.notebook)
            tab_session.tab_frame = tab_frame
            
            # Create completely isolated root wrapper
            tab_root = IsolatedRootWrapper(tab_frame, self.root, tab_id)
            
            # Create new app instance with isolated data
            print(f"Creating ReciboAppMejorado instance for tab {self.tab_counter}")
            app_instance = ReciboAppMejorado(tab_root, tab_session.user_data)
            tab_session.app_instance = app_instance
            
            # Verify isolation by checking if instances are different
            if len(self.tabs) > 0:
                first_tab = list(self.tabs.values())[0]
                print(f"Instance comparison - Current: {id(app_instance)}, First: {id(first_tab.app_instance)}")
                print(f"DB Manager comparison - Current: {id(app_instance.db_manager)}, First: {id(first_tab.app_instance.db_manager)}")
                print(f"Cart Manager comparison - Current: {id(app_instance.cart_manager)}, First: {id(first_tab.app_instance.cart_manager)}")
            
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
            
            print(f"Successfully created isolated tab {self.tab_counter}")
            return tab_id
            
        except Exception as e:
            print(f"Error creating tab: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al crear nueva pestaña: {str(e)}")
            return None
    
    def _setup_tab_monitoring(self, tab_session: IsolatedTabSession):
        """Setup monitoring for tab state changes with complete isolation"""
        app = tab_session.app_instance
        if not app:
            return
        
        try:
            # Create isolated monitoring functions that don't interfere with other tabs
            original_update_cart = app._update_cart_display
            
            def isolated_update_cart():
                """Isolated cart update that only affects this tab"""
                try:
                    original_update_cart()
                    # Update only this tab's session status
                    cart_count = app.cart_manager.get_cart_count() if hasattr(app, 'cart_manager') else 0
                    client_name = app.current_client.nombre_cliente if hasattr(app, 'current_client') and app.current_client else ""
                    tab_session.update_status(client_name, cart_count)
                    
                    # Update only this tab's title
                    self._update_tab_title(tab_session.tab_id)
                    
                    # Update UI only if this is the current tab
                    if self.current_tab_id == tab_session.tab_id:
                        self._update_tab_info()
                        
                except Exception as e:
                    print(f"Error in isolated cart update for tab {tab_session.tab_id[-8:]}: {e}")
            
            app._update_cart_display = isolated_update_cart
            
            # Monitor client changes with isolation
            original_client_change = app.on_client_change
            
            def isolated_client_change(event=None):
                """Isolated client change that only affects this tab"""
                try:
                    original_client_change(event)
                    # Update only this tab's session status
                    client_name = app.current_client.nombre_cliente if hasattr(app, 'current_client') and app.current_client else ""
                    tab_session.update_status(client_name, tab_session.cart_count)
                    
                    # Update only this tab's title
                    self._update_tab_title(tab_session.tab_id)
                    
                    # Update UI only if this is the current tab
                    if self.current_tab_id == tab_session.tab_id:
                        self._update_tab_info()
                        
                except Exception as e:
                    print(f"Error in isolated client change for tab {tab_session.tab_id[-8:]}: {e}")
            
            app.on_client_change = isolated_client_change
            
            print(f"Setup isolated monitoring for tab {tab_session.tab_id[-8:]}")
            
        except Exception as e:
            print(f"Warning: Could not setup isolated monitoring for tab {tab_session.tab_id[-8:]}: {e}")
    
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
            print(f"Warning: Could not update tab title for {tab_id[-8:]}: {e}")
    
    def _close_current_tab(self):
        """Close the current tab"""
        if self.current_tab_id:
            self._close_tab(self.current_tab_id)
    
    def _close_tab(self, tab_id: str):
        """Close a specific tab with proper cleanup"""
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
            
            print(f"Closing isolated tab {tab_id[-8:]}")
            
            # Find and remove tab from notebook
            tab_frame = tab_session.tab_frame
            if tab_frame:
                for i in range(self.notebook.index("end")):
                    if self.notebook.nametowidget(self.notebook.tabs()[i]) == tab_frame:
                        self.notebook.forget(i)
                        break
            
            # Cleanup tab session with proper isolation
            if tab_session.app_instance:
                try:
                    # Close database connections for this specific instance
                    if hasattr(tab_session.app_instance, 'db_manager'):
                        tab_session.app_instance.db_manager.close()
                        print(f"Closed database connection for tab {tab_id[-8:]}")
                except Exception as e:
                    print(f"Warning: Error closing database for tab {tab_id[-8:]}: {e}")
            
            # Remove from tabs dictionary
            del self.tabs[tab_id]
            
            # Update current tab reference
            if self.current_tab_id == tab_id:
                self.current_tab_id = None
                self._on_tab_changed(None)
            
            print(f"Successfully closed isolated tab {tab_id[-8:]}")
            
        except Exception as e:
            print(f"Warning: Error closing tab {tab_id[-8:]}: {e}")
    
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
            old_tab_id = self.current_tab_id
            self.current_tab_id = None
            
            for tab_id, tab_session in self.tabs.items():
                if tab_session.tab_frame == current_tab_widget:
                    self.current_tab_id = tab_id
                    break
            
            if old_tab_id != self.current_tab_id:
                print(f"Tab changed from {old_tab_id[-8:] if old_tab_id else 'None'} to {self.current_tab_id[-8:] if self.current_tab_id else 'None'}")
            
            self._update_tab_info()
            
        except Exception as e:
            print(f"Warning: Error in tab change handler: {e}")
    
    def _update_tab_info(self):
        """Update the tab information display"""
        try:
            if self.current_tab_id and self.current_tab_id in self.tabs:
                tab_session = self.tabs[self.current_tab_id]
                info_text = f"Pestaña Activa: {tab_session.get_tab_title()} | "
                info_text += f"Total: {len(self.tabs)} pestañas"
                
                if tab_session.cart_count > 0:
                    info_text += f" | Carrito: {tab_session.cart_count} productos"
                
                self.tab_info_label.config(text=info_text)
            else:
                self.tab_info_label.config(text=f"Total pestañas: {len(self.tabs)}")
        except:
            pass
    
    def _on_window_close(self):
        """Handle window close event with proper cleanup"""
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
            
            print("Cleaning up all isolated tabs...")
            
            # Cleanup all tabs with proper isolation
            for tab_id, tab_session in self.tabs.items():
                if tab_session.app_instance:
                    try:
                        if hasattr(tab_session.app_instance, 'db_manager'):
                            tab_session.app_instance.db_manager.close()
                            print(f"Closed database for tab {tab_id[-8:]}")
                    except Exception as e:
                        print(f"Warning: Error closing database for tab {tab_id[-8:]}: {e}")
            
            print("All tabs cleaned up. Closing application.")
            
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
    app = IsolatedTabbedReceiptApp(root, user_data)
    root.mainloop()