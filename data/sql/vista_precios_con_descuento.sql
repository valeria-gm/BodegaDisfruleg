USE disfruleg;

CREATE OR REPLACE VIEW vista_precios_con_descuento AS
SELECT 
    p.id_producto,
    p.nombre_producto,
    p.unidad_producto,
    g.id_grupo,
    g.clave_grupo,
    pg.precio_base AS precio_base_para_grupo,
    tc.id_tipo_cliente,
    tc.nombre_tipo AS tipo_cliente,
    tc.descuento,
    ROUND(pg.precio_base * (1 - tc.descuento/100), 2) AS precio_final_con_descuento
FROM producto p
CROSS JOIN grupo g
JOIN precio_por_grupo pg ON p.id_producto = pg.id_producto AND g.id_grupo = pg.id_grupo
JOIN tipo_cliente tc  -- Mostramos todos los tipos posibles
ORDER BY p.nombre_producto, g.clave_grupo, tc.nombre_tipo;

-- Propósito:
-- Muestra los precios con posibles descuentos para cada combinación grupo-tipo de cliente
-- Nota: Esta vista ahora muestra todas las combinaciones posibles, no asume que el grupo tiene un tipo específico