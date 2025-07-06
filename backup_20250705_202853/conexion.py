import mysql.connector
from mysql.connector import Error

# Variable global para estado de disponibilidad
db_available = False

def verify_db_availability():
    global db_available
    try:
        conn = conectar()
        if conn and conn.is_connected():
            db_available = True
            conn.close()
        return db_available
    except:
        return False

def conectar():
    try:
        conn = mysql.connector.connect(
            #unix_socket='/var/run/mysqld/mysqld.sock',
            host='localhost',
            port=3306,
            user='jared',
            password='zoibnG31!!EAEA',
            database='disfruleg',
            auth_plugin='mysql_native_password'
        )
        return conn
    except Error as e:
        print(f"Error de conexión: {e}")
        return None

# Verificar disponibilidad al importar
verify_db_availability()