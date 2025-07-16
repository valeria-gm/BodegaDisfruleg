# database.py
# Módulo actualizado para interactuar con la base de datos 'disfruleg'.

import mysql.connector
from mysql.connector import Error
import bcrypt # Para el manejo seguro de contraseñas

# --- CONFIGURACIÓN DE LA CONEXIÓN ---
# !! Asegúrate de que estos valores son correctos.
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root', # La contraseña de tu usuario de MySQL
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
            SELECT p.nombre_producto, ppg.precio_base
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
            SELECT p.nombre_producto, ppg.precio_base, p.es_especial
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

# --- Funciones de Facturación ---

def crear_factura_completa(id_cliente, items_carrito):
    """
    Crea una transacción completa: factura, detalles, deuda y actualiza stock.
    Retorna el ID de la nueva factura o None si falla.
    """
    conn = conectar()
    if not conn: return None
    
    cursor = conn.cursor()
    id_factura_nueva = None
    
    try:
        # Iniciar una transacción para asegurar que todas las operaciones se completen
        conn.start_transaction()

        # 1. Crear la factura
        query_factura = "INSERT INTO factura (fecha_factura, id_cliente) VALUES (CURDATE(), %s)"
        cursor.execute(query_factura, (id_cliente,))
        id_factura_nueva = cursor.lastrowid # Obtener el ID de la factura recién creada

        # 2. Insertar cada producto en detalle_factura y actualizar stock
        monto_total = 0.0
        query_detalle = """
            INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta)
            VALUES (%s, (SELECT id_producto FROM producto WHERE nombre_producto = %s), %s, %s)
        """
        query_stock = "UPDATE producto SET stock = stock - %s WHERE nombre_producto = %s"

        for cantidad, nombre_prod, precio_unit_str, subtotal_str in items_carrito:
            precio_unit = float(precio_unit_str.replace('$', ''))
            cantidad_float = float(cantidad)
            
            # Insertar detalle
            cursor.execute(query_detalle, (id_factura_nueva, nombre_prod, cantidad_float, precio_unit))
            # Actualizar stock
            cursor.execute(query_stock, (cantidad_float, nombre_prod))
            
            monto_total += float(subtotal_str.replace('$', ''))

        # 3. Crear la deuda asociada a la factura
        query_deuda = "INSERT INTO deuda (id_cliente, id_factura, monto, fecha_generada) VALUES (%s, %s, %s, CURDATE())"
        cursor.execute(query_deuda, (id_cliente, id_factura_nueva, monto_total))
        
        # Si todo fue exitoso, confirmar la transacción
        conn.commit()

    except Error as e:
        print(f"Error en la transacción de facturación: {e}")
        # Si algo falla, revertir todos los cambios
        conn.rollback()
        id_factura_nueva = None
    finally:
        cursor.close()
        conn.close()
        
    return id_factura_nueva


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