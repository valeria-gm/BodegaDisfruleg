import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Any

from .receipt_generator_refactored import ReciboAppMejorado
from .core import (TabRootWrapper, IsolatedRootWrapper, TabSession, IsolatedTabSession, 
                   TabSessionFactory, AppFactory, setup_tab_monitoring)


class TabbedReceiptAppConsolidated:
    """Consolidated multi-tab wrapper for the receipt generator application"""
    
    def __init__(self, root: tk.Tk, user_data: Dict[str, Any], mode: str = "standard"):
        self.root = root
        self.root.title("Generador de Recibos - Multi-Tab")
        self.root.geometry("1200x800")
        self.user_data = user_data
        self.mode = mode  # "standard" or "isolated"
        
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
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab control frame
        self.tab_control_frame = ttk.Frame(self.main_frame)
        self.tab_control_frame.pack(fill="x", pady=(0, 5))
        
        # Create notebook for tabs
        notebook_name = f"{self.mode}_receipt_notebook"
        self.notebook = ttk.Notebook(self.tab_control_frame, name=notebook_name)
        self.notebook.pack(fill="both", expand=True, side="left")
        
        # Tab control buttons
        self._create_control_buttons()
        
        # Bind tab selection event
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
        # Status bar
        self._create_status_bar()
    
    def _create_control_buttons(self):
        """Create tab control buttons"""
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
        
        # Duplicate tab button (only in standard mode)
        if self.mode == "standard":
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
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill="x", side="bottom", pady=(5, 0))
        
        status_text = "Listo" if self.mode == "standard" else "Aplicación iniciada - Estado aislado"
        self.status_label = ttk.Label(self.status_frame, text=status_text)
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
        
        if self.mode == "standard":
            self.root.bind("<Control-d>", lambda e: self._duplicate_current_tab())
        
        # Number keys for direct tab access (Ctrl+1, Ctrl+2, etc.)
        for i in range(1, 10):
            self.root.bind(f"<Control-{i}>", lambda e, idx=i-1: self._select_tab_by_index(idx))
    
    def _create_new_tab(self, duplicate_from: Optional[str] = None) -> str:
        """Create a new tab"""
        try:
            # Create tab session using factory
            session_type = "isolated" if self.mode == "isolated" else "standard"
            tab_session = TabSessionFactory.create_session(session_type, self.user_data)
            self.tab_counter += 1
            
            if self.mode == "isolated":
                print(f"Creating isolated tab {self.tab_counter} with ID: {tab_session.tab_id[-8:]}")
            
            # Create tab frame
            tab_frame = ttk.Frame(self.notebook, name=f"tab_frame_{self.tab_counter}")
            tab_session.tab_frame = tab_frame
            
            # Create root wrapper based on mode
            if self.mode == "isolated":
                tab_root = IsolatedRootWrapper(tab_frame, self.root, tab_session.tab_id)
            else:
                tab_root = TabRootWrapper(tab_frame, self.root, tab_session.tab_id)
            
            # Create app instance using factory
            app_instance = AppFactory.create_app_for_mode(
                mode=self.mode,
                root_or_frame=tab_frame,
                user_data=tab_session.user_data,
                tab_id=tab_session.tab_id,
                main_window=self.root
            )
            
            tab_session.app_instance = app_instance
            
            # Copy state if duplicating
            if duplicate_from and duplicate_from in self.tabs and self.mode == "standard":
                self._copy_tab_state(duplicate_from, tab_session)
            
            # Store tab session
            self.tabs[tab_session.tab_id] = tab_session
            
            # Add tab to notebook
            initial_title = tab_session.get_tab_title()
            self.notebook.add(tab_frame, text=initial_title)
            
            # Select the new tab
            self.notebook.select(tab_frame)
            self.current_tab_id = tab_session.tab_id
            
            # Setup monitoring for this tab
            self._setup_tab_monitoring(tab_session)
            
            # Update UI
            self._update_tab_info()
            
            if self.mode == "isolated":
                print(f"Successfully created isolated tab {self.tab_counter}")
            
            return tab_session.tab_id
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear nueva pestaña: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _copy_tab_state(self, source_tab_id: str, target_session):
        """Copy state from one tab to another (standard mode only)"""
        if self.mode == "isolated":
            return
            
        try:
            source_session = self.tabs[source_tab_id]
            source_app = source_session.app_instance
            target_app = target_session.app_instance
            
            if not source_app or not target_app:
                return
            
            # Copy group selection
            if hasattr(source_app, 'current_group') and source_app.current_group:
                target_app.grupo_seleccionado.set(source_app.current_group['clave_grupo'])
                target_app.on_group_change()
            
            # Copy client selection
            if hasattr(source_app, 'current_client') and source_app.current_client:
                client_type = source_app.db_manager.get_client_type_name(source_app.current_client.id_tipo_cliente)
                display_name = f"{source_app.current_client.nombre_cliente} ({client_type})"
                target_app.cliente_seleccionado.set(display_name)
                target_app.on_client_change()
            
            # Copy sectioning state
            if (hasattr(source_app, 'sectioning_var') and hasattr(target_app, 'sectioning_var') and 
                source_app.sectioning_var and target_app.sectioning_var):
                target_app.sectioning_var.set(source_app.sectioning_var.get())
                target_app.on_sectioning_toggle()
            
            # Copy database save preference
            if hasattr(source_app, 'guardar_en_bd') and hasattr(target_app, 'guardar_en_bd'):
                target_app.guardar_en_bd.set(source_app.guardar_en_bd.get())
            
        except Exception as e:
            print(f"Warning: Could not fully copy tab state: {e}")
    
    def _setup_tab_monitoring(self, tab_session):
        """Setup monitoring for tab state changes using monitoring module"""
        def update_title():
            if self.current_tab_id == tab_session.tab_id:
                self._update_tab_info()
        
        setup_tab_monitoring(
            tab_session=tab_session,
            app_instance=tab_session.app_instance,
            update_tab_title_func=self._update_tab_title,
            update_tab_info_func=update_title
        )
    
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
        """Duplicate the current tab (standard mode only)"""
        if self.current_tab_id and self.mode == "standard":
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
            
            if self.mode == "isolated":
                print(f"Closing isolated tab {tab_id[-8:]}")
            
            # Find and remove tab from notebook
            tab_frame = tab_session.tab_frame
            if tab_frame:
                for i in range(self.notebook.index("end")):
                    if self.notebook.nametowidget(self.notebook.tabs()[i]) == tab_frame:
                        self.notebook.forget(i)
                        break
            
            # Cleanup tab session
            tab_session.cleanup()
            
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
            old_tab_id = self.current_tab_id
            self.current_tab_id = None
            for tab_id, tab_session in self.tabs.items():
                if tab_session.tab_frame == current_tab_widget:
                    self.current_tab_id = tab_id
                    break
            
            if self.mode == "isolated" and old_tab_id != self.current_tab_id:
                old_id = old_tab_id[-8:] if old_tab_id else 'None'
                new_id = self.current_tab_id[-8:] if self.current_tab_id else 'None'
                print(f"Tab changed from {old_id} to {new_id}")
            
            self._update_tab_info()
            
        except Exception as e:
            print(f"Warning: Error in tab change handler: {e}")
    
    def _update_tab_info(self):
        """Update the tab information display"""
        try:
            if self.current_tab_id and self.current_tab_id in self.tabs:
                tab_session = self.tabs[self.current_tab_id]
                if self.mode == "isolated":
                    info_text = f"Pestaña Activa: {tab_session.get_tab_title()} | "
                else:
                    info_text = f"Pestaña: {tab_session.get_tab_title()} | "
                info_text += f"Total: {len(self.tabs)} pestañas"
                
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
            
            if self.mode == "isolated":
                print("Cleaning up all isolated tabs...")
            
            # Cleanup all tabs
            for tab_session in self.tabs.values():
                tab_session.cleanup()
            
            if self.mode == "isolated":
                print("All tabs cleaned up. Closing application.")
            
            # Close the application
            self.root.destroy()
            
        except Exception as e:
            print(f"Warning: Error during window close: {e}")
            self.root.destroy()


# Convenience classes for specific modes
class TabbedReceiptApp(TabbedReceiptAppConsolidated):
    """Standard tabbed receipt app"""
    
    def __init__(self, root: tk.Tk, user_data: Dict[str, Any]):
        super().__init__(root, user_data, mode="standard")


class IsolatedTabbedReceiptApp(TabbedReceiptAppConsolidated):
    """Isolated tabbed receipt app"""
    
    def __init__(self, root: tk.Tk, user_data: Dict[str, Any]):
        super().__init__(root, user_data, mode="isolated")


if __name__ == "__main__":
    root = tk.Tk()
    user_data = {
        'nombre_completo': 'Usuario Prueba',
        'rol': 'admin'
    }
    
    # You can use either:
    # app = TabbedReceiptApp(root, user_data)  # Standard mode
    # app = IsolatedTabbedReceiptApp(root, user_data)  # Isolated mode
    # app = TabbedReceiptAppConsolidated(root, user_data, "standard")  # Explicit mode
    
    app = TabbedReceiptApp(root, user_data)
    root.mainloop()