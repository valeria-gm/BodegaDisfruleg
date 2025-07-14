USE disfruleg;

CREATE OR REPLACE VIEW vista_ganancias_por_grupo AS
SELECT 
    g.id_grupo,
    g.clave_grupo,
    COUNT(DISTINCT c.id_cliente) AS cantidad_clientes,
    SUM(vd.subtotal_con_descuento) AS total_ventas,
    COUNT(DISTINCT f.id_factura) AS cantidad_facturas,
    AVG(tc.descuento) AS descuento_promedio
FROM grupo g
LEFT JOIN cliente c ON g.id_grupo = c.id_grupo
LEFT JOIN factura f ON c.id_cliente = f.id_cliente
LEFT JOIN detalle_factura df ON f.id_factura = df.id_factura
LEFT JOIN vista_detalle_factura_con_descuento vd ON df.id_detalle = vd.id_detalle
LEFT JOIN tipo_cliente tc ON c.id_tipo_cliente = tc.id_tipo_cliente
GROUP BY g.id_grupo, g.clave_grupo;