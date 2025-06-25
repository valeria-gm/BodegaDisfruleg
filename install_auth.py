#!/usr/bin/env python3
"""
Script de instalación para el sistema de autenticación de DISFRULEG
Instala dependencias y configura la base de datos
"""

import subprocess
import sys
import mysql.connector
from getpass import getpass

def install_dependencies():
    """Instalar dependencias de Python"""
    print("Instalando dependencias de Python...")
    
    dependencies = [
        'bcrypt',
        'Pillow',  # Para PIL en login_window
    ]
    
    for dep in dependencies:
        try:
            print(f"Instalando {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✓ {dep} instalado correctamente")
        except subprocess.CalledProcessError:
            print(f"✗ Error instalando {dep}")
            return False
    
    print("✓ Todas las dependencias instaladas correctamente")
    return True

def setup_database():
    """Configurar base de datos"""
    print("\nConfigurando base de datos...")
    
    # Solicitar credenciales administrativas
    print("Ingrese las credenciales administrativas de MySQL:")
    admin_user = input("Usuario admin (ejemplo: jared): ")
    admin_pass = getpass("Contraseña admin: ")
    
    try:
        # Conectar con credenciales admin
        conn = mysql.connector.connect(
            host="localhost",
            user=admin_user,
            password=admin_pass,
            database="disfruleg"
        )
        
        cursor = conn.cursor()
        
        # Crear tabla usuarios_sistema
        print("Creando tabla usuarios_sistema...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios_sistema (
                id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                nombre_completo VARCHAR(100) NOT NULL,
                rol ENUM('admin', 'usuario') DEFAULT 'usuario',
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_acceso TIMESTAMP NULL,
                intentos_fallidos INT DEFAULT 0,
                bloqueado_hasta TIMESTAMP NULL
            )
        """)
        
        # Crear índices
        print("Creando índices...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_username ON usuarios_sistema(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activo ON usuarios_sistema(activo)")
        
        # Crear tabla log_accesos
        print("Creando tabla log_accesos...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS log_accesos (
                id_log INT AUTO_INCREMENT PRIMARY KEY,
                id_usuario INT NULL,
                username_intento VARCHAR(50),
                ip_address VARCHAR(45) DEFAULT 'localhost',
                exito BOOLEAN,
                fecha_intento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                detalle VARCHAR(255),
                FOREIGN KEY (id_usuario) REFERENCES usuarios_sistema(id_usuario) ON DELETE SET NULL
            )
        """)
        
        conn.commit()
        print("✓ Tablas creadas correctamente")
        
        # Generar hashes de contraseñas
        print("\nGenerando hashes de contraseñas...")
        import bcrypt
        
        # Hash para jared
        jared_pass = "zoibnG31!!EAEA"
        jared_hash = bcrypt.hashpw(jared_pass.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        
        # Hash para valeria
        valeria_pass = "proYect0.593"
        valeria_hash = bcrypt.hashpw(valeria_pass.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        
        # Insertar usuarios (usando ON DUPLICATE KEY UPDATE para evitar errores)
        print("Insertando usuarios del sistema...")
        cursor.execute("""
            INSERT INTO usuarios_sistema (username, password_hash, nombre_completo, rol) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            password_hash = VALUES(password_hash),
            nombre_completo = VALUES(nombre_completo),
            rol = VALUES(rol)
        """, ('jared', jared_hash, 'Jared (Administrador)', 'admin'))
        
        cursor.execute("""
            INSERT INTO usuarios_sistema (username, password_hash, nombre_completo, rol) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            password_hash = VALUES(password_hash),
            nombre_completo = VALUES(nombre_completo),
            rol = VALUES(rol)
        """, ('valeria', valeria_hash, 'Valeria (Administrador)', 'admin'))
        
        conn.commit()
        print("✓ Usuarios insertados correctamente")
        
        # Verificar instalación
        cursor.execute("SELECT COUNT(*) FROM usuarios_sistema")
        user_count = cursor.fetchone()[0]
        print(f"✓ {user_count} usuarios configurados en el sistema")
        
        conn.close()
        print("✓ Base de datos configurada correctamente")
        return True
        
    except mysql.connector.Error as e:
        print(f"✗ Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def backup_old_files():
    """Hacer backup de archivos existentes"""
    import os
    import shutil
    from datetime import datetime
    
    print("\nCreando backup de archivos existentes...")
    
    files_to_backup = [
        'menu_principal.py',
        'conexion.py'
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_{timestamp}"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    for file in files_to_backup:
        if os.path.exists(file):
            backup_path = os.path.join(backup_dir, file)
            shutil.copy2(file, backup_path)
            print(f"✓ Backup creado: {backup_path}")
    
    print(f"✓ Backup completado en directorio: {backup_dir}")

def test_authentication():
    """Probar el sistema de autenticación"""
    print("\nProbando sistema de autenticación...")
    
    try:
        from auth_manager import AuthManager
        
        auth = AuthManager()
        
        # Probar autenticación con jared
        result = auth.authenticate('jared', 'zoibnG31!!EAEA')
        if result['success']:
            print("✓ Autenticación de jared: EXITOSA")
        else:
            print(f"✗ Autenticación de jared: FALLÓ - {result['message']}")
            return False
        
        # Probar autenticación con valeria
        result = auth.authenticate('valeria', 'proYect0.593')
        if result['success']:
            print("✓ Autenticación de valeria: EXITOSA")
        else:
            print(f"✗ Autenticación de valeria: FALLÓ - {result['message']}")
            return False
        
        # Probar autenticación fallida
        result = auth.authenticate('usuario_falso', 'password_falso')
        if not result['success']:
            print("✓ Autenticación fallida manejada correctamente")
        else:
            print("✗ Error: autenticación fallida no detectada")
            return False
        
        print("✓ Sistema de autenticación funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"✗ Error probando autenticación: {e}")
        return False

def main():
    """Función principal de instalación"""
    print("="*60)
    print("INSTALADOR DEL SISTEMA DE AUTENTICACIÓN DISFRULEG")
    print("="*60)
    
    # Paso 1: Instalar dependencias
    if not install_dependencies():
        print("\n✗ Error instalando dependencias. Abortando...")
        return False
    
    # Paso 2: Backup de archivos existentes
    backup_old_files()
    
    # Paso 3: Configurar base de datos
    if not setup_database():
        print("\n✗ Error configurando base de datos. Abortando...")
        return False
    
    # Paso 4: Probar autenticación
    if not test_authentication():
        print("\n✗ Error en pruebas de autenticación. Abortando...")
        return False
    
    # Finalización exitosa
    print("\n" + "="*60)
    print("✓ INSTALACIÓN COMPLETADA EXITOSAMENTE")
    print("="*60)
    print("\nEl sistema de autenticación está listo para usar.")
    print("\nPROCEDIMIENTO PARA USAR EL NUEVO SISTEMA:")
    print("1. Ejecute 'python new_main.py' en lugar de 'python menu_principal.py'")
    print("2. Use las credenciales existentes:")
    print("   - Usuario: jared / Contraseña: zoibnG31!!EAEA")
    print("   - Usuario: valeria / Contraseña: proYect0.593")
    print("3. El sistema solicitará login antes de mostrar el menú principal")
    print("\nNOTAS IMPORTANTES:")
    print("- Los archivos originales fueron respaldados")
    print("- El sistema ahora requiere autenticación obligatoria")
    print("- Se agregó control de sesiones con timeout automático")
    print("- Se implementó logging de accesos y seguridad mejorada")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstalación cancelada por el usuario.")
    except Exception as e:
        print(f"\n\nError durante la instalación: {e}")
        print("Contacte al desarrollador para soporte.")