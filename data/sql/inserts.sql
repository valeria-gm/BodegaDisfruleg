USE disfruleg;

-- Insertar tipos de cliente
INSERT INTO tipo_cliente (nombre_tipo, descuento) VALUES
('Tipo1', 15.00),
('Tipo2', 0.00 );

-- Insertar grupos
INSERT INTO grupo (clave_grupo, descripcion) VALUES 
('Aeropuerto', NULL),    
('Mrl', NULL),          
('Salerosa', NULL),     
('Bocanegra', NULL),
('General', NULL),
('3M', NULL),
('Especial', NULL);

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

-- Insertar precios por Grupo de cliente
-- Precios para Aeropuerto
INSERT INTO precio_por_grupo (id_grupo, id_producto, precio_base) VALUES
(1, 1, 55.00), (1, 2, 49.00), (1, 3, 46.00),
(1, 4, 77.00), (1, 5, 49.00), (1, 6, 35.50),
(1, 7, 28.00), (1, 8, 22.00), (1, 9, 100.00),
(1, 10, 119.00), (1, 11, 155.00), (1, 12, 155.00),
(1, 13, 20.00), (1, 14, 53.00), (1, 15, 33.00),
(1, 16, 600.00);

-- Precios para Mrl
INSERT INTO precio_por_grupo (id_grupo, id_producto, precio_base) VALUES
(2, 1, 45.00), (2, 2, 40.00), (2, 3, 38.00),
(2, 4, 65.00), (2, 5, 40.00), (2, 6, 30.00),
(2, 7, 24.00), (2, 8, 18.00), (2, 9, 85.00),
(2, 10, 100.00), (2, 11, 130.00), (2, 12, 130.00),
(2, 13, 16.00), (2, 14, 45.00), (2, 15, 28.00),
(2, 16, 550.00);

-- Precios para Salerosa
INSERT INTO precio_por_grupo (id_grupo, id_producto, precio_base) VALUES
(3, 1, 40.00), (3, 2, 35.00), (3, 3, 34.00),
(3, 4, 60.00), (3, 5, 35.00), (3, 6, 28.00),
(3, 7, 22.00), (3, 8, 16.00), (3, 9, 80.00),
(3, 10, 95.00), (3, 11, 125.00), (3, 12, 125.00),
(3, 13, 15.00), (3, 14, 42.00), (3, 15, 25.00),
(3, 16, 520.00);

-- Precios para Bocanegra
INSERT INTO precio_por_grupo (id_grupo, id_producto, precio_base) VALUES
(4, 1, 45.00), (4, 2, 45.00), (4, 3, 44.00),
(4, 4, 65.00), (4, 5, 45.00), (4, 6, 38.00),
(4, 7, 32.00), (4, 8, 26.00), (4, 9, 85.00),
(4, 10, 105.00), (4, 11, 135.00), (4, 12, 135.00),
(4, 13, 25.00), (4, 14, 45.00), (4, 15, 35.00),
(4, 16, 620.00);

-- Precios para General
INSERT INTO precio_por_grupo (id_grupo, id_producto, precio_base) VALUES
(5, 1, 50.00), (5, 2, 45.00), (5, 3, 44.00),
(5, 4, 70.00), (5, 5, 45.00), (5, 6, 38.00),
(5, 7, 32.00), (5, 8, 26.00), (5, 9, 90.00),
(5, 10, 105.00), (5, 11, 135.00), (5, 12, 135.00),
(5, 13, 25.00), (5, 14, 52.00), (5, 15, 35.00),
(5, 16, 620.00);

-- Precios para 3M
INSERT INTO precio_por_grupo (id_grupo, id_producto, precio_base) VALUES
(6, 1, 30.00), (6, 2, 25.00), (6, 3, 24.00),
(6, 4, 50.00), (6, 5, 25.00), (6, 6, 18.00),
(6, 7, 12.00), (6, 8, 16.00), (6, 9, 70.00),
(6, 10, 85.00), (6, 11, 105.00), (6, 12, 115.00),
(6, 13, 15.00), (6, 14, 32.00), (6, 15, 15.00),
(6, 16, 520.00);

-- Precios para Especial
INSERT INTO precio_por_grupo (id_grupo, id_producto, precio_base) VALUES
(7, 1, 33.00), (7, 2, 23.00), (7, 3, 23.00),
(7, 4, 53.00), (7, 5, 23.00), (7, 6, 13.00),
(7, 7, 13.00), (7, 8, 13.00), (7, 9, 73.00),
(7, 10, 83.00), (7, 11, 103.00), (7, 12, 113.00),
(7, 13, 13.00), (7, 14, 33.00), (7, 15, 13.00),
(7, 16, 523.00);

-- Insertar clientes
INSERT INTO cliente (nombre_cliente, telefono, correo, id_grupo, id_tipo_cliente) VALUES
('Restaurante 1', '5551234567', 'ana.perez@example.com', 1, 1),  
('Restaurante 2', '5559876543', 'luis.gomez@example.com', 3, 2), 
('Restaurante 3', '5551112222', NULL, 2, 2),                   
('Restaurante 4', '5552223333', 'carlos.m@example.com', 5, 2); 