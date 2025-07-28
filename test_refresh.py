#!/usr/bin/env python3
"""
Test script to verify the order refresh functionality
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    try:
        from launch_module import launch_receipts_module
        
        # Test data
        user_data = {
            'nombre_completo': 'Usuario de Prueba',
            'rol': 'admin', 
            'username': 'test'
        }
        
        print("🧪 Probando funcionalidad de actualización de órdenes")
        print("📋 Instrucciones de prueba:")
        print("1. Crear una nueva orden desde la ventana principal")
        print("2. Agregar algunos productos y guardar la orden")
        print("3. Volver a la ventana principal (botón 'Ver Órdenes')")  
        print("4. Verificar que la orden aparece inmediatamente en la lista")
        print("5. También probar editando una orden existente")
        print("")
        print("🔍 Funcionalidades implementadas:")
        print("   ✅ Auto-refresh al guardar orden")
        print("   ✅ Auto-refresh al cerrar ventana de edición") 
        print("   ✅ Auto-refresh al ganar foco la ventana principal")
        print("   ✅ Eventos personalizados entre ventanas")
        print("")
        
        # Launch the module
        launch_receipts_module(user_data)
        
    except Exception as e:
        print(f"❌ Error en prueba de refresh: {e}")
        import traceback
        traceback.print_exc()