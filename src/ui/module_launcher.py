"""
DISFRULEG - Module Launcher
Handles module definitions, launching, and management
"""

import os
import sys
import subprocess
from tkinter import messagebox
from src.config import debug_print, USE_SESSION_MANAGER

class ModuleLauncher:
    """Class for managing and launching application modules"""
    
    def __init__(self):
        self.modules = self._get_module_definitions()
    
    def _get_module_definitions(self):
        """Get all module definitions"""
        return [
            {
                'title': 'Generar Recibos',
                'description': 'Crear recibos para clientes\ny gestionar facturación',
                'module_key': 'receipts',
                'bg_color': '#3498DB',
                'hover_color': '#2980B9',
                'requires_admin': False
            },
            {
                'title': 'Editor de Precios',
                'description': 'Gestionar productos\ny precios por tipo de cliente',
                'module_key': 'pricing',
                'bg_color': '#E74C3C',
                'hover_color': '#C0392B',
                'requires_admin': True
            },
            {
                'title': 'Registro de Compras',
                'description': 'Registrar compras\ny gestionar inventario',
                'module_key': 'inventory',
                'bg_color': '#2ECC71',
                'hover_color': '#27AE60',
                'requires_admin': False
            },
            {
                'title': 'Análisis de Ganancias',
                'description': 'Ver reportes detallados\nde ganancias y pérdidas',
                'module_key': 'analytics',
                'bg_color': '#9B59B6',
                'hover_color': '#8E44AD',
                'requires_admin': False
            },
            {
                'title': 'Administrar Clientes',
                'description': 'Gestionar clientes\ny tipos de cliente',
                'module_key': 'clients',
                'bg_color': '#F39C12',
                'hover_color': '#E67E22',
                'requires_admin': True
            }
        ]
    
    def get_available_modules(self, user_role):
        """Get modules available for the given user role"""
        available_modules = []
        
        for module in self.modules:
            if module['requires_admin'] and user_role != 'admin':
                continue
            available_modules.append(module)
        
        debug_print(f"Available modules for role '{user_role}': {len(available_modules)}")
        return available_modules
    
    def launch_module(self, module_key, user_data=None):
        """Launch a module using the proper launcher"""
        debug_print(f"Launching module: {module_key}")
        
        try:
            # Update session activity if session manager is enabled
            if USE_SESSION_MANAGER:
                try:
                    from src.auth.session_manager import session_manager
                    session_manager.update_activity()
                except ImportError:
                    debug_print("Session manager not available")
            
            # Prepare user data as JSON string
            user_data_json = ""
            if user_data:
                import json
                user_data_json = json.dumps(user_data)
            
            # Use the module launcher script
            launcher_script = "launch_module.py"
            if not os.path.exists(launcher_script):
                messagebox.showerror("Error", f"No se encontró el launcher: {launcher_script}")
                return False
            
            # Prepare command
            cmd = [sys.executable, launcher_script, module_key]
            if user_data_json:
                cmd.append(user_data_json)
            
            # Launch module
            if sys.platform.startswith('win'):
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(cmd)
                
            debug_print(f"Module {module_key} launched successfully")
            return True
            
        except Exception as e:
            debug_print(f"Error launching module: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")
            return False
    
    def validate_module_launcher(self):
        """Validate that the module launcher exists"""
        launcher_script = "launch_module.py"
        if not os.path.exists(launcher_script):
            debug_print(f"Missing module launcher: {launcher_script}")
            return False, [launcher_script]
        
        debug_print("Module launcher validated successfully")
        return True, []
    
    def get_module_by_key(self, module_key):
        """Get module definition by module key"""
        for module in self.modules:
            if module['module_key'] == module_key:
                return module
        return None