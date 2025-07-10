#!/usr/bin/env python3
"""
Script de diagnóstico para identificar el problema
"""

import sys
import traceback

def test_tkinter_basic():
    """Test básico de Tkinter"""
    print("=== TEST 1: Tkinter Básico ===")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.title("Test")
        root.geometry("400x300")
        print("✓ Tkinter básico funciona")
        root.destroy()
        return True
    except Exception as e:
        print(f"✗ Error en Tkinter básico: {e}")
        traceback.print_exc()
        return False

def test_tkinter_geometry():
    """Test de geometría de Tkinter"""
    print("\n=== TEST 2: Geometría de Tkinter ===")
    try:
        import tkinter as tk
        root = tk.Tk()
        
        # Test diferentes configuraciones de geometría
        root.geometry("800x600")
        print("✓ Geometría básica funciona")
        
        root.geometry("800x600+100+100")
        print("✓ Geometría con posición funciona")
        
        # Test centrado
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        root.geometry(f"{width}x{height}+{x}+{y}")
        print("✓ Centrado funciona")
        
        root.destroy()
        return True
    except Exception as e:
        print(f"✗ Error en geometría: {e}")
        traceback.print_exc()
        return False

def test_login_window():
    """Test de la ventana de login"""
    print("\n=== TEST 3: Login Window ===")
    try:
        from login_window import LoginWindow
        print("✓ Importación de login_window exitosa")
        
        # No crear la ventana, solo probar la importación
        return True
    except Exception as e:
        print(f"✗ Error en login_window: {e}")
        traceback.print_exc()
        return False

def test_session_manager():
    """Test del session manager"""
    print("\n=== TEST 4: Session Manager ===")
    try:
        from session_manager import session_manager, SessionStatusBar
        print("✓ Importación de session_manager exitosa")
        return True
    except Exception as e:
        print(f"✗ Error en session_manager: {e}")
        traceback.print_exc()
        return False

def test_db_manager():
    """Test del database manager"""
    print("\n=== TEST 5: Database Manager ===")
    try:
        from db_manager import db_manager
        print("✓ Importación de db_manager exitosa")
        return True
    except Exception as e:
        print(f"✗ Error en db_manager: {e}")
        traceback.print_exc()
        return False

def test_pil():
    """Test de PIL/Pillow"""
    print("\n=== TEST 6: PIL/Pillow ===")
    try:
        from PIL import Image, ImageTk
        print("✓ PIL/Pillow funciona")
        return True
    except Exception as e:
        print(f"✗ Error en PIL: {e}")
        return False

def test_dependencies():
    """Test de dependencias"""
    print("\n=== TEST 7: Dependencias ===")
    
    dependencies = [
        ('bcrypt', 'bcrypt'),
        ('mysql.connector', 'mysql-connector-python'),
        ('PIL', 'Pillow')
    ]
    
    all_ok = True
    for module, package in dependencies:
        try:
            __import__(module)
            print(f"✓ {module} disponible")
        except ImportError:
            print(f"✗ {module} no disponible - instalar: pip install {package}")
            all_ok = False
    
    return all_ok

def test_show_login():
    """Test de show_login sin ejecutar"""
    print("\n=== TEST 8: Show Login Function ===")
    try:
        from login_window import show_login
        print("✓ Función show_login importada correctamente")
        return True
    except Exception as e:
        print(f"✗ Error importando show_login: {e}")
        traceback.print_exc()
        return False

def main():
    """Ejecutar todos los tests"""
    print("DIAGNÓSTICO DEL SISTEMA DISFRULEG")
    print("=" * 50)
    
    tests = [
        test_tkinter_basic,
        test_tkinter_geometry,
        test_dependencies,
        test_db_manager,
        test_session_manager,
        test_pil,
        test_login_window,
        test_show_login
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test falló completamente: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("RESUMEN:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests pasados: {passed}/{total}")
    
    if passed == total:
        print("✓ Todos los tests pasaron. El problema puede estar en la lógica específica.")
    else:
        print("✗ Algunos tests fallaron. Revisar los errores arriba.")
    
    print("\nRECOMENDACIONES:")
    
    if not results[0]:  # tkinter básico
        print("- Reinstalar Python o verificar instalación de Tkinter")
    
    if not results[1]:  # geometría
        print("- Problema con la configuración de geometría de ventanas")
        print("- Intentar usar la versión simplificada")
    
    if not results[2]:  # dependencias
        print("- Instalar dependencias faltantes")
    
    if not any(results[3:6]):  # módulos internos
        print("- Problema con los módulos del sistema")
        print("- Verificar que todos los archivos estén presentes")
    
    if not results[6] or not results[7]:  # login
        print("- Problema específico con el sistema de login")
        print("- Usar versión simplificada sin autenticación")

if __name__ == "__main__":
    main()