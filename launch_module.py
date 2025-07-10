#!/usr/bin/env python3
"""
Module Launcher Script
Properly launches business modules with correct Python path and imports
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def launch_receipts_module(user_data=None):
    """Launch the receipts generator module"""
    try:
        # Change to project root directory
        os.chdir(project_root)
        
        # Import and run the module
        from src.modules.receipts.receipt_generator_refactored import ReciboAppMejorado
        
        # Create main window
        root = tk.Tk()
        
        # Default user data if none provided
        if user_data is None:
            user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test'
            }
        
        # Launch the application
        app = ReciboAppMejorado(root, user_data)
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el módulo de recibos: {str(e)}")
        print(f"Error launching receipts module: {e}")

def launch_pricing_module(user_data=None):
    """Launch the price editor module"""
    try:
        os.chdir(project_root)
        from src.modules.pricing.price_editor import PriceEditorApp
        
        root = tk.Tk()
        
        if user_data is None:
            user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test'
            }
        
        app = PriceEditorApp(root, user_data)
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el editor de precios: {str(e)}")
        print(f"Error launching pricing module: {e}")

def launch_inventory_module(user_data=None):
    """Launch the inventory/purchases module"""
    try:
        os.chdir(project_root)
        from src.modules.inventory.registro_compras import ComprasApp
        
        root = tk.Tk()
        
        if user_data is None:
            user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test'
            }
        
        app = ComprasApp(root, user_data)
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el registro de compras: {str(e)}")
        print(f"Error launching inventory module: {e}")

def launch_analytics_module(user_data=None):
    """Launch the analytics module"""
    try:
        os.chdir(project_root)
        from src.modules.analytics.analizador_ganancias import AnalisisGananciasApp
        
        root = tk.Tk()
        
        if user_data is None:
            user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test'
            }
        
        app = AnalisisGananciasApp(root, user_data)
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el analizador de ganancias: {str(e)}")
        print(f"Error launching analytics module: {e}")

def launch_clients_module(user_data=None):
    """Launch the client management module"""
    try:
        os.chdir(project_root)
        from src.modules.clients.client_manager import ClientManagerApp
        
        root = tk.Tk()
        
        if user_data is None:
            user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test'
            }
        
        app = ClientManagerApp(root)
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el administrador de clientes: {str(e)}")
        print(f"Error launching clients module: {e}")

def main():
    """Main entry point when script is run directly"""
    if len(sys.argv) < 2:
        print("Usage: python launch_module.py <module_name>")
        print("Available modules: receipts, pricing, inventory, analytics, clients")
        sys.exit(1)
    
    module_name = sys.argv[1].lower()
    
    # Get user data from command line if provided (as JSON string)
    user_data = None
    if len(sys.argv) > 2:
        import json
        try:
            user_data = json.loads(sys.argv[2])
        except:
            print("Warning: Invalid user data JSON, using default")
    
    # Launch the appropriate module
    if module_name == "receipts":
        launch_receipts_module(user_data)
    elif module_name == "pricing":
        launch_pricing_module(user_data)
    elif module_name == "inventory":
        launch_inventory_module(user_data)
    elif module_name == "analytics":
        launch_analytics_module(user_data)
    elif module_name == "clients":
        launch_clients_module(user_data)
    else:
        print(f"Unknown module: {module_name}")
        print("Available modules: receipts, pricing, inventory, analytics, clients")
        sys.exit(1)

if __name__ == "__main__":
    main()