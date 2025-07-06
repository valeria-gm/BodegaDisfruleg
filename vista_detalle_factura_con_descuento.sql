USE disfruleg;

-- Una vista funciona como una tabla virtual que puedes consultar como cualquier SELECT, pero no puedes modificar directamente.
USE disfruleg;

CREATE OR REPLACE VIEW vista_detalle_factura_con_descuento AS
SELECT 
    df.id_detalle,
    df.id_factura,
    df.id_producto,
    df.cantidad_factura,
    df.precio_unitario_venta,
    g.descuento,
    ROUND(
        df.cantidad_factura * df.precio_unitario_venta * (1 - IFNULL(g.descuento, 0)/100), 
        2
    ) AS subtotal_con_descuento
FROM detalle_factura df
JOIN factura f ON df.id_factura = f.id_factura
JOIN cliente c ON f.id_cliente = c.id_cliente
LEFT JOIN grupo g ON c.id_grupo = g.id_grupo;


-- si el cliente no tiene grupo, el descuento se considera 0 
-- redondea el resultado a 2 decimales

