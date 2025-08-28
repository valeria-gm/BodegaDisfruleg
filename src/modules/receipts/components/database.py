# database.py
# Módulo actualizado para interactuar con la base de datos 'disfruleg'.

import mysql.connector
from mysql.connector import Error
import bcrypt # Para el manejo seguro de contraseñas

# --- CONFIGURACIÓN DE LA CONEXIÓN ---
# !! Asegúrate de que estos valores son correctos.
db_config = {
    'host': 'localhost',
    'user': 'jared',
    'password': 'zoibnG31!!EAEA', # La contraseña de tu usuario de MySQL
    'database': 'disfruleg'
}

def conectar():
    """Establece la conexión a la base de datos."""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

# --- Funciones de Autenticación ---

def validar_usuario(username, password):
    """
    Valida las credenciales de un usuario contra la base de datos.
    Retorna el rol del usuario si es válido, de lo contrario None.
    """
    conn = conectar()
    if not conn: return None
    
    rol_usuario = None
    cursor = conn.cursor(dictionary=True) # dictionary=True para obtener resultados como dict
    
    try:
        query = "SELECT password_hash, rol FROM usuarios_sistema WHERE username = %s AND activo = TRUE"
        cursor.execute(query, (username,))
        usuario = cursor.fetchone()

        if usuario:
            # Compara la contraseña proporcionada con el hash almacenado
            if bcrypt.checkpw(password.encode('utf-8'), usuario['password_hash'].encode('utf-8')):
                rol_usuario = usuario['rol']
                # Aquí podrías agregar lógica para registrar el acceso en log_accesos
    except Error as e:
        print(f"Error al validar usuario: {e}")
    finally:
        cursor.close()
        conn.close()
        
    return rol_usuario

# --- Funciones de Clientes y Grupos ---

def obtener_grupos():
    """Obtiene todos los grupos de clientes."""
    conn = conectar()
    if not conn: return []
    
    grupos = []
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_grupo, clave_grupo FROM grupo ORDER BY clave_grupo")
        grupos = cursor.fetchall()
    except Error as e:
        print(f"Error al obtener grupos: {e}")
    finally:
        cursor.close()
        conn.close()
    return grupos

def obtener_clientes_por_grupo(id_grupo):
    """Obtiene los clientes que pertenecen a un grupo específico."""
    conn = conectar()
    if not conn: return []
    
    clientes = []
    cursor = conn.cursor()
    try:
        query = "SELECT id_cliente, nombre_cliente FROM cliente WHERE id_grupo = %s ORDER BY nombre_cliente"
        cursor.execute(query, (id_grupo,))
        clientes = cursor.fetchall()
    except Error as e:
        print(f"Error al obtener clientes: {e}")
    finally:
        cursor.close()
        conn.close()
    return clientes

# --- Funciones de Productos y Precios ---

def buscar_productos_por_grupo(id_grupo, texto_busqueda):
    """
    Busca productos y obtiene su precio específico para un grupo de clientes.
    """
    conn = conectar()
    if not conn: return []
    
    productos = []
    cursor = conn.cursor()
    try:
        # Unimos producto con precio_por_grupo para obtener el precio correcto
        query = """
            SELECT p.nombre_producto, ppg.precio_base, p.unidad_producto
            FROM producto p
            JOIN precio_por_grupo ppg ON p.id_producto = ppg.id_producto
            WHERE ppg.id_grupo = %s AND p.nombre_producto LIKE %s AND p.stock > 0
        """
        valores = (id_grupo, f"%{texto_busqueda}%")
        cursor.execute(query, valores)
        productos = cursor.fetchall()
    except Error as e:
        print(f"Error al buscar productos: {e}")
    finally:
        cursor.close()
        conn.close()
    return productos

def buscar_productos_por_grupo_con_especial(id_grupo, texto_busqueda):
    """
    Busca productos y obtiene su precio específico para un grupo de clientes,
    incluyendo si el producto es 'especial'.
    """
    conn = conectar()
    if not conn: return []
    
    productos = []
    cursor = conn.cursor()
    try:
        query = """
            SELECT p.nombre_producto, ppg.precio_base, p.es_especial, p.unidad_producto
            FROM producto p
            JOIN precio_por_grupo ppg ON p.id_producto = ppg.id_producto
            WHERE ppg.id_grupo = %s AND p.nombre_producto LIKE %s AND p.stock > 0
        """
        valores = (id_grupo, f"%{texto_busqueda}%")
        cursor.execute(query, valores)
        productos = cursor.fetchall()
    except Error as e:
        print(f"Error al buscar productos con es_especial: {e}")
    finally:
        cursor.close()
        conn.close()
    return productos

