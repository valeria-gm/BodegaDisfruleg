USE disfruleg;

-- Insertar facturas y detalles para Fuego & Brasa (Grupo Mrl)
INSERT INTO factura (fecha_factura, id_cliente) VALUES 
('2023-10-01', 3),
('2023-10-05', 3),
('2023-10-10', 3);

INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 1 (Fuego & Brasa)
(1, 2, 10.00, 40.00), -- Huevo
(1, 7, 5.00, 24.00),  -- Jitomate
(1, 10, 3.00, 100.00), -- Bistec de puerco
-- Factura 2 (Fuego & Brasa)
(2, 3, 8.00, 38.00),  -- Jitomate bola
(2, 6, 15.00, 30.00), -- Frijol
(2, 12, 2.00, 130.00), -- Queso Oaxaca
-- Factura 3 (Fuego & Brasa)
(3, 5, 10.00, 40.00), -- Rábano rojo
(3, 9, 5.00, 85.00),  -- Chorizo
(3, 14, 3.00, 45.00); -- Frambuesa

-- Insertar facturas y detalles para El Jardín de los Platos (Grupo Mrl)
INSERT INTO factura (fecha_factura, id_cliente) VALUES 
('2023-10-02', 4),
('2023-10-08', 4);

INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 4 (El Jardín de los Platos)
(4, 1, 5.00, 45.00),  -- Col morado
(4, 4, 2.00, 65.00),  -- Chile habanero
(4, 8, 10.00, 18.00), -- Apio
(4, 13, 4.00, 16.00), -- Sandía
-- Factura 5 (El Jardín de los Platos)
(5, 11, 3.00, 130.00), -- Tocino
(5, 16, 1.00, 550.00); -- Tequila

-- Insertar facturas y detalles para Tinto & Trufa (Grupo Salerosa)
INSERT INTO factura (fecha_factura, id_cliente) VALUES 
('2023-10-03', 5),
('2023-10-07', 5),
('2023-10-12', 5);

INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 6 (Tinto & Trufa)
(6, 2, 12.00, 35.00),  -- Huevo
(6, 7, 8.00, 22.00),   -- Jitomate
(6, 12, 3.00, 125.00), -- Queso Oaxaca
-- Factura 7 (Tinto & Trufa)
(7, 3, 10.00, 34.00),  -- Jitomate bola
(7, 10, 4.00, 95.00),  -- Bistec de puerco
(7, 15, 2.00, 25.00),  -- Tenedores (especial)
-- Factura 8 (Tinto & Trufa)
(8, 5, 15.00, 35.00),  -- Rábano rojo
(8, 9, 6.00, 80.00),   -- Chorizo
(8, 16, 2.00, 520.00); -- Tequila

-- Insertar facturas y detalles para Sazón Nómada (Grupo Salerosa)
INSERT INTO factura (fecha_factura, id_cliente) VALUES 
('2023-10-04', 6),
('2023-10-11', 6);

INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 9 (Sazón Nómada)
(9, 1, 8.00, 40.00),  -- Col morado
(9, 6, 20.00, 28.00), -- Frijol
(9, 11, 4.00, 125.00), -- Tocino
-- Factura 10 (Sazón Nómada)
(10, 4, 3.00, 60.00),  -- Chile habanero
(10, 8, 12.00, 16.00), -- Apio
(10, 14, 5.00, 42.00); -- Frambuesa

-- Insertar facturas y detalles para Cuchara Urbana (Grupo Bocanegra)
INSERT INTO factura (fecha_factura, id_cliente) VALUES 
('2023-10-06', 7),
('2023-10-09', 7);

INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 11 (Cuchara Urbana)
(11, 2, 15.00, 45.00), -- Huevo
(11, 7, 10.00, 32.00), -- Jitomate
(11, 10, 5.00, 105.00), -- Bistec de puerco
-- Factura 12 (Cuchara Urbana)
(12, 3, 12.00, 44.00), -- Jitomate bola
(12, 12, 4.00, 135.00), -- Queso Oaxaca
(12, 15, 3.00, 35.00); -- Tenedores (especial)

-- Insertar facturas y detalles para Casa Mar & Tierra (Grupo General)
INSERT INTO factura (fecha_factura, id_cliente) VALUES 
('2023-10-13', 9),
('2023-10-15', 9);

INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 13 (Casa Mar & Tierra)
(13, 1, 10.00, 50.00), -- Col morado
(13, 5, 20.00, 45.00), -- Rábano rojo
(13, 9, 8.00, 90.00),  -- Chorizo
-- Factura 14 (Casa Mar & Tierra)
(14, 6, 25.00, 38.00), -- Frijol
(14, 13, 6.00, 25.00), -- Sandía
(14, 16, 1.00, 620.00); -- Tequila

-- Insertar facturas y detalles para Albahaca y Olivo (Grupo 3M)
INSERT INTO factura (fecha_factura, id_cliente) VALUES 
('2023-10-14', 11),
('2023-10-16', 11);

INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 15 (Albahaca y Olivo)
(15, 2, 20.00, 25.00), -- Huevo
(15, 7, 15.00, 12.00), -- Jitomate
(15, 10, 6.00, 85.00), -- Bistec de puerco
-- Factura 16 (Albahaca y Olivo)
(16, 4, 5.00, 50.00),  -- Chile habanero
(16, 8, 20.00, 16.00), -- Apio
(16, 14, 8.00, 32.00); -- Frambuesa

-- Insertar facturas y detalles para Manjar Moderno (Grupo Especial)
INSERT INTO factura (fecha_factura, id_cliente) VALUES 
('2023-10-17', 13),
('2023-10-19', 13);

INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
-- Factura 17 (Manjar Moderno)
(17, 1, 12.00, 33.00), -- Col morado
(17, 3, 15.00, 23.00), -- Jitomate bola
(17, 6, 30.00, 13.00), -- Frijol
-- Factura 18 (Manjar Moderno)
(18, 9, 10.00, 73.00), -- Chorizo
(18, 12, 5.00, 113.00), -- Queso Oaxaca
(18, 15, 4.00, 13.00); -- Tenedores (especial)