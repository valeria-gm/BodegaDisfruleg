USE disfruleg;

CREATE OR REPLACE VIEW vista_detalle_factura_con_descuento AS
SELECT 
    df.id_detalle,
    df.id_factura,
    df.id_producto,
    p.nombre_producto,
    p.unidad_producto,
    df.cantidad_factura,
    pg.precio_base AS precio_base_grupo,
    tc.descuento AS porcentaje_descuento,
    ROUND(pg.precio_base * (1 - tc.descuento/100), 2) AS precio_unitario_calculado,
    df.precio_unitario_venta AS precio_registrado,
    ROUND(df.cantidad_factura * pg.precio_base * (1 - tc.descuento/100), 2) AS subtotal_con_descuento,
    c.id_tipo_cliente,
    tc.nombre_tipo AS tipo_cliente,
    c.id_grupo,
    g.clave_grupo
FROM detalle_factura df
JOIN factura f ON df.id_factura = f.id_factura
JOIN cliente c ON f.id_cliente = c.id_cliente
JOIN grupo g ON c.id_grupo = g.id_grupo
JOIN tipo_cliente tc ON c.id_tipo_cliente = tc.id_tipo_cliente  -- Tipo viene del cliente, no del grupo
JOIN producto p ON df.id_producto = p.id_producto
JOIN precio_por_grupo pg ON p.id_producto = pg.id_producto AND c.id_grupo = pg.id_grupo;

-- Propósito:
-- Muestra los detalles de factura con el cálculo de descuento basado en el tipo de cliente asociado al cliente