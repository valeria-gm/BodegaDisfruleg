USE disfruleg;

-- Compras en diferentes meses y años
INSERT INTO compra (fecha_compra, id_producto, cantidad_compra, precio_unitario_compra) VALUES
-- Compras en 2023
('2023-09-15', 1, 100.00, 30.00), ('2023-09-15', 2, 200.00, 20.00), ('2023-09-15', 3, 150.00, 25.00),
('2023-10-01', 4, 50.00, 40.00), ('2023-10-01', 5, 80.00, 30.00), ('2023-10-01', 6, 120.00, 20.00),
('2023-11-10', 7, 90.00, 15.00), ('2023-11-10', 8, 70.00, 12.00), ('2023-11-10', 9, 40.00, 60.00),
('2023-12-05', 10, 30.00, 80.00), ('2023-12-05', 11, 25.00, 90.00), ('2023-12-05', 12, 20.00, 100.00),

-- Compras en 2024
('2024-01-15', 1, 120.00, 32.00), ('2024-01-15', 2, 180.00, 22.00), ('2024-01-15', 3, 160.00, 26.00),
('2024-02-10', 4, 60.00, 42.00), ('2024-02-10', 5, 90.00, 32.00), ('2024-02-10', 6, 110.00, 22.00),
('2024-03-20', 7, 100.00, 16.00), ('2024-03-20', 8, 80.00, 13.00), ('2024-03-20', 9, 50.00, 65.00),
('2024-04-25', 10, 35.00, 85.00), ('2024-04-25', 11, 30.00, 95.00), ('2024-04-25', 12, 25.00, 105.00);

-- Ventas en diferentes meses y años
INSERT INTO factura (fecha_factura, id_cliente) VALUES 
-- Ventas en 2023 (octubre ya existe)
('2023-09-05', 3), ('2023-09-12', 4), ('2023-09-18', 5), ('2023-09-25', 6),
('2023-11-02', 3), ('2023-11-08', 4), ('2023-11-15', 5), ('2023-11-22', 6),
('2023-12-03', 3), ('2023-12-10', 4), ('2023-12-17', 5), ('2023-12-23', 6),

-- Ventas en 2024
('2024-01-05', 3), ('2024-01-12', 4), ('2024-01-19', 5), ('2024-01-26', 6),
('2024-02-07', 3), ('2024-02-14', 4), ('2024-02-21', 5), ('2024-02-28', 6),
('2024-03-06', 3), ('2024-03-13', 4), ('2024-03-20', 5), ('2024-03-27', 6),
('2024-04-04', 3), ('2024-04-11', 4), ('2024-04-18', 5), ('2024-04-25', 6);

-- Detalles de facturas para las ventas de 2023-09
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 19 (Fuego & Brasa - 2023-09-05)
(19, 2, 8.00, 42.00), (19, 7, 4.00, 26.00), (19, 10, 2.00, 105.00),
-- Factura 20 (El Jardín - 2023-09-12)
(20, 1, 6.00, 48.00), (20, 4, 3.00, 68.00), (20, 8, 8.00, 20.00),
-- Factura 21 (Tinto & Trufa - 2023-09-18)
(21, 3, 7.00, 40.00), (21, 12, 2.00, 130.00), (21, 15, 1.00, 30.00),
-- Factura 22 (Sazón Nómada - 2023-09-25)
(22, 6, 18.00, 32.00), (22, 11, 3.00, 128.00), (22, 14, 4.00, 46.00);

-- Detalles de facturas para las ventas de 2023-11
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 23 (Fuego & Brasa - 2023-11-02)
(23, 5, 12.00, 42.00), (23, 9, 6.00, 88.00), (23, 14, 2.00, 48.00),
-- Factura 24 (El Jardín - 2023-11-08)
(24, 1, 7.00, 50.00), (24, 4, 2.00, 70.00), (24, 13, 5.00, 28.00),
-- Factura 25 (Tinto & Trufa - 2023-11-15)
(25, 2, 10.00, 38.00), (25, 7, 7.00, 25.00), (25, 16, 1.00, 540.00),
-- Factura 26 (Sazón Nómada - 2023-11-22)
(26, 3, 9.00, 42.00), (26, 8, 15.00, 18.00), (26, 12, 3.00, 132.00);

