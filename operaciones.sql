-- Desglose por producto dentro de cada factura
SELECT 
    f.id_factura,
    c.nombre AS cliente,
    p.nombre_producto,
    df.cantidad,
    df.precio_unitario_venta,
    df.subtotal
FROM detalle_factura df
JOIN factura f ON df.id_factura = f.id_factura
JOIN cliente c ON f.id_cliente = c.id_cliente
JOIN producto p ON df.id_producto = p.id_producto
ORDER BY f.id_factura, df.id_detalle;

-- Total general por factura
SELECT 
    f.id_factura,
    c.nombre AS cliente,
    SUM(df.subtotal) AS total_factura
FROM detalle_factura df
JOIN factura f ON df.id_factura = f.id_factura
JOIN cliente c ON f.id_cliente = c.id_cliente
GROUP BY f.id_factura, c.nombre
ORDER BY f.id_factura;

