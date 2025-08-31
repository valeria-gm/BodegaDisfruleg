#!/usr/bin/env python3
"""
Script para probar conexión a Cloud SQL y verificar usuarios
"""

from src.database.conexion import conectar

def test_connection():
    """Probar conexión y mostrar usuarios disponibles"""
    try:
        print("Probando conexión...")
        conn = conectar()
        
        if conn:
            print("✓ Conexión exitosa a la base de datos")
            
            cursor = conn.cursor()
            
            # Verificar qué usuarios hay en Cloud SQL
            print("\n--- Usuarios en la tabla usuarios_sistema ---")
            cursor.execute('SELECT username, nombre_completo, rol FROM usuarios_sistema LIMIT 10')
            users = cursor.fetchall()
            
            if users:
                for user in users:
                    print(f"- {user[0]} ({user[1]}) - Rol: {user[2]}")
            else:
                print("No hay usuarios en la tabla usuarios_sistema")
            
            conn.close()
            print("\n✓ Prueba completada")
            
        else:
            print("✗ Error de conexión")
            
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_connection()