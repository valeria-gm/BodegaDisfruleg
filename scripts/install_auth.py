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
        
        # Verificar si la tabla usuarios_sistema ya existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'disfruleg' 
            AND table_name = 'usuarios_sistema'
        """)
        tabla_existe = cursor.fetchone()[0] > 0
        
        if tabla_existe:
            print("✓ Tabla usuarios_sistema ya existe")
        else:
            # Crear tabla usuarios_sistema
            print("Creando tabla usuarios_sistema...")
            cursor.execute("""
                CREATE TABLE usuarios_sistema (
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
            print("✓ Tabla usuarios_sistema creada")
        
        # Verificar si la tabla log_accesos ya existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'disfruleg' 
            AND table_name = 'log_accesos'
        """)
        log_tabla_existe = cursor.fetchone()[0] > 0
        
        if log_tabla_existe:
            print("✓ Tabla log_accesos ya existe")
        else:
            # Crear tabla log_accesos
            print("Creando tabla log_accesos...")
            cursor.execute("""
                CREATE TABLE log_accesos (
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
            print("✓ Tabla log_accesos creada")
        
        # Crear índices solo si no existen
        print("Verificando índices...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.statistics 
            WHERE table_schema = 'disfruleg'
            AND table_name = 'usuarios_sistema'
            AND index_name = 'idx_username'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("CREATE INDEX idx_username ON usuarios_sistema(username)")
            print("✓ Índice idx_username creado")
        else:
            print("✓ Índice idx_username ya existe")

        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.statistics 
            WHERE table_schema = 'disfruleg'
            AND table_name = 'usuarios_sistema'
            AND index_name = 'idx_activo'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("CREATE INDEX idx_activo ON usuarios_sistema(activo)")
            print("✓ Índice idx_activo creado")
        else:
            print("✓ Índice idx_activo ya existe")
        
        conn.commit()
        print("✓ Estructura de base de datos verificada/actualizada")
        
        # Generar hashes de contraseñas
        print("\nGenerando hashes de contraseñas...")
        import bcrypt
        
        # Hash para jared
        jared_pass = "zoibnG31!!EAEA"
        jared_hash = bcrypt.hashpw(jared_pass.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        
        # Hash para valeria
        valeria_pass = "proYect0.593"
        valeria_hash = bcrypt.hashpw(valeria_pass.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        
        # Insertar/actualizar usuarios (usando ON DUPLICATE KEY UPDATE para evitar errores)
        print("Insertando/actualizando usuarios del sistema...")
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
        
        # Agregar usuario administrador genérico
        admin_pass = "admin123"
        admin_hash = bcrypt.hashpw(admin_pass.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        
        cursor.execute("""
            INSERT INTO usuarios_sistema (username, password_hash, nombre_completo, rol) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            password_hash = VALUES(password_hash),
            nombre_completo = VALUES(nombre_completo),
            rol = VALUES(rol)
        """, ('admin', admin_hash, 'Administrador Sistema', 'admin'))
        
        # Agregar usuario vendedor genérico
        vendedor_pass = "vend123"
        vendedor_hash = bcrypt.hashpw(vendedor_pass.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        
        cursor.execute("""
            INSERT INTO usuarios_sistema (username, password_hash, nombre_completo, rol) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            password_hash = VALUES(password_hash),
            nombre_completo = VALUES(nombre_completo),
            rol = VALUES(rol)
        """, ('vendedor1', vendedor_hash, 'Vendedor General', 'usuario'))
        
        conn.commit()
        print("✓ Usuarios insertados/actualizados correctamente")
        
        # Verificar instalación
        cursor.execute("SELECT COUNT(*) FROM usuarios_sistema")
        user_count = cursor.fetchone()[0]
        print(f"✓ {user_count} usuarios configurados en el sistema")
        
        # Mostrar usuarios configurados
        cursor.execute("SELECT username, nombre_completo, rol FROM usuarios_sistema ORDER BY rol DESC, username")
        usuarios = cursor.fetchall()
        print("\nUsuarios configurados:")
        for usuario in usuarios:
            print(f"  - {usuario[0]} ({usuario[1]}) - Rol: {usuario[2]}")
        
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
        'conexion.py',
        'main.py'
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_{timestamp}"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"✓ Directorio de backup creado: {backup_dir}")
    
    backup_creado = False
    for file in files_to_backup:
        if os.path.exists(file):
            backup_path = os.path.join(backup_dir, file)
            shutil.copy2(file, backup_path)
            print(f"✓ Backup creado: {backup_path}")
            backup_creado = True
    
    if backup_creado:
        print(f"✓ Backup completado en directorio: {backup_dir}")
    else:
        print("ⓘ No se encontraron archivos para respaldar")

def test_authentication():
    """Probar el sistema de autenticación"""
    print("\nProbando sistema de autenticación...")
    
    try:
        # Importar desde la estructura actualizada del proyecto
        import sys
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        from src.modules.receipts.components.database import validar_usuario
        
        # Probar autenticación con jared
        rol = validar_usuario('jared', 'zoibnG31!!EAEA')
        if rol:
            print(f"✓ Autenticación de jared: EXITOSA (Rol: {rol})")
        else:
            print("✗ Autenticación de jared: FALLÓ")
            return False
        
        # Probar autenticación con valeria
        rol = validar_usuario('valeria', 'proYect0.593')
        if rol:
            print(f"✓ Autenticación de valeria: EXITOSA (Rol: {rol})")
        else:
            print("✗ Autenticación de valeria: FALLÓ")
            return False
        
        # Probar autenticación con admin
        rol = validar_usuario('admin', 'admin123')
        if rol:
            print(f"✓ Autenticación de admin: EXITOSA (Rol: {rol})")
        else:
            print("✗ Autenticación de admin: FALLÓ")
            return False
        
        # Probar autenticación fallida
        rol = validar_usuario('usuario_falso', 'password_falso')
        if not rol:
            print("✓ Autenticación fallida manejada correctamente")
        else:
            print("✗ Error: autenticación fallida no detectada")
            return False
        
        print("✓ Sistema de autenticación funcionando correctamente")
        return True
        
    except ImportError as e:
        print(f"✗ Error importando módulos: {e}")
        print("Nota: Ejecute este script desde el directorio raíz del proyecto")
        return False
    except Exception as e:
        print(f"✗ Error probando autenticación: {e}")
        return False

def test_database_connection():
    """Probar conexión a la base de datos"""
    print("\nProbando conexión a la base de datos...")
    
    try:
        import sys
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        from src.modules.receipts.components.database import conectar
        
        conn = conectar()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            
            # Verificar tablas críticas
            tablas_criticas = [
                'usuarios_sistema', 'cliente', 'producto', 'grupo', 'tipo_cliente',
                'precio_por_grupo', 'factura', 'ordenes_guardadas', 'folio_sequence'
            ]
            
            tablas_existentes = []
            for tabla in tablas_criticas:
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'disfruleg' AND table_name = '{tabla}'
                """)
                if cursor.fetchone()[0] > 0:
                    tablas_existentes.append(tabla)
            
            print(f"✓ Conexión a base de datos exitosa")
            print(f"✓ Tablas encontradas: {len(tablas_existentes)}/{len(tablas_criticas)}")
            
            if len(tablas_existentes) == len(tablas_criticas):
                print("✓ Todas las tablas críticas están presentes")
            else:
                tablas_faltantes = set(tablas_criticas) - set(tablas_existentes)
                print(f"⚠ Tablas faltantes: {', '.join(tablas_faltantes)}")
            
            conn.close()
            return len(tablas_existentes) >= 7  # Al menos las tablas más importantes
        else:
            print("✗ No se pudo conectar a la base de datos")
            return False
            
    except Exception as e:
        print(f"✗ Error probando conexión: {e}")
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
    
    # Paso 3: Probar conexión a base de datos
    if not test_database_connection():
        print("\n⚠ La base de datos no está completamente configurada.")
        print("Asegúrese de haber ejecutado los scripts de instalación de BD primero:")
        print("1. disfruleg_schema_fixed.sql")
        print("2. usuarios_fixed.sql")
        print("3. inserts_updated.sql")
        print("4. disfruleg_triggers_fixed.sql")
        print("5. disfruleg_views_fixed.sql")
        
    # Paso 4: Configurar base de datos (usuarios de autenticación)
    if not setup_database():
        print("\n✗ Error configurando base de datos. Abortando...")
        return False
    
    # Paso 5: Probar autenticación
    if not test_authentication():
        print("\n✗ Error en pruebas de autenticación. Abortando...")
        return False
    
    # Finalización exitosa
    print("\n" + "="*60)
    print("✓ INSTALACIÓN COMPLETADA EXITOSAMENTE")
    print("="*60)
    print("\nEl sistema de autenticación está listo para usar.")
    print("\nCREDENCIALES CONFIGURADAS:")
    print("1. Usuario: jared / Contraseña: zoibnG31!!EAEA (Admin)")
    print("2. Usuario: valeria / Contraseña: proYect0.593 (Admin)")
    print("3. Usuario: admin / Contraseña: admin123 (Admin)")
    print("4. Usuario: vendedor1 / Contraseña: vend123 (Usuario)")
    print("\nPROCEDIMIENTO PARA USAR EL SISTEMA:")
    print("1. Ejecute 'python main.py' para iniciar la aplicación")
    print("2. El sistema solicitará credenciales de login")
    print("3. Use cualquiera de las credenciales mostradas arriba")
    print("4. El sistema cargará con los permisos correspondientes al rol")
    print("\nARCHITECTURA DEL SISTEMA:")
    print("- Base de datos: disfruleg (MySQL)")
    print("- Autenticación: bcrypt con hashing seguro")
    print("- Gestión de sesiones: Timeout automático")
    print("- Logging: Registro completo de accesos")
    print("- Roles: admin (acceso completo) / usuario (acceso limitado)")
    print("\nNOTAS IMPORTANTES:")
    print("- Los archivos originales fueron respaldados automáticamente")
    print("- El sistema requiere autenticación obligatoria")
    print("- Se implementó control de intentos fallidos")
    print("- Todas las contraseñas están encriptadas con bcrypt")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstalación cancelada por el usuario.")
    except Exception as e:
        print(f"\n\nError durante la instalación: {e}")
        print("Contacte al desarrollador para soporte.")