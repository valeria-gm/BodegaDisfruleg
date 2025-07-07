#!/usr/bin/env python3
"""
Script para crear un nuevo usuario con rol 'trabajador' en DISFRULEG
"""

import bcrypt
import mysql.connector
from getpass import getpass

def hash_password(password):
    """Generar hash seguro de una contraseña"""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_worker_user():
    """Crear un nuevo usuario trabajador"""
    print("CREACIÓN DE NUEVO USUARIO TRABAJADOR")
    print("=" * 40)
    
    # Solicitar datos del nuevo usuario
    username = input("Ingrese nombre de usuario: ").strip()
    if not username:
        print("Error: El nombre de usuario es obligatorio")
        return False
    
    nombre_completo = input("Ingrese nombre completo: ").strip()
    if not nombre_completo:
        print("Error: El nombre completo es obligatorio")
        return False
    
    # Solicitar contraseña
    while True:
        password = getpass("Ingrese contraseña (mínimo 8 caracteres): ")
        if len(password) < 8:
            print("Error: La contraseña debe tener al menos 8 caracteres")
            continue
        
        password_confirm = getpass("Confirme la contraseña: ")
        if password != password_confirm:
            print("Error: Las contraseñas no coinciden")
            continue
        
        break
    
    # Solicitar credenciales administrativas para la conexión
    print("\nIngrese credenciales administrativas de MySQL:")
    admin_user = input("Usuario admin (jared/valeria): ")
    admin_pass = getpass("Contraseña admin: ")
    
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(
            host="localhost",
            user=admin_user,
            password=admin_pass,
            database="disfruleg"
        )
        
        cursor = conn.cursor()
        
        # Verificar que el usuario no existe
        cursor.execute("SELECT COUNT(*) FROM usuarios_sistema WHERE username = %s", (username,))
        if cursor.fetchone()[0] > 0:
            print(f"Error: Ya existe un usuario con el nombre '{username}'")
            conn.close()
            return False
        
        # Generar hash de la contraseña
        password_hash = hash_password(password)
        
        # Insertar nuevo usuario
        cursor.execute("""
            INSERT INTO usuarios_sistema (username, password_hash, nombre_completo, rol, activo) 
            VALUES (%s, %s, %s, %s, %s)
        """, (username, password_hash, nombre_completo, 'trabajador', True))
        
        conn.commit()
        
        print(f"\n✓ Usuario '{username}' creado exitosamente con rol 'trabajador'")
        print(f"  Nombre completo: {nombre_completo}")
        print(f"  Rol: trabajador")
        print(f"  Estado: activo")
        
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Función principal"""
    success = create_worker_user()
    
    if success:
        print("\n" + "=" * 40)
        print("USUARIO CREADO EXITOSAMENTE")
        print("=" * 40)
        print("\nEl nuevo usuario trabajador puede ahora:")
        print("- Iniciar sesión en el sistema")
        print("- Generar recibos y facturas")
        print("- Registrar compras")
        print("- Ver análisis de ganancias")
        print("- NO puede editar precios (requiere admin)")
        print("- NO puede administrar clientes (requiere admin)")
        print("- NO puede acceder a productos especiales (requiere admin)")
    else:
        print("\nError al crear el usuario. Intente nuevamente.")

if __name__ == "__main__":
    main()