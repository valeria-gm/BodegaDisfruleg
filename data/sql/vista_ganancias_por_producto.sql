USE disfruleg;

CREATE OR REPLACE VIEW vista_ganancias_por_producto AS
SELECT 
    p.id_producto,
    p.nombre_producto,
    p.unidad_producto,
    SUM(df.cantidad_factura) AS cantidad_vendida,
    SUM(vd.subtotal_con_descuento) AS ingresos_totales,
    COALESCE(SUM(c.cantidad_compra), 0) AS cantidad_comprada,
    COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0) AS costos_totales,
    SUM(vd.subtotal_con_descuento) - COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0) AS ganancia_total,
    CASE 
        WHEN COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0) = 0 THEN 0
        ELSE ROUND(((SUM(vd.subtotal_con_descuento) - 
                    COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0)) / 
                    COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0)) * 100, 2)
    END AS margen_ganancia_porcentaje,
    p.stock
FROM producto p
LEFT JOIN detalle_factura df ON p.id_producto = df.id_producto
LEFT JOIN vista_detalle_factura_con_descuento vd ON df.id_detalle = vd.id_detalle
LEFT JOIN compra c ON p.id_producto = c.id_producto
GROUP BY p.id_producto, p.nombre_producto, p.unidad_producto, p.stock;