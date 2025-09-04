-- =====================================================
-- SCRIPT DE LIMPIEZA DE DATOS TRANSACCIONALES
-- Base de datos: disfruleg
-- Fecha: Diciembre 2024
-- 
-- IMPORTANTE: Este script eliminará TODOS los datos de:
-- - Órdenes guardadas
-- - Facturas y sus detalles
-- - Deudas
-- - Secuencias de folios
-- 
-- CONSERVARÁ:
-- - Productos
-- - Clientes
-- - Grupos
-- - Tipos de cliente
-- - Precios
-- - Historial de compras
-- =====================================================

USE disfruleg;

-- 1. DESACTIVAR VERIFICACIONES DE FOREIGN KEY
SET FOREIGN_KEY_CHECKS = 0;

-- 2. LIMPIAR TABLAS TRANSACCIONALES
-- (En orden para evitar problemas con dependencias)

-- Limpiar órdenes guardadas
TRUNCATE TABLE ordenes_guardadas;
SELECT 'Órdenes guardadas eliminadas' AS status;

-- Limpiar detalles de factura
TRUNCATE TABLE detalle_factura;
SELECT 'Detalles de factura eliminados' AS status;

-- Limpiar secciones de factura
TRUNCATE TABLE seccion_factura;
SELECT 'Secciones de factura eliminadas' AS status;

-- Limpiar metadata de facturas
TRUNCATE TABLE factura_metadata;
SELECT 'Metadata de facturas eliminada' AS status;

-- Limpiar deudas
TRUNCATE TABLE deuda;
SELECT 'Deudas eliminadas' AS status;

-- Limpiar facturas
TRUNCATE TABLE factura;
SELECT 'Facturas eliminadas' AS status;

-- Limpiar logs de acceso (opcional - descomenta si quieres limpiarlos)
-- TRUNCATE TABLE log_accesos;
-- SELECT 'Logs de acceso eliminados' AS status;

-- 3. REINICIAR SECUENCIA DE FOLIOS
DELETE FROM folio_sequence;
INSERT INTO folio_sequence (id, next_val) VALUES (1, 1);
SELECT 'Secuencia de folios reiniciada a 1' AS status;

-- 4. REACTIVAR VERIFICACIONES DE FOREIGN KEY
SET FOREIGN_KEY_CHECKS = 1;

-- 5. VERIFICAR ESTADO DE LAS TABLAS
SELECT 'RESUMEN DE LIMPIEZA:' AS status;

SELECT 
    'ordenes_guardadas' AS tabla, 
    COUNT(*) AS registros 
FROM ordenes_guardadas
UNION ALL
SELECT 
    'factura' AS tabla, 
    COUNT(*) AS registros 
FROM factura
UNION ALL
SELECT 
    'detalle_factura' AS tabla, 
    COUNT(*) AS registros 
FROM detalle_factura
UNION ALL
SELECT 
    'deuda' AS tabla, 
    COUNT(*) AS registros 
FROM deuda
UNION ALL
SELECT 
    'folio_sequence' AS tabla,
    next_val - 1 AS registros
FROM folio_sequence WHERE id = 1;

-- 6. VERIFICAR QUE LOS DATOS MAESTROS SIGUEN INTACTOS
SELECT 'DATOS MAESTROS CONSERVADOS:' AS status;

SELECT 
    'producto' AS tabla, 
    COUNT(*) AS registros 
FROM producto
UNION ALL
SELECT 
    'cliente' AS tabla, 
    COUNT(*) AS registros 
FROM cliente
UNION ALL
SELECT 
    'grupo' AS tabla, 
    COUNT(*) AS registros 
FROM grupo
UNION ALL
SELECT 
    'precio_por_grupo' AS tabla, 
    COUNT(*) AS registros 
FROM precio_por_grupo
UNION ALL
SELECT 
    'compra' AS tabla, 
    COUNT(*) AS registros 
FROM compra;

SELECT '✅ LIMPIEZA COMPLETADA EXITOSAMENTE' AS status;