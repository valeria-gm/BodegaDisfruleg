USE disfruleg;

-- Insertar tipos de cliente
INSERT INTO tipo_cliente (nombre_tipo, descripcion) VALUES
('Minorista', 'Clientes que compran pequeñas cantidades'),
('Mayorista', 'Clientes con compras al por mayor'),
('Distribuidor', 'Clientes con descuentos especiales por volumen');

-- Insertar grupos
INSERT INTO grupo (clave_grupo, descuento) VALUES 
('Grupo1', 5.00),        -- id_grupo = 1 
('Grupo2', 10.00),       -- id_grupo = 2 
('Grupo3', 20.00);       -- id_grupo = 3 

-- Insertar productos (sin precio_base)
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
('Tenedores', 'caja', 20, TRUE),
('Tequila', 'botella', 15, TRUE);

-- Insertar precios por tipo de cliente
-- Precios para Minoristas (tipo 1)
INSERT INTO precio_por_tipo (id_tipo_cliente, id_producto, precio) VALUES
(1, 1, 55.00), (1, 2, 49.00), (1, 3, 46.00),
(1, 4, 77.00), (1, 5, 49.00), (1, 6, 35.50),
(1, 7, 28.00), (1, 8, 22.00), (1, 9, 100.00),
(1, 10, 119.00), (1, 11, 155.00), (1, 12, 155.00),
(1, 13, 20.00), (1, 14, 53.00), (1, 15, 33.00),
(1, 16, 600.00);

-- Precios para Mayoristas (tipo 2)
INSERT INTO precio_por_tipo (id_tipo_cliente, id_producto, precio) VALUES
(2, 1, 45.00), (2, 2, 40.00), (2, 3, 38.00),
(2, 4, 65.00), (2, 5, 40.00), (2, 6, 30.00),
(2, 7, 24.00), (2, 8, 18.00), (2, 9, 85.00),
(2, 10, 100.00), (2, 11, 130.00), (2, 12, 130.00),
(2, 13, 16.00), (2, 14, 45.00), (2, 15, 28.00),
(2, 16, 550.00);

-- Precios para Distribuidores (tipo 3)
INSERT INTO precio_por_tipo (id_tipo_cliente, id_producto, precio) VALUES
(3, 1, 40.00), (3, 2, 35.00), (3, 3, 34.00),
(3, 4, 60.00), (3, 5, 35.00), (3, 6, 28.00),
(3, 7, 22.00), (3, 8, 16.00), (3, 9, 80.00),
(3, 10, 95.00), (3, 11, 125.00), (3, 12, 125.00),
(3, 13, 15.00), (3, 14, 42.00), (3, 15, 25.00),
(3, 16, 520.00);

-- Insertar clientes
INSERT INTO cliente (nombre_cliente, telefono, correo, id_grupo, id_tipo_cliente) VALUES
('Ana Pérez', '5551234567', 'ana.perez@example.com', 1, 1),  -- Minorista con Grupo1
('Luis Gómez', '5559876543', 'luis.gomez@example.com', 3, 2), -- Mayorista con Grupo3
('María López', '5551112222', NULL, 2, 1),                   -- Minorista con Grupo2
('Carlos Méndez', '5552223333', 'carlos.m@example.com', NULL, 3); -- Distribuidor sin grupo