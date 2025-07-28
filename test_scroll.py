#!/usr/bin/env python3
"""
Test script to verify the scrolling functionality
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Test the scrolling interface
if __name__ == "__main__":
    try:
        from src.modules.receipts.receipt_generator_refactored import ReciboAppMejorado
        
        # Test data
        user_data = {
            'nombre_completo': 'Usuario de Prueba',
            'rol': 'admin', 
            'username': 'test'
        }
        
        # Create and run app
        app = ReciboAppMejorado(user_data=user_data)
        print("✅ Scrolling interface initialized successfully")
        print("🔍 Testing scrolling functionality...")
        print("📏 Try resizing the window to test auto-hide/show scrollbar")
        print("🖱️ Use mouse wheel to scroll when content exceeds window height")
        
        app.run()
        
    except Exception as e:
        print(f"❌ Error testing scroll functionality: {e}")
        import traceback
        traceback.print_exc()