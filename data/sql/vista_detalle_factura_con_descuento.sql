USE disfruleg;

CREATE OR REPLACE VIEW vista_detalle_factura_con_descuento AS
SELECT 
    df.id_detalle,
    df.id_factura,
    df.id_producto,
    p.nombre_producto,
    p.unidad_producto,
    df.cantidad_factura,
    -- Precio base según tipo de cliente (antes de descuento)
    pt.precio AS precio_base_tipo,
    -- Descuento del grupo (puede ser NULL)
    g.descuento AS porcentaje_descuento,
    -- Precio final aplicando descuento
    ROUND(pt.precio * (1 - IFNULL(g.descuento, 0)/100), 2) AS precio_unitario_calculado,
    -- Comparación con el precio registrado (para auditoría)
    df.precio_unitario_venta AS precio_registrado,
    -- Subtotal calculado correctamente
    ROUND(df.cantidad_factura * pt.precio * (1 - IFNULL(g.descuento, 0)/100), 2) AS subtotal_con_descuento,
    c.id_tipo_cliente,
    tc.nombre_tipo AS tipo_cliente
FROM detalle_factura df
JOIN factura f ON df.id_factura = f.id_factura
JOIN cliente c ON f.id_cliente = c.id_cliente
JOIN tipo_cliente tc ON c.id_tipo_cliente = tc.id_tipo_cliente
JOIN producto p ON df.id_producto = p.id_producto
JOIN precio_por_tipo pt ON p.id_producto = pt.id_producto AND tc.id_tipo_cliente = pt.id_tipo_cliente
LEFT JOIN grupo g ON c.id_grupo = g.id_grupo;

-- Propósito principal:
-- Mostrar información histórica de lo que ya se facturó, con análisis de cómo se calcularon los precios.