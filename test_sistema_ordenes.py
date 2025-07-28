#!/usr/bin/env python3
"""
test_sistema_ordenes.py
Comprehensive Integration Test Suite for the Saved Orders System

This script tests all aspects of the saved orders system including:
- Database operations (insert, update, mark registered, soft delete)
- Folio management (sequence, gaps, reserve, release, reuse)
- Permissions (user vs admin views)
- Serialization/Deserialization (cart with sections, data integrity)
- Full order lifecycle flows

Author: System Integration Test Suite
Date: 2025
"""

import sys
import os
import unittest
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import system modules
try:
    from src.modules.receipts.components.orden_manager import obtener_manager, OrdenManager
    from src.modules.receipts.components.carrito_module import CarritoConSecciones, ItemCarrito, SeccionCarrito
    from src.modules.receipts.components import database
    import tkinter as tk
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Some imports not available: {e}")
    IMPORTS_AVAILABLE = False


class TestSistemaOrdenes(unittest.TestCase):
    """
    Comprehensive test suite for the saved orders system
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        if not IMPORTS_AVAILABLE:
            cls.skipTest(None, "Required imports not available")
        
        print("\n" + "="*70)
        print("🚀 INICIANDO SUITE DE PRUEBAS DEL SISTEMA DE ÓRDENES")
        print("="*70)
        
        # Test data
        cls.test_users = {
            'regular_user': {
                'username': 'test_user',
                'nombre_completo': 'Usuario Regular de Prueba',
                'rol': 'user'
            },
            'admin_user': {
                'username': 'test_admin',
                'nombre_completo': 'Admin de Prueba',
                'rol': 'admin'
            }
        }
        
        cls.test_client_id = 1  # Assuming test client exists
        cls.created_folios = []  # Track created folios for cleanup
        
        # Get manager instance
        cls.manager = obtener_manager()
        
        print(f"✅ Configuración inicial completada")
        print(f"📋 Manager obtenido: {type(cls.manager).__name__}")
    
    def setUp(self):
        """Set up each individual test"""
        self.start_time = time.time()
        print(f"\n🔍 Ejecutando: {self._testMethodName}")
    
    def tearDown(self):
        """Clean up after each test"""
        duration = time.time() - self.start_time
        print(f"   ⏱️ Completado en {duration:.3f}s")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if not IMPORTS_AVAILABLE:
            return
            
        print(f"\n🧹 Limpiando folios de prueba creados: {cls.created_folios}")
        
        # Clean up any test folios created
        for folio in cls.created_folios:
            try:
                cls.manager.liberar_folio(folio)
            except Exception as e:
                print(f"⚠️ Error limpiando folio {folio}: {e}")
        
        print("✅ Limpieza completada")
        print("="*70)
        print("🏁 SUITE DE PRUEBAS COMPLETADA")
        print("="*70)


class TestDatabaseOperations(TestSistemaOrdenes):
    """Test database operations for saved orders"""
    
    def test_01_insert_saved_order(self):
        """Test inserting a new saved order into database"""
        print("   📝 Probando inserción de orden guardada...")
        
        # Get next available folio
        folio = self.manager.obtener_siguiente_folio_disponible()
        self.assertIsNotNone(folio, "Should get a valid folio")
        self.__class__.created_folios.append(folio)
        
        # Create test cart data
        test_cart_data = {
            'sectioning_enabled': True,
            'secciones': {
                'sec1': {'id': 'sec1', 'nombre': 'Verduras'}
            },
            'items': {
                'item1': {
                    'nombre_producto': 'Tomate',
                    'cantidad': 2.5,
                    'precio_unitario': 15.0,
                    'unidad_producto': 'kg',
                    'seccion_id': 'sec1',
                    'subtotal': 37.5
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Reserve folio (insert order)
        result = self.manager.reservar_folio(
            folio=folio,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito=test_cart_data,
            total=37.5
        )
        
        self.assertTrue(result, "Should successfully insert saved order")
        print(f"   ✅ Orden insertada con folio {folio}")
    
    def test_02_unique_folio_constraint(self):
        """Test that database enforces unique folio constraint"""
        print("   🔒 Probando restricción de folio único...")
        
        # Get a folio and reserve it
        folio = self.manager.obtener_siguiente_folio_disponible()
        self.assertIsNotNone(folio)
        self.__class__.created_folios.append(folio)
        
        test_data = {'test': 'data'}
        
        # First reservation should succeed
        result1 = self.manager.reservar_folio(
            folio=folio,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito=test_data,
            total=100.0
        )
        self.assertTrue(result1, "First reservation should succeed")
        
        # Second reservation with same folio should fail
        result2 = self.manager.reservar_folio(
            folio=folio,
            id_cliente=self.test_client_id,
            usuario=self.test_users['admin_user']['username'],
            datos_carrito=test_data,
            total=200.0
        )
        self.assertFalse(result2, "Second reservation should fail due to unique constraint")
        print(f"   ✅ Restricción de folio único funcionando correctamente")
    
    def test_03_update_existing_order(self):
        """Test updating an existing order in database"""
        print("   📝 Probando actualización de orden existente...")
        
        # Create initial order
        folio = self.manager.obtener_siguiente_folio_disponible()
        self.assertIsNotNone(folio)
        self.__class__.created_folios.append(folio)
        
        initial_data = {
            'items': {'item1': {'nombre_producto': 'Producto Original', 'cantidad': 1}},
            'timestamp': datetime.now().isoformat()
        }
        
        # Insert initial order
        insert_result = self.manager.reservar_folio(
            folio=folio,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito=initial_data,
            total=50.0
        )
        self.assertTrue(insert_result, "Initial order should be created")
        
        # Update order with new data
        updated_data = {
            'items': {
                'item1': {'nombre_producto': 'Producto Actualizado', 'cantidad': 3},
                'item2': {'nombre_producto': 'Producto Nuevo', 'cantidad': 2}
            },
            'timestamp': datetime.now().isoformat()
        }
        
        update_result = self.manager.actualizar_orden(
            folio=folio,
            datos_carrito=updated_data,
            total=150.0
        )
        self.assertTrue(update_result, "Order should be updated successfully")
        
        # Verify update by loading order
        loaded_order = self.manager.cargar_orden(folio)
        self.assertIsNotNone(loaded_order, "Should load updated order")
        self.assertEqual(loaded_order['total_estimado'], 150.0, "Total should be updated")
        print(f"   ✅ Orden {folio} actualizada correctamente")
    
    def test_04_mark_as_registered(self):
        """Test marking an order as registered"""
        print("   ✅ Probando marcado como registrada...")
        
        # Create order
        folio = self.manager.obtener_siguiente_folio_disponible()
        self.assertIsNotNone(folio)
        self.__class__.created_folios.append(folio)
        
        test_data = {'test': 'registration_data'}
        
        # Insert order
        self.manager.reservar_folio(
            folio=folio,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito=test_data,
            total=75.0
        )
        
        # Mark as registered
        result = self.manager.marcar_como_registrada(folio)
        self.assertTrue(result, "Should successfully mark order as registered")
        
        # Verify status change by checking it appears in history
        historial = self.manager.obtener_historial(
            self.test_users['regular_user']['username'], 
            es_admin=False,
            limite=10
        )
        
        # Find our order in history
        found_in_history = any(orden['folio_numero'] == folio for orden in historial)
        self.assertTrue(found_in_history, "Registered order should appear in history")
        print(f"   ✅ Orden {folio} marcada como registrada")
    
    def test_05_soft_delete(self):
        """Test soft delete functionality"""
        print("   🗑️ Probando eliminación suave...")
        
        # Create order
        folio = self.manager.obtener_siguiente_folio_disponible()
        self.assertIsNotNone(folio)
        self.__class__.created_folios.append(folio)
        
        test_data = {'test': 'soft_delete_data'}
        
        # Insert order
        self.manager.reservar_folio(
            folio=folio,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito=test_data,
            total=25.0
        )
        
        # Verify order exists in active orders
        ordenes_activas_antes = self.manager.obtener_ordenes_activas(
            self.test_users['regular_user']['username'], 
            es_admin=False
        )
        found_before = any(orden['folio_numero'] == folio for orden in ordenes_activas_antes)
        self.assertTrue(found_before, "Order should exist before soft delete")
        
        # Perform soft delete
        result = self.manager.liberar_folio(folio)
        self.assertTrue(result, "Soft delete should succeed")
        
        # Verify order no longer appears in active orders
        ordenes_activas_despues = self.manager.obtener_ordenes_activas(
            self.test_users['regular_user']['username'], 
            es_admin=False
        )
        found_after = any(orden['folio_numero'] == folio for orden in ordenes_activas_despues)
        self.assertFalse(found_after, "Order should not appear after soft delete")
        print(f"   ✅ Orden {folio} eliminada suavemente (activo=FALSE)")


class TestFolioManagement(TestSistemaOrdenes):
    """Test folio management functionality"""
    
    def test_06_get_next_folio_normal_sequence(self):
        """Test getting next folio in normal sequence"""
        print("   📊 Probando secuencia normal de folios...")
        
        # Get current next folio
        folio1 = self.manager.obtener_siguiente_folio_disponible()
        self.assertIsNotNone(folio1, "Should get first folio")
        
        # Reserve it
        self.manager.reservar_folio(
            folio=folio1,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito={'test': 'sequence1'},
            total=10.0
        )
        self.__class__.created_folios.append(folio1)
        
        # Get next folio - should be sequential
        folio2 = self.manager.obtener_siguiente_folio_disponible()
        self.assertIsNotNone(folio2, "Should get second folio")
        self.assertEqual(folio2, folio1 + 1, "Second folio should be sequential")
        
        # Reserve second folio
        self.manager.reservar_folio(
            folio=folio2,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito={'test': 'sequence2'},
            total=20.0
        )
        self.__class__.created_folios.append(folio2)
        
        print(f"   ✅ Secuencia normal: {folio1} → {folio2}")
    
    def test_07_get_next_folio_with_gaps(self):
        """Test getting next folio when there are gaps in sequence"""
        print("   🕳️ Probando detección de gaps en folios...")
        
        # Create a gap by reserving non-consecutive folios
        folio1 = self.manager.obtener_siguiente_folio_disponible()
        self.assertIsNotNone(folio1)
        
        # Reserve folio1
        self.manager.reservar_folio(
            folio=folio1,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito={'test': 'gap_test1'},
            total=30.0
        )
        self.__class__.created_folios.append(folio1)
        
        # Skip folio1+1 and reserve folio1+2 (creating a gap)
        gap_folio = folio1 + 2
        
        # We need to simulate this gap by directly reserving the higher folio
        # This might not work with the current implementation, so let's test gap filling
        
        # Instead, let's create a gap by soft-deleting a folio
        folio2 = self.manager.obtener_siguiente_folio_disponible()
        self.manager.reservar_folio(
            folio=folio2,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito={'test': 'gap_test2'},
            total=40.0
        )
        self.__class__.created_folios.append(folio2)
        
        # Create third folio
        folio3 = self.manager.obtener_siguiente_folio_disponible()
        self.manager.reservar_folio(
            folio=folio3,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito={'test': 'gap_test3'},
            total=50.0
        )
        self.__class__.created_folios.append(folio3)
        
        # Now delete folio2 to create a gap
        self.manager.liberar_folio(folio2)
        
        # Next folio should fill the gap (should be folio2 again)
        next_folio = self.manager.obtener_siguiente_folio_disponible()
        self.assertEqual(next_folio, folio2, f"Should fill gap at {folio2}, got {next_folio}")
        
        print(f"   ✅ Gap detectado y rellenado: {folio1}, [GAP: {folio2}], {folio3} → siguiente: {next_folio}")
    
    def test_08_reserve_and_release_folio(self):
        """Test reserving and releasing folios"""
        print("   🔄 Probando reserva y liberación de folios...")
        
        # Get and reserve folio
        folio = self.manager.obtener_siguiente_folio_disponible()
        self.assertIsNotNone(folio)
        
        reserve_result = self.manager.reservar_folio(
            folio=folio,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito={'test': 'reserve_release'},
            total=60.0
        )
        self.assertTrue(reserve_result, "Should successfully reserve folio")
        self.__class__.created_folios.append(folio)
        
        # Verify folio is not available for reservation again
        duplicate_reserve = self.manager.reservar_folio(
            folio=folio,
            id_cliente=self.test_client_id,
            usuario=self.test_users['admin_user']['username'],
            datos_carrito={'test': 'duplicate'},
            total=70.0
        )
        self.assertFalse(duplicate_reserve, "Should not allow duplicate reservation")
        
        # Release folio
        release_result = self.manager.liberar_folio(folio)
        self.assertTrue(release_result, "Should successfully release folio")
        
        print(f"   ✅ Folio {folio} reservado y liberado correctamente")
    
    def test_09_reuse_released_folios(self):
        """Test that released folios are reused"""
        print("   ♻️ Probando reutilización de folios liberados...")
        
        # Reserve a folio
        folio1 = self.manager.obtener_siguiente_folio_disponible()
        self.manager.reservar_folio(
            folio=folio1,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito={'test': 'reuse1'},
            total=80.0
        )
        self.__class__.created_folios.append(folio1)
        
        # Get next folio
        folio2 = self.manager.obtener_siguiente_folio_disponible()
        self.manager.reservar_folio(
            folio=folio2,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito={'test': 'reuse2'},
            total=90.0
        )
        self.__class__.created_folios.append(folio2)
        
        # Release first folio
        self.manager.liberar_folio(folio1)
        
        # Next available folio should be the released one (folio1)
        next_folio = self.manager.obtener_siguiente_folio_disponible()
        self.assertEqual(next_folio, folio1, f"Should reuse released folio {folio1}, got {next_folio}")
        
        print(f"   ✅ Folio liberado {folio1} reutilizado correctamente")


class TestPermissions(TestSistemaOrdenes):
    """Test permission-based functionality"""
    
    def test_10_normal_user_views_own_orders(self):
        """Test that normal user sees only their own orders"""
        print("   👤 Probando vista de usuario normal (solo sus órdenes)...")
        
        regular_user = self.test_users['regular_user']['username']
        admin_user = self.test_users['admin_user']['username']
        
        # Create order for regular user
        folio1 = self.manager.obtener_siguiente_folio_disponible()
        self.manager.reservar_folio(
            folio=folio1,
            id_cliente=self.test_client_id,
            usuario=regular_user,
            datos_carrito={'test': 'user_order'},
            total=100.0
        )
        self.__class__.created_folios.append(folio1)
        
        # Create order for admin user
        folio2 = self.manager.obtener_siguiente_folio_disponible()
        self.manager.reservar_folio(
            folio=folio2,
            id_cliente=self.test_client_id,
            usuario=admin_user,
            datos_carrito={'test': 'admin_order'},
            total=200.0
        )
        self.__class__.created_folios.append(folio2)
        
        # Regular user should see only their order
        user_orders = self.manager.obtener_ordenes_activas(regular_user, es_admin=False)
        user_folios = [orden['folio_numero'] for orden in user_orders]
        
        self.assertIn(folio1, user_folios, "User should see their own order")
        self.assertNotIn(folio2, user_folios, "User should NOT see admin's order")
        
        print(f"   ✅ Usuario normal ve solo su orden: {folio1} (no ve {folio2})")
    
    def test_11_admin_views_all_orders(self):
        """Test that admin user sees all orders"""
        print("   👑 Probando vista de administrador (todas las órdenes)...")
        
        regular_user = self.test_users['regular_user']['username']
        admin_user = self.test_users['admin_user']['username']
        
        # Create order for regular user
        folio1 = self.manager.obtener_siguiente_folio_disponible()
        self.manager.reservar_folio(
            folio=folio1,
            id_cliente=self.test_client_id,
            usuario=regular_user,
            datos_carrito={'test': 'user_order_for_admin'},
            total=150.0
        )
        self.__class__.created_folios.append(folio1)
        
        # Create order for admin user
        folio2 = self.manager.obtener_siguiente_folio_disponible()
        self.manager.reservar_folio(
            folio=folio2,
            id_cliente=self.test_client_id,
            usuario=admin_user,
            datos_carrito={'test': 'admin_own_order'},
            total=250.0
        )
        self.__class__.created_folios.append(folio2)
        
        # Admin should see all orders
        admin_orders = self.manager.obtener_ordenes_activas(admin_user, es_admin=True)
        admin_folios = [orden['folio_numero'] for orden in admin_orders]
        
        # Filter for our test folios
        test_folios_found = [f for f in admin_folios if f in [folio1, folio2]]
        
        self.assertIn(folio1, test_folios_found, "Admin should see user's order")
        self.assertIn(folio2, test_folios_found, "Admin should see their own order")
        
        print(f"   ✅ Administrador ve todas las órdenes: {test_folios_found}")


class TestSerialization(TestSistemaOrdenes):
    """Test cart serialization and deserialization"""
    
    def setUp(self):
        """Set up GUI context for cart tests"""
        super().setUp()
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide window
        except Exception as e:
            self.skipTest(f"Cannot create Tkinter root: {e}")
    
    def tearDown(self):
        """Clean up GUI context"""
        if hasattr(self, 'root'):
            try:
                self.root.destroy()
            except:
                pass
        super().tearDown()
    
    def test_12_serialize_cart_with_sections(self):
        """Test serialization of complex cart with sections"""
        print("   📦 Probando serialización de carrito con secciones...")
        
        # Create cart with sections
        frame = tk.Frame(self.root)
        carrito = CarritoConSecciones(frame)
        
        # Enable sectioning
        carrito.sectioning_enabled = True
        carrito.sectioning_var.set(True)
        
        # Add sections
        seccion1 = SeccionCarrito('frutas', 'Frutas')
        seccion2 = SeccionCarrito('verduras', 'Verduras')
        carrito.secciones['frutas'] = seccion1
        carrito.secciones['verduras'] = seccion2
        
        # Add items to sections
        item1 = ItemCarrito('Manzana', 2.0, 12.0, 'kg', 'frutas')
        item2 = ItemCarrito('Lechuga', 1.5, 8.0, 'pz', 'verduras')
        item3 = ItemCarrito('Naranja', 3.0, 10.0, 'kg', 'frutas')
        
        carrito.items['item1'] = item1
        carrito.items['item2'] = item2
        carrito.items['item3'] = item3
        
        # Serialize cart
        serialized_data = OrdenManager.carrito_a_json(carrito)
        
        # Verify serialization
        self.assertIsInstance(serialized_data, dict, "Should return dictionary")
        self.assertTrue(serialized_data.get('sectioning_enabled'), "Should preserve sectioning state")
        self.assertIn('secciones', serialized_data, "Should include sections")
        self.assertIn('items', serialized_data, "Should include items")
        self.assertIn('timestamp', serialized_data, "Should include timestamp")
        
        # Verify sections
        self.assertEqual(len(serialized_data['secciones']), 2, "Should have 2 sections")
        self.assertIn('frutas', serialized_data['secciones'], "Should include frutas section")
        self.assertIn('verduras', serialized_data['secciones'], "Should include verduras section")
        
        # Verify items
        self.assertEqual(len(serialized_data['items']), 3, "Should have 3 items")
        
        print(f"   ✅ Carrito serializado: {len(serialized_data['secciones'])} secciones, {len(serialized_data['items'])} items")
    
    def test_13_deserialize_and_verify_integrity(self):
        """Test deserialization and data integrity"""
        print("   📥 Probando deserialización e integridad de datos...")
        
        # Create original cart
        frame1 = tk.Frame(self.root)
        original_cart = CarritoConSecciones(frame1)
        
        # Set up original cart with complex data
        original_cart.sectioning_enabled = True
        original_cart.sectioning_var.set(True)
        
        # Add sections
        sec1 = SeccionCarrito('lacteos', 'Lácteos')
        sec2 = SeccionCarrito('carnes', 'Carnes')
        original_cart.secciones['lacteos'] = sec1
        original_cart.secciones['carnes'] = sec2
        
        # Add items with special characters and edge cases
        item1 = ItemCarrito('Leche "Entera"', 2.5, 25.50, 'L', 'lacteos')
        item2 = ItemCarrito('Carne de Res & Cerdo', 1.0, 85.75, 'kg', 'carnes')
        item3 = ItemCarrito('Queso Añejo (Especial)', 0.5, 120.00, 'kg', 'lacteos')
        
        original_cart.items['milk'] = item1
        original_cart.items['meat'] = item2
        original_cart.items['cheese'] = item3
        
        # Calculate original total
        original_total = original_cart.obtener_total()
        
        # Serialize
        serialized_data = OrdenManager.carrito_a_json(original_cart)
        
        # Create new cart for deserialization
        frame2 = tk.Frame(self.root)
        restored_cart = CarritoConSecciones(frame2)
        
        # Deserialize
        result = OrdenManager.json_a_carrito(serialized_data, restored_cart)
        self.assertTrue(result, "Deserialization should succeed")
        
        # Verify integrity
        self.assertEqual(restored_cart.sectioning_enabled, original_cart.sectioning_enabled, 
                        "Sectioning state should be preserved")
        self.assertEqual(len(restored_cart.secciones), len(original_cart.secciones), 
                        "Number of sections should match")
        self.assertEqual(len(restored_cart.items), len(original_cart.items), 
                        "Number of items should match")
        
        # Verify total calculation
        restored_total = restored_cart.obtener_total()
        self.assertAlmostEqual(restored_total, original_total, places=2, 
                              msg="Total should be preserved after deserialization")
        
        # Verify specific item data
        restored_milk = restored_cart.items.get('milk')
        self.assertIsNotNone(restored_milk, "Milk item should be restored")
        self.assertEqual(restored_milk.nombre_producto, 'Leche "Entera"', 
                        "Item name with quotes should be preserved")
        self.assertEqual(restored_milk.precio_unitario, 25.50, 
                        "Item price should be preserved")
        
        print(f"   ✅ Integridad verificada: Total original={original_total:.2f}, Restaurado={restored_total:.2f}")
    
    def test_14_handle_complex_carts(self):
        """Test handling of particularly complex cart structures"""
        print("   🎯 Probando carritos complejos...")
        
        frame = tk.Frame(self.root)
        complex_cart = CarritoConSecciones(frame)
        
        # Create complex scenario
        complex_cart.sectioning_enabled = True
        complex_cart.sectioning_var.set(True)
        
        # Add many sections
        sections_data = [
            ('bebidas', 'Bebidas & Refrescos'),
            ('snacks', 'Snacks/Botanas'),
            ('higiene', 'Higiene Personal'),
            ('limpieza', 'Productos de Limpieza'),
            ('especiales', 'Productos Especiales')
        ]
        
        for sec_id, sec_name in sections_data:
            section = SeccionCarrito(sec_id, sec_name)
            complex_cart.secciones[sec_id] = section
        
        # Add many items with edge cases
        items_data = [
            ('Coca-Cola 2.5L', 3.0, 28.50, 'pz', 'bebidas'),
            ('Papas "Sabritas" Original', 5.0, 15.75, 'pz', 'snacks'),
            ('Shampoo Head & Shoulders', 1.0, 65.00, 'pz', 'higiene'),
            ('Cloro "Cloralex" 1L', 2.0, 22.30, 'pz', 'limpieza'),
            ('Producto Ñandú (Importado)', 0.25, 450.00, 'kg', 'especiales'),
            ('Refresco de Tamarindo', 6.0, 12.99, 'pz', 'bebidas'),
            ('Jabón para Trastes', 1.5, 18.50, 'pz', 'limpieza')
        ]
        
        for i, (name, qty, price, unit, section_id) in enumerate(items_data):
            item = ItemCarrito(name, qty, price, unit, section_id)
            complex_cart.items[f'item_{i}'] = item
        
        # Test serialization/deserialization cycle
        serialized = OrdenManager.carrito_a_json(complex_cart)
        
        # Verify serialization didn't fail
        self.assertIsInstance(serialized, dict, "Complex cart should serialize to dict")
        self.assertEqual(len(serialized['secciones']), 5, "Should preserve all sections")
        self.assertEqual(len(serialized['items']), 7, "Should preserve all items")
        
        # Test deserialization
        frame2 = tk.Frame(self.root)
        restored_cart = CarritoConSecciones(frame2)
        
        restore_result = OrdenManager.json_a_carrito(serialized, restored_cart)
        self.assertTrue(restore_result, "Complex cart should deserialize successfully")
        
        # Verify complex data preservation
        original_total = complex_cart.obtener_total()
        restored_total = restored_cart.obtener_total()
        self.assertAlmostEqual(original_total, restored_total, places=2, 
                              msg="Complex cart total should be preserved")
        
        print(f"   ✅ Carrito complejo: {len(serialized['secciones'])} secciones, {len(serialized['items'])} items, total={original_total:.2f}")


class TestFullFlows(TestSistemaOrdenes):
    """Test complete order lifecycle flows"""
    
    def test_15_complete_order_lifecycle(self):
        """Test Create → Save → Edit → Register Order flow"""
        print("   🔄 Probando ciclo completo de orden...")
        
        # Step 1: Create order (get folio)
        folio = self.manager.obtener_siguiente_folio_disponible()
        self.assertIsNotNone(folio, "Should get folio for new order")
        self.__class__.created_folios.append(folio)
        
        # Step 2: Save order
        initial_data = {
            'sectioning_enabled': False,
            'items': {
                'item1': {
                    'nombre_producto': 'Producto Inicial',
                    'cantidad': 2.0,
                    'precio_unitario': 50.00,
                    'unidad_producto': 'pz',
                    'seccion_id': None,
                    'subtotal': 100.00
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        save_result = self.manager.reservar_folio(
            folio=folio,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito=initial_data,
            total=100.00
        )
        self.assertTrue(save_result, "Should save order successfully")
        
        # Step 3: Edit order
        edited_data = {
            'sectioning_enabled': False,
            'items': {
                'item1': {
                    'nombre_producto': 'Producto Inicial',
                    'cantidad': 3.0,  # Changed quantity
                    'precio_unitario': 50.00,
                    'unidad_producto': 'pz',
                    'seccion_id': None,
                    'subtotal': 150.00
                },
                'item2': {  # Added new item
                    'nombre_producto': 'Producto Adicional',
                    'cantidad': 1.0,
                    'precio_unitario': 25.00,
                    'unidad_producto': 'pz',
                    'seccion_id': None,
                    'subtotal': 25.00
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        edit_result = self.manager.actualizar_orden(folio, edited_data, 175.00)
        self.assertTrue(edit_result, "Should edit order successfully")
        
        # Step 4: Verify edit by loading
        loaded_order = self.manager.cargar_orden(folio)
        self.assertIsNotNone(loaded_order, "Should load edited order")
        self.assertEqual(loaded_order['total_estimado'], 175.00, "Should reflect edited total")
        
        # Verify it appears in active orders
        active_orders = self.manager.obtener_ordenes_activas(
            self.test_users['regular_user']['username'], 
            es_admin=False
        )
        found_in_active = any(orden['folio_numero'] == folio for orden in active_orders)
        self.assertTrue(found_in_active, "Edited order should appear in active orders")
        
        # Step 5: Register order
        register_result = self.manager.marcar_como_registrada(folio)
        self.assertTrue(register_result, "Should register order successfully")
        
        # Step 6: Verify registration
        # Should no longer appear in active orders
        active_after_register = self.manager.obtener_ordenes_activas(
            self.test_users['regular_user']['username'], 
            es_admin=False
        )
        found_in_active_after = any(orden['folio_numero'] == folio for orden in active_after_register)
        self.assertFalse(found_in_active_after, "Registered order should not appear in active orders")
        
        # Should appear in history
        history = self.manager.obtener_historial(
            self.test_users['regular_user']['username'], 
            es_admin=False
        )
        found_in_history = any(orden['folio_numero'] == folio for orden in history)
        self.assertTrue(found_in_history, "Registered order should appear in history")
        
        print(f"   ✅ Ciclo completo exitoso para folio {folio}: Crear → Guardar → Editar → Registrar")
    
    def test_16_create_close_without_saving(self):
        """Test Create → Close Without Saving → Verify Folio Released"""
        print("   ❌ Probando creación y cierre sin guardar...")
        
        # Get next available folio (simulating user opening new order)
        folio = self.manager.obtener_siguiente_folio_disponible()
        initial_folio = folio
        self.assertIsNotNone(folio, "Should get folio for new order")
        
        # Simulate user closing without saving (folio should be available again)
        # In real scenario, the app would call liberar_folio or just not reserve it
        
        # Verify the same folio is still available
        folio_after_close = self.manager.obtener_siguiente_folio_disponible()
        self.assertEqual(folio_after_close, initial_folio, 
                        "Same folio should be available after closing without saving")
        
        # Now actually reserve it to test proper flow
        test_data = {'test': 'after_close_without_save'}
        reserve_result = self.manager.reservar_folio(
            folio=folio_after_close,
            id_cliente=self.test_client_id,
            usuario=self.test_users['regular_user']['username'],
            datos_carrito=test_data,
            total=99.99
        )
        self.assertTrue(reserve_result, "Should be able to reserve folio after close without save")
        self.__class__.created_folios.append(folio_after_close)
        
        # Verify folio is now unavailable
        next_folio = self.manager.obtener_siguiente_folio_disponible()
        self.assertNotEqual(next_folio, folio_after_close, 
                           "Next folio should be different after reservation")
        
        print(f"   ✅ Folio {initial_folio} disponible después de cerrar sin guardar, reservado correctamente")


class TestRunner:
    """Custom test runner with enhanced reporting"""
    
    @staticmethod
    def run_all_tests():
        """Run all test suites with comprehensive reporting"""
        if not IMPORTS_AVAILABLE:
            print("❌ No se pueden ejecutar las pruebas - Imports no disponibles")
            print("   Asegúrate de que tkinter esté disponible y que el proyecto esté configurado correctamente")
            return False
            
        print("\n" + "🧪 EJECUTANDO SUITE COMPLETA DE PRUEBAS DEL SISTEMA DE ÓRDENES" + "\n")
        
        # Test suites in order
        test_suites = [
            TestDatabaseOperations,
            TestFolioManagement, 
            TestPermissions,
            TestSerialization,
            TestFullFlows
        ]
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        for suite_class in test_suites:
            print(f"\n{'='*50}")
            print(f"📋 EJECUTANDO: {suite_class.__name__}")
            print(f"{'='*50}")
            
            # Create test suite
            suite = unittest.TestLoader().loadTestsFromTestCase(suite_class)
            
            # Run tests with custom result
            result = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w')).run(suite)
            
            # Count results
            suite_tests = result.testsRun
            suite_failures = len(result.failures)
            suite_errors = len(result.errors)
            suite_success = suite_tests - suite_failures - suite_errors
            
            total_tests += suite_tests
            total_failures += suite_failures
            total_errors += suite_errors
            
            # Report suite results
            print(f"\n📊 RESULTADOS {suite_class.__name__}:")
            print(f"   ✅ Exitosas: {suite_success}/{suite_tests}")
            if suite_failures > 0:
                print(f"   ❌ Fallas: {suite_failures}")
                for test, traceback in result.failures:
                    error_msg = traceback.split('AssertionError: ')[-1].split('\n')[0] if 'AssertionError:' in traceback else 'Error'
                    print(f"      • {test}: {error_msg}")
            if suite_errors > 0:
                print(f"   💥 Errores: {suite_errors}")
                for test, traceback in result.errors:
                    error_msg = traceback.split('Exception: ')[-1].split('\n')[0] if 'Exception:' in traceback else 'Error'
                    print(f"      • {test}: {error_msg}")
        
        # Final summary
        print(f"\n{'='*70}")
        print(f"🏁 RESUMEN FINAL DE PRUEBAS")
        print(f"{'='*70}")
        print(f"📊 Total de pruebas: {total_tests}")
        print(f"✅ Exitosas: {total_tests - total_failures - total_errors}")
        print(f"❌ Fallas: {total_failures}")
        print(f"💥 Errores: {total_errors}")
        
        success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
        print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        if total_failures == 0 and total_errors == 0:
            print(f"\n🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema de órdenes está funcionando correctamente.")
            return True
        else:
            print(f"\n⚠️ Se encontraron problemas. Revisa los fallos y errores arriba.")
            return False


if __name__ == "__main__":
    # Run comprehensive test suite
    success = TestRunner.run_all_tests()
    sys.exit(0 if success else 1)