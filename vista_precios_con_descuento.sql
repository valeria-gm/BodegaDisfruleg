USE disfruleg;

CREATE OR REPLACE VIEW vista_precios_con_descuento AS
SELECT 
    p.id_producto,
    p.nombre_producto,
    p.unidad_producto,
    p.precio_base,
    g.id_grupo,
    g.clave_grupo,
    g.descuento,
    ROUND(p.precio_base * (1 - g.descuento / 100), 2) AS precio_final
FROM producto p
CROSS JOIN grupo g
ORDER BY p.nombre_producto;
