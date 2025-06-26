-- Insertar grupos
INSERT INTO grupo (clave_grupo, descuento) VALUES 
('Grupo1', 0.00),        -- id_grupo = 1 
('Grupo2', 10.00),       -- id_grupo = 2 
('Grupo3', 20.00);       -- id_grupo = 3 

-- Insertar clientes
INSERT INTO cliente (nombre_cliente, telefono, correo, id_grupo) VALUES
('Ana Pérez', '5551234567', 'ana.perez@example.com', 1),
('Luis Gómez', '5559876543', 'luis.gomez@example.com', 3),
('María López', '5551112222', NULL, 2),
('Carlos Méndez', '5552223333', 'carlos.m@example.com', NULL); -- sin grupo

-- Insertar productos con stock y si son especiales
INSERT INTO producto (nombre_producto, unidad_producto, stock, es_especial) VALUES
('Col morado', 'pz', 100, FALSE),
('Huevo', 'kg', 200, FALSE),
('Jitomate bola', 'kg', 150, FALSE),
('Chile habanero', 'kg', 80, FALSE),
('Rábano rojo', 'manojo', 90, FALSE),
('Frijol', 'kg', 300, FALSE),
('Jitomate', 'kg', 250, FALSE),
('Apio', 'pz', 60, FALSE),
('Chorizo', 'kg', 40, FALSE),
('Bistec de puerco', 'kg', 45, FALSE),
('Tocino', 'kg', 50, FALSE),
('Queso Oaxaca', 'kg', 70, FALSE),
('Sandía', 'pz', 30, FALSE),
('Frambuesa', 'caja', 20, FALSE),
('Tenedores', 'caja', 20, TRUE), -- producto especial
('Tequila', 'botella', 15, TRUE); -- producto especial

-- Precios por grupo
INSERT INTO precio (id_producto, id_grupo, precio) VALUES
-- Grupo 1
(1, 1, 55.00), (2, 1, 49.00), (3, 1, 46.00), (4, 1, 77.00),
(5, 1, 49.00), (6, 1, 35.50), (7, 1, 28.00), (8, 1, 22.00),
(9, 1, 100.00), (10, 1, 119.00), (11, 1, 155.00), (12, 1, 155.00),
(13, 1, 20.00), (14, 1, 53.00), (15, 1, 33.00), (16, 1, 600.00),

-- Grupo 2
(1, 2, 50.00), (2, 2, 42.00), (3, 2, 43.00), (4, 2, 75.00),
(5, 2, 45.00), (6, 2, 32.50), (7, 2, 22.00), (8, 2, 18.00),
(9, 2, 95.00), (10, 2, 109.00), (11, 2, 145.00), (12, 2, 145.00),
(13, 2, 17.00), (14, 2, 49.00), (15, 2, 55.00),

-- Grupo 3
(1, 3, 40.00), (2, 3, 32.00), (3, 3, 33.00), (4, 3, 65.00),
(5, 3, 35.00), (6, 3, 22.50), (7, 3, 12.00), (8, 3, 8.00),
(9, 3, 85.00), (10, 3, 99.00), (11, 3, 135.00), (12, 3, 135.00),
(13, 3, 7.00), (14, 3, 39.00), (15, 3, 45.00);

-- Facturas
INSERT INTO factura (fecha_factura, id_cliente) VALUES
('2025-04-27', 1),
('2025-04-27', 2),
('2025-05-02', 3),
('2025-05-03', 1),
('2025-05-04', 2),
('2025-05-06', 4); -- cliente sin grupo

-- Detalles de factura 1
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
(1, 1, 1.0, 55.00), (1, 2, 0.5, 49.00), (1, 3, 2.0, 46.00),
(1, 4, 0.25, 77.00), (1, 5, 1.0, 49.00), (1, 6, 7.0, 35.50),
(1, 7, 10.0, 28.00), (1, 8, 1.6, 22.00);

-- Factura 2
INSERT INTO detalle_factura VALUES
(2, 9, 1.0, 85.00), (2, 10, 2.0, 99.00), (2, 11, 0.5, 135.00),
(2, 12, 1.0, 135.00), (2, 13, 1.8, 7.00), (2, 14, 1.0, 39.00);

-- Factura 3
INSERT INTO detalle_factura VALUES
(3, 2, 3.0, 42.00), (3, 5, 2.0, 45.00), (3, 8, 2.5, 18.00),
(3, 13, 1.0, 17.00);

-- Factura 4
INSERT INTO detalle_factura VALUES
(4, 6, 5.0, 35.50), (4, 10, 1.5, 119.00), (4, 12, 1.0, 155.00),
(4, 14, 0.5, 53.00);

-- Factura 5
INSERT INTO detalle_factura VALUES
(5, 1, 2.0, 40.00), (5, 3, 1.5, 33.00), (5, 4, 0.5, 65.00),
(5, 7, 4.0, 12.00);

-- Factura 6 (cliente sin grupo)
INSERT INTO detalle_factura VALUES
(6, 15, 1.0, 60.00);

-- Compras simuladas
INSERT INTO compra (fecha_compra, id_producto, cantidad_compra, precio_unitario_compra) VALUES
('2025-05-01', 1, 10.0, 45.00), ('2025-05-10', 1, 8.0, 47.00),
('2025-05-01', 2, 15.0, 40.00), ('2025-05-10', 2, 12.0, 42.00),
('2025-05-01', 3, 20.0, 38.00), ('2025-05-10', 3, 18.0, 40.00),
('2025-05-01', 4, 5.0, 65.00),  ('2025-05-10', 4, 4.0, 68.00),
('2025-05-01', 5, 10.0, 40.00), ('2025-05-10', 5, 10.0, 42.00),
('2025-05-01', 6, 25.0, 28.00), ('2025-05-10', 6, 20.0, 29.00),
('2025-05-01', 7, 30.0, 22.00), ('2025-05-10', 7, 25.0, 24.00),
('2025-05-01', 8, 15.0, 15.00), ('2025-05-10', 8, 10.0, 16.00),
('2025-05-01', 9, 8.0, 85.00),  ('2025-05-10', 9, 5.0, 88.00),
('2025-05-01', 10, 5.0, 100.00),('2025-05-10', 10, 3.0, 105.00),
('2025-05-01', 11, 4.0, 130.00),('2025-05-10', 11, 3.0, 135.00),
('2025-05-01', 12, 6.0, 130.00),('2025-05-10', 12, 5.0, 132.00),
('2025-05-01', 13, 10.0, 15.00),('2025-05-10', 13, 8.0, 16.00),
('2025-05-01', 14, 8.0, 40.00), ('2025-05-10', 14, 6.0, 42.00),
('2025-05-01', 15, 6.0, 50.00), ('2025-05-10', 15, 5.0, 52.00);