def obtener_producto_por_nombre(nombre_producto):
    """Obtiene información completa de un producto por su nombre."""
    conn = conectar()
    if not conn: return None
    
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM producto WHERE nombre_producto = %s"
        cursor.execute(query, (nombre_producto,))
        producto = cursor.fetchone()
        return producto
    except Error as e:
        print(f"Error al obtener producto: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# --- Funciones de Numeración de Folios ---

def obtener_siguiente_folio():
    """
    Obtiene el siguiente número de folio disponible usando la secuencia.
    Retorna un número de folio único e incremental.
    """
    conn = conectar()
    if not conn: return None
    
    cursor = conn.cursor()
    siguiente_folio = None
    
    try:
        # Usar la tabla de secuencia para obtener el siguiente folio
        cursor.execute("SELECT next_val FROM folio_sequence WHERE id = 1 FOR UPDATE")
        resultado = cursor.fetchone()
        
        if resultado:
            siguiente_folio = resultado[0]
            # Actualizar la secuencia
            cursor.execute("UPDATE folio_sequence SET next_val = next_val + 1 WHERE id = 1")
            conn.commit()
        else:
            # Inicializar la secuencia si no existe
            cursor.execute("INSERT INTO folio_sequence (id, next_val) VALUES (1, 2)")
            siguiente_folio = 1
            conn.commit()
        
    except Error as e:
        print(f"Error al obtener siguiente folio: {e}")
        conn.rollback()
    finally:
        cursor.close()
    
    return siguiente_folio

def verificar_folio_disponible(folio):
    """
    Verifica si un folio específico está disponible para usar.
    
    En el diseño actual:
    - Las facturas usan id_factura (AUTO_INCREMENT) como identificador único
    - Las órdenes guardadas usan folio_numero para reservar números secuenciales
    - Un folio está disponible si no existe una factura con ese ID 
      Y no hay una orden activa que lo reserve
    
    Args:
        folio (int): Número de folio a verificar
        
    Returns:
        bool: True si está disponible, False si está ocupado
    """
    conn = conectar()
    if not conn: 
        return False
    
    cursor = conn.cursor()
    
    try:
        # Verificar si existe factura con ese ID
        # En nuestro diseño, id_factura actúa como el folio oficial
        query_factura = "SELECT COUNT(*) FROM factura WHERE id_factura = %s"
        cursor.execute(query_factura, (folio,))
        count_factura = cursor.fetchone()[0]
        
        # Verificar si hay órdenes activas que reserven ese folio
        query_orden = """
            SELECT COUNT(*) FROM ordenes_guardadas 
            WHERE folio_numero = %s AND activo = TRUE
        """
        cursor.execute(query_orden, (folio,))
        count_orden = cursor.fetchone()[0]
        
        # El folio está disponible si no está usado en ninguna tabla
        disponible = (count_factura + count_orden) == 0
        
        return disponible
        
    except Error as e:
        print(f"Error al verificar disponibilidad del folio {folio}: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def verificar_rango_folios_disponibles(inicio, fin):
    """
    Verifica un rango de folios para encontrar el primero disponible.
    Útil cuando necesitas encontrar gaps en la secuencia.
    
    Args:
        inicio (int): Folio inicial del rango
        fin (int): Folio final del rango
        
    Returns:
        int or None: Primer folio disponible en el rango, None si no hay ninguno
    """
    for folio in range(inicio, fin + 1):
        if verificar_folio_disponible(folio):
            return folio
    return None

def obtener_folios_ocupados(limite=100):
    """
    Obtiene una lista de todos los folios actualmente ocupados.
    Útil para diagnóstico y debugging.
    
    Args:
        limite (int): Máximo número de folios a verificar
        
    Returns:
        dict: {'facturas': [list], 'ordenes': [list], 'todos': [list]}
    """
    conn = conectar()
    if not conn:
        return {'facturas': [], 'ordenes': [], 'todos': []}
    
    cursor = conn.cursor()
    folios_ocupados = {'facturas': [], 'ordenes': [], 'todos': []}
    
    try:
        # Obtener folios usados en facturas
        cursor.execute("SELECT id_factura FROM factura ORDER BY id_factura")
        facturas = [row[0] for row in cursor.fetchall()]
        
        # Obtener folios reservados en órdenes activas
        cursor.execute("""
            SELECT folio_numero FROM ordenes_guardadas 
            WHERE activo = TRUE 
            ORDER BY folio_numero
        """)
        ordenes = [row[0] for row in cursor.fetchall()]
        
        # Combinar y eliminar duplicados
        todos = sorted(set(facturas + ordenes))
        
        folios_ocupados = {
            'facturas': facturas,
            'ordenes': ordenes,
            'todos': todos
        }
        
    except Error as e:
        print(f"Error al obtener folios ocupados: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return folios_ocupados

def diagnosticar_sistema_folios():
    """
    Función de diagnóstico para verificar el estado del sistema de folios.
    Útil para detectar inconsistencias.
    
    Returns:
        dict: Reporte completo del estado del sistema
    """
    conn = conectar()
    if not conn:
        return {'error': 'No se pudo conectar a la base de datos'}
    
    cursor = conn.cursor()
    reporte = {}
    
    try:
        # Estado de la secuencia
        cursor.execute("SELECT next_val FROM folio_sequence WHERE id = 1")
        resultado = cursor.fetchone()
        reporte['siguiente_folio_secuencia'] = resultado[0] if resultado else None
        
        # Máximo folio en facturas
        cursor.execute("SELECT MAX(id_factura) FROM factura")
        reporte['max_folio_facturas'] = cursor.fetchone()[0] or 0
        
        # Máximo folio en órdenes
        cursor.execute("SELECT MAX(folio_numero) FROM ordenes_guardadas WHERE activo = TRUE")
        reporte['max_folio_ordenes'] = cursor.fetchone()[0] or 0
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM factura")
        reporte['total_facturas'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ordenes_guardadas WHERE activo = TRUE")
        reporte['total_ordenes_activas'] = cursor.fetchone()[0]
        
        # Detectar inconsistencias
        max_usado = max(reporte['max_folio_facturas'], reporte['max_folio_ordenes'])
        siguiente_secuencia = reporte['siguiente_folio_secuencia'] or 1
        
        reporte['inconsistencia_detectada'] = siguiente_secuencia <= max_usado
        reporte['folios_potencialmente_duplicados'] = []
        
        if reporte['inconsistencia_detectada']:
            # Buscar posibles duplicados
            cursor.execute("""
                SELECT f.id_factura 
                FROM factura f, ordenes_guardadas o 
                WHERE f.id_factura = o.folio_numero AND o.activo = TRUE
            """)
            reporte['folios_potencialmente_duplicados'] = [row[0] for row in cursor.fetchall()]
        
    except Error as e:
        reporte['error'] = f"Error durante diagnóstico: {e}"
    finally:
        cursor.close()
        conn.close()
    
    return reporte

# Función de mantenimiento para corregir inconsistencias
def reparar_secuencia_folios():
    """
    Repara la secuencia de folios para evitar conflictos futuros.
    Ajusta next_val al siguiente número disponible.
    
    Returns:
        dict: Resultado de la reparación
    """
    conn = conectar()
    if not conn:
        return {'error': 'No se pudo conectar a la base de datos'}
    
    cursor = conn.cursor()
    
    try:
        # Encontrar el mayor folio usado
        cursor.execute("SELECT MAX(id_factura) FROM factura")
        max_factura = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT MAX(folio_numero) FROM ordenes_guardadas WHERE activo = TRUE")
        max_orden = cursor.fetchone()[0] or 0
        
        siguiente_seguro = max(max_factura, max_orden) + 1
        
        # Actualizar la secuencia
        cursor.execute("UPDATE folio_sequence SET next_val = %s WHERE id = 1", (siguiente_seguro,))
        conn.commit()
        
        return {
            'exito': True,
            'max_factura': max_factura,
            'max_orden': max_orden,
            'nuevo_next_val': siguiente_seguro,
            'mensaje': f'Secuencia reparada. Próximo folio será: {siguiente_seguro}'
        }
        
    except Error as e:
        conn.rollback()
        return {'error': f'Error al reparar secuencia: {e}'}
    finally:
        cursor.close()
        conn.close()

# --- Funciones de Facturación ---

def crear_factura_completa(id_cliente, items_carrito, folio_numero=None):
    """
    Crea una transacción completa: factura, detalles y actualiza stock.
    Ahora compatible con el trigger after_factura_insert que maneja la deuda automáticamente.
    Retorna un diccionario con el ID de la nueva factura y el número de folio.
    """
    conn = conectar()
    if not conn: return None
    
    cursor = conn.cursor()
    id_factura_nueva = None
    folio_usado = folio_numero
    
    try:
        # Iniciar una transacción para asegurar que todas las operaciones se completen
        conn.start_transaction()

        # 1. Crear la factura (el trigger manejará la deuda automáticamente)
        if folio_usado:
            # Si se proporciona folio específico, forzar el AUTO_INCREMENT
            query_factura = "INSERT INTO factura (id_factura, fecha_factura, id_cliente) VALUES (%s, CURDATE(), %s)"
            cursor.execute(query_factura, (folio_usado, id_cliente))
            id_factura_nueva = folio_usado
        else:
            query_factura = "INSERT INTO factura (fecha_factura, id_cliente) VALUES (CURDATE(), %s)"
            cursor.execute(query_factura, (id_cliente,))
            id_factura_nueva = cursor.lastrowid

        # 2. Insertar cada producto en detalle_factura
        # Los triggers se encargarán de actualizar stock y validar existencia
        query_detalle = """
            INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta)
            VALUES (%s, (SELECT id_producto FROM producto WHERE nombre_producto = %s), %s, %s)
        """

        for cantidad, nombre_prod, precio_unit_str, subtotal_str, unidad_producto in items_carrito:
            precio_unit = float(precio_unit_str.replace('$', ''))
            cantidad_float = float(cantidad)
            
            # Insertar detalle - los triggers manejarán stock y validaciones
            cursor.execute(query_detalle, (id_factura_nueva, nombre_prod, cantidad_float, precio_unit))

        # Si todo fue exitoso, confirmar la transacción
        conn.commit()
        folio_usado = id_factura_nueva

    except Error as e:
        print(f"Error en la transacción de facturación: {e}")
        # Si algo falla, revertir todos los cambios
        conn.rollback()
        id_factura_nueva = None
        folio_usado = None
    finally:
        cursor.close()
        conn.close()
        
    return {
        'id_factura': id_factura_nueva,
        'folio_numero': folio_usado
    } if id_factura_nueva else None

# --- Funciones de Gestión de Tipos de Cliente ---

def obtener_tipos_cliente():
    """Obtiene todos los tipos de cliente."""
    conn = conectar()
    if not conn: return []
    
    tipos = []
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_tipo_cliente, nombre_tipo, descuento FROM tipo_cliente ORDER BY nombre_tipo")
        tipos = cursor.fetchall()
    except Error as e:
        print(f"Error al obtener tipos de cliente: {e}")
    finally:
        cursor.close()
        conn.close()
    return tipos

def obtener_grupo_con_tipo(id_grupo):
    """Obtiene información completa de un grupo incluyendo su tipo de cliente."""
    conn = conectar()
    if not conn: return None
    
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT g.*, tc.nombre_tipo, tc.descuento
            FROM grupo g
            LEFT JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
            WHERE g.id_grupo = %s
        """
        cursor.execute(query, (id_grupo,))
        grupo = cursor.fetchone()
        return grupo
    except Error as e:
        print(f"Error al obtener grupo con tipo: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# --- BLOQUE DE PRUEBA ---
if __name__ == '__main__':
    print("--- Probando funciones del nuevo database.py para 'disfruleg' ---")
    
    # Para probar, necesitas tener datos en tus tablas.
    # Por ejemplo, un grupo con id=1.
    print("\nObteniendo grupos:")
    grupos = obtener_grupos()
    if grupos:
        print(f"Grupos encontrados: {grupos}")
        id_grupo_prueba = grupos[0][0] # Usar el primer grupo para las demás pruebas
        
        print(f"\nObteniendo clientes del grupo ID {id_grupo_prueba}:")
        clientes = obtener_clientes_por_grupo(id_grupo_prueba)
        print(f"Clientes encontrados: {clientes}")

        print(f"\nBuscando productos para el grupo ID {id_grupo_prueba} que contengan 'a':")
        productos = buscar_productos_por_grupo(id_grupo_prueba, 'a')
        print(f"Productos encontrados: {productos}")

        print(f"\nBuscando productos (con 'es_especial') para el grupo ID {id_grupo_prueba} que contengan 'e':")
        productos_especiales = buscar_productos_por_grupo_con_especial(id_grupo_prueba, 'e')
        print(f"Productos especiales encontrados: {productos_especiales}")
    else:
        print("No se encontraron grupos. Asegúrate de tener datos en la BD.")
    
    print(f"\nObteniendo siguiente folio:")
    folio = obtener_siguiente_folio()
    print(f"Siguiente folio: {folio}")
    
    print(f"\nObteniendo tipos de cliente:")
    tipos = obtener_tipos_cliente()
    print(f"Tipos encontrados: {tipos}")