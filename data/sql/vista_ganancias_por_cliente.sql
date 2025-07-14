USE disfruleg;

CREATE OR REPLACE VIEW vista_ganancias_por_cliente AS
SELECT 
    c.id_cliente,
    c.nombre_cliente,
    g.clave_grupo,
    tc.nombre_tipo AS tipo_cliente,
    tc.descuento AS porcentaje_descuento,
    SUM(vd.subtotal_con_descuento) AS total_ventas,
    COUNT(DISTINCT f.id_factura) AS cantidad_facturas,
    MAX(f.fecha_factura) AS ultima_compra
FROM cliente c
JOIN factura f ON c.id_cliente = f.id_cliente
JOIN detalle_factura df ON f.id_factura = df.id_factura
JOIN vista_detalle_factura_con_descuento vd ON df.id_detalle = vd.id_detalle
JOIN grupo g ON c.id_grupo = g.id_grupo
JOIN tipo_cliente tc ON c.id_tipo_cliente = tc.id_tipo_cliente
GROUP BY c.id_cliente, c.nombre_cliente, g.clave_grupo, tc.nombre_tipo, tc.descuento;