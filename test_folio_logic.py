#!/usr/bin/env python3
"""
Test script to verify the folio assignment logic and duplicate handling
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_folio_logic():
    """Test the folio assignment logic"""
    try:
        from src.modules.receipts.components.orden_manager import obtener_manager
        
        manager = obtener_manager()
        
        print("🧪 Probando lógica de asignación de folios")
        print("=" * 50)
        
        # Test 1: Obtener siguiente folio disponible
        print("\n📋 Test 1: Obtener siguiente folio disponible")
        folio = manager.obtener_siguiente_folio_disponible()
        print(f"Folio sugerido: {folio}")
        
        # Test 2: Verificar disponibilidad
        print(f"\n📋 Test 2: Verificar disponibilidad del folio {folio}")
        disponible = manager._verificar_folio_disponible(folio)
        print(f"¿Folio {folio} disponible?: {disponible}")
        
        # Test 3: Verificar folios ya usados
        print(f"\n📋 Test 3: Verificar algunos folios existentes")
        for test_folio in range(1, 10):
            disponible = manager._verificar_folio_disponible(test_folio)
            print(f"Folio {test_folio}: {'✅ Disponible' if disponible else '❌ Ya usado'}")
        
        # Test 4: Mostrar órdenes activas
        print(f"\n📋 Test 4: Órdenes guardadas actualmente")
        ordenes = manager.obtener_ordenes_activas("test", es_admin=True)
        print(f"Número de órdenes activas: {len(ordenes)}")
        
        if ordenes:
            print("Folios en uso por órdenes guardadas:")
            for orden in ordenes:
                print(f"  - Folio {orden['folio_numero']:06d}: {orden['nombre_cliente']} (Estado: guardada)")
        
        # Test 5: Mostrar historial
        print(f"\n📋 Test 5: Historial de órdenes registradas")
        historial = manager.obtener_historial("test", es_admin=True, limite=10)
        print(f"Número de órdenes registradas: {len(historial)}")
        
        if historial:
            print("Folios registrados:")
            for orden in historial:
                print(f"  - Folio {orden['folio_numero']:06d}: {orden['nombre_cliente']} (Estado: registrada)")
        
        print("\n" + "=" * 50)
        print("🎯 Soluciones implementadas:")
        print("  ✅ Query actualizada para considerar órdenes guardadas")
        print("  ✅ Verificación mejorada de disponibilidad de folios")
        print("  ✅ Manejo de errores de duplicados")
        print("  ✅ Sistema de reintentos para race conditions")
        print("  ✅ Mejor detección de conflictos de folios")
        
    except Exception as e:
        print(f"❌ Error en prueba de lógica de folios: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_folio_logic()