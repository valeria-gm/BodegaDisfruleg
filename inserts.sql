-- Insertar grupos
INSERT INTO grupo (clave_grupo, descuento) VALUES 
('Grupo1', 5.00),        -- id_grupo = 1 
('Grupo2', 10.00),       -- id_grupo = 2 
('Grupo3', 20.00);       -- id_grupo = 3 

-- Insertar clientes
INSERT INTO cliente (nombre_cliente, telefono, correo, id_grupo) VALUES
('Ana Pérez', '5551234567', 'ana.perez@example.com', 1),
('Luis Gómez', '5559876543', 'luis.gomez@example.com', 3),
('María López', '5551112222', NULL, 2),
('Carlos Méndez', '5552223333', 'carlos.m@example.com', NULL); -- sin grupo

-- Insertar productos (con precio_base)
INSERT INTO producto (nombre_producto, unidad_producto, stock, es_especial, precio_base) VALUES
('Col morado', 'pz', 100, FALSE, 55.00),
('Huevo', 'kg', 200, FALSE, 49.00),
('Jitomate bola', 'kg', 150, FALSE, 46.00),
('Chile habanero', 'kg', 80, FALSE, 77.00),
('Rábano rojo', 'manojo', 90, FALSE, 49.00),
('Frijol', 'kg', 300, FALSE, 35.50),
('Jitomate', 'kg', 250, FALSE, 28.00),
('Apio', 'pz', 60, FALSE, 22.00),
('Chorizo', 'kg', 40, FALSE, 100.00),
('Bistec de puerco', 'kg', 45, FALSE, 119.00),
('Tocino', 'kg', 50, FALSE, 155.00),
('Queso Oaxaca', 'kg', 70, FALSE, 155.00),
('Sandía', 'pz', 30, FALSE, 20.00),
('Frambuesa', 'caja', 20, FALSE, 53.00),
('Tenedores', 'caja', 20, TRUE, 33.00),
('Tequila', 'botella', 15, TRUE, 600.00);



-- Facturas
INSERT INTO factura (fecha_factura, id_cliente) VALUES
('2025-04-27', 1),  
('2025-04-27', 2),  
('2025-05-02', 3),  
('2025-05-03', 1),
('2025-05-04', 2),
('2025-05-06', 4);  -- (sin grupo, 0%)

-- Detalles de factura 1 (Grupo1 - 5%)
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
(1, 1, 1.0, 55.00), (1, 2, 0.5, 49.00), (1, 3, 2.0, 46.00),
(1, 4, 0.25, 77.00), (1, 5, 1.0, 49.00), (1, 6, 7.0, 35.50),
(1, 7, 10.0, 28.00), (1, 8, 1.6, 22.00);

-- Detalles de factura 2 (Grupo3 - 20%)
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
(2, 9, 1.0, 80.00), (2, 10, 2.0, 95.20), (2, 11, 0.5, 124.00),
(2, 12, 1.0, 124.00), (2, 13, 1.8, 16.00), (2, 14, 1.0, 42.40);

-- Factura 3 (Grupo2 - 10%)
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
(3, 2, 3.0, 44.10), (3, 5, 2.0, 44.10), (3, 8, 2.5, 19.80),
(3, 13, 1.0, 18.00);

-- Factura 4 (Grupo1 - 5%)
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
(4, 6, 5.0, 35.50), (4, 10, 1.5, 119.00), (4, 12, 1.0, 155.00),
(4, 14, 0.5, 53.00);

-- Factura 5 (Grupo3 - 20%)
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
(5, 1, 2.0, 44.00), (5, 3, 1.5, 36.80), (5, 4, 0.5, 61.60),
(5, 7, 4.0, 22.40);

-- Factura 6 (sin grupo - sin descuento)
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta) VALUES
(6, 15, 1.0, 33.00);

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
