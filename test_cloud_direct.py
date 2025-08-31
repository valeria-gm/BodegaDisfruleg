#!/usr/bin/env python3
"""
Script para probar conexión directa a Cloud SQL
"""

import mysql.connector
import os
from dotenv import load_dotenv

def test_cloud_sql_direct():
    """Probar conexión directa a Cloud SQL"""
    # Forzar recarga del .env
    load_dotenv(override=True)
    
    config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
        'auth_plugin': 'mysql_native_password',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    print("=== PRUEBA DIRECTA CLOUD SQL ===")
    print(f"Host: {config['host']}")
    print(f"Usuario: {config['user']}")
    print(f"Base de datos: {config['database']}")
    
    try:
        conn = mysql.connector.connect(**config)
        print("✓ Conexión exitosa a Cloud SQL")
        
        cursor = conn.cursor()
        cursor.execute('SELECT username, nombre_completo, rol FROM usuarios_sistema LIMIT 10')
        users = cursor.fetchall()
        
        print("\n--- Usuarios en Cloud SQL ---")
        if users:
            for user in users:
                print(f"- {user[0]} ({user[1]}) - Rol: {user[2]}")
        else:
            print("No hay usuarios en la tabla usuarios_sistema")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Error conectando a Cloud SQL: {e}")

if __name__ == "__main__":
    test_cloud_sql_direct()