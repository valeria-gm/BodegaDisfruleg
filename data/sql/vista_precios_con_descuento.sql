USE disfruleg;

CREATE OR REPLACE VIEW vista_precios_con_descuento AS
SELECT 
    p.id_producto,
    p.nombre_producto,
    p.unidad_producto,
    tc.id_tipo_cliente,
    tc.nombre_tipo AS tipo_cliente,
    pt.precio AS precio_base_para_tipo,
    g.id_grupo,
    g.clave_grupo,
    g.descuento,
    ROUND(pt.precio * (1 - IFNULL(g.descuento, 0)/100), 2) AS precio_final_con_descuento
FROM producto p
JOIN precio_por_tipo pt ON p.id_producto = pt.id_producto
JOIN tipo_cliente tc ON pt.id_tipo_cliente = tc.id_tipo_cliente
LEFT JOIN grupo g ON 1=1  -- Alternativa si realmente se necesita el CROSS JOIN
ORDER BY p.nombre_producto, tc.nombre_tipo, g.clave_grupo;

-- Propósito principal:
-- Ser una herramienta de consulta y referencia para precios actuales antes de facturar.