#!/usr/bin/env python3
"""
Script para actualizar la vista vista_historial_pagos con el campo folio_numero
"""

import mysql.connector
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.database.conexion import conectar

    def actualizar_vista():
        """Actualiza la vista vista_historial_pagos para incluir folio_numero"""
        conn = conectar()
        if not conn:
            print("❌ No se pudo conectar a la base de datos")
            return False

        cursor = conn.cursor()
        try:
            # Recrear la vista con el campo folio_numero
            vista_sql = """
            CREATE OR REPLACE VIEW vista_historial_pagos AS
            SELECT
                d.id_deuda,
                c.id_cliente,
                c.nombre_cliente,
                f.id_factura,
                f.folio_numero,
                d.monto AS monto_total,
                d.monto_pagado,
                d.fecha_pago,
                d.metodo_pago,
                d.referencia_pago,
                u.username AS registrado_por,
                d.descripcion,
                g.clave_grupo,
                tc.nombre_tipo AS tipo_cliente
            FROM deuda d
            JOIN cliente c ON d.id_cliente = c.id_cliente
            JOIN factura f ON d.id_factura = f.id_factura
            JOIN grupo g ON c.id_grupo = g.id_grupo
            JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
            LEFT JOIN usuarios_sistema u ON d.descripcion LIKE CONCAT('%Operador:%', u.username, '%')
            WHERE d.pagado = TRUE;
            """

            cursor.execute(vista_sql)
            conn.commit()
            print("✅ Vista vista_historial_pagos actualizada exitosamente")

            # Verificar que la vista funciona
            cursor.execute("SELECT COUNT(*) FROM vista_historial_pagos")
            count = cursor.fetchone()[0]
            print(f"✅ Vista funciona correctamente: {count} registros encontrados")

            # Mostrar las columnas de la vista
            cursor.execute("DESCRIBE vista_historial_pagos")
            columnas = cursor.fetchall()
            print("\n📋 Columnas de la vista:")
            for col in columnas:
                print(f"  - {col[0]} ({col[1]})")

            return True

        except Exception as e:
            print(f"❌ Error al actualizar vista: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    if __name__ == "__main__":
        print("🔄 Actualizando vista vista_historial_pagos...")
        if actualizar_vista():
            print("\n✅ Actualización completada con éxito!")
        else:
            print("\n❌ Error en la actualización")

except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Asegúrate de que el módulo esté instalado y el path sea correcto")