-- Detalles de facturas para las ventas de 2023-12
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 27 (Fuego & Brasa - 2023-12-03)
(27, 2, 15.00, 44.00), (27, 10, 4.00, 108.00), (27, 15, 2.00, 32.00),
-- Factura 28 (El Jardín - 2023-12-10)
(28, 4, 4.00, 72.00), (28, 8, 10.00, 22.00), (28, 14, 6.00, 50.00),
-- Factura 29 (Tinto & Trufa - 2023-12-17)
(29, 3, 11.00, 46.00), (29, 9, 7.00, 92.00), (29, 16, 2.00, 560.00),
-- Factura 30 (Sazón Nómada - 2023-12-23)
(30, 1, 9.00, 54.00), (30, 6, 22.00, 36.00), (30, 11, 5.00, 135.00);

-- Detalles de facturas para las ventas de 2024-01
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 31 (Fuego & Brasa - 2024-01-05)
(31, 2, 12.00, 46.00), (31, 7, 8.00, 28.00), (31, 12, 3.00, 138.00),
-- Factura 32 (El Jardín - 2024-01-12)
(32, 1, 8.00, 56.00), (32, 5, 15.00, 48.00), (32, 13, 7.00, 32.00),
-- Factura 33 (Tinto & Trufa - 2024-01-19)
(33, 3, 10.00, 50.00), (33, 10, 5.00, 112.00), (33, 15, 3.00, 38.00),
-- Factura 34 (Sazón Nómada - 2024-01-26)
(34, 4, 5.00, 78.00), (34, 8, 14.00, 24.00), (34, 14, 7.00, 54.00);

-- Detalles de facturas para las ventas de 2024-02
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 35 (Fuego & Brasa - 2024-02-07)
(35, 5, 14.00, 50.00), (35, 9, 8.00, 96.00), (35, 16, 1.00, 580.00),
-- Factura 36 (El Jardín - 2024-02-14)
(36, 2, 18.00, 48.00), (36, 7, 12.00, 30.00), (36, 11, 4.00, 140.00),
-- Factura 37 (Tinto & Trufa - 2024-02-21)
(37, 1, 11.00, 58.00), (37, 6, 25.00, 40.00), (37, 12, 4.00, 142.00),
-- Factura 38 (Sazón Nómada - 2024-02-28)
(38, 3, 12.00, 54.00), (38, 8, 16.00, 26.00), (38, 15, 4.00, 42.00);

-- Detalles de facturas para las ventas de 2024-03
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 39 (Fuego & Brasa - 2024-03-06)
(39, 4, 6.00, 82.00), (39, 10, 6.00, 115.00), (39, 14, 8.00, 58.00),
-- Factura 40 (El Jardín - 2024-03-13)
(40, 2, 20.00, 50.00), (40, 5, 18.00, 52.00), (40, 13, 8.00, 36.00),
-- Factura 41 (Tinto & Trufa - 2024-03-20)
(41, 3, 13.00, 58.00), (41, 9, 9.00, 100.00), (41, 16, 2.00, 600.00),
-- Factura 42 (Sazón Nómada - 2024-03-27)
(42, 1, 12.00, 62.00), (42, 7, 15.00, 34.00), (42, 11, 6.00, 148.00);

-- Detalles de facturas para las ventas de 2024-04
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 43 (Fuego & Brasa - 2024-04-04)
(43, 2, 15.00, 52.00), (43, 12, 5.00, 148.00), (43, 15, 5.00, 45.00),
-- Factura 44 (El Jardín - 2024-04-11)
(44, 4, 7.00, 86.00), (44, 8, 18.00, 28.00), (44, 14, 9.00, 62.00),
-- Factura 45 (Tinto & Trufa - 2024-04-18)
(45, 3, 14.00, 62.00), (45, 6, 30.00, 44.00), (45, 10, 7.00, 120.00),
-- Factura 46 (Sazón Nómada - 2024-04-25)
(46, 1, 14.00, 66.00), (46, 5, 20.00, 56.00), (46, 16, 1.00, 620.00);