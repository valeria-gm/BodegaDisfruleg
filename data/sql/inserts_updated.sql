USE disfruleg;

-- Insertar tipos de cliente
INSERT INTO tipo_cliente (nombre_tipo, descuento) VALUES
('Tipo1', 15.00),
('Tipo2', 0.00);

-- Insertar grupos con relación a tipos de cliente
INSERT INTO grupo (clave_grupo, descripcion, id_tipo_cliente) VALUES 
('Aeropuerto', 'Clientes del área aeroportuaria', 1),    -- Tipo1 (15%)
('Mrl', 'Grupo Miraflores', 2),                         -- Tipo2 (0%)
('Salerosa', 'Grupo Salerosa', 2),                      -- Tipo2 (0%)
('Bocanegra', 'Grupo Bocanegra', 1),                    -- Tipo1 (15%)
('General', 'Clientes generales', 2),                   -- Tipo2 (0%)
('3M', 'Clientes mayoristas', 1),                       -- Tipo1 (15%)
('Especial', 'Clientes especiales VIP', 1);             -- Tipo1 (15%)

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
('Tequila', 'botella', 15, TRUE),
('Aguacate', 'kg', 120, FALSE),
('Cebolla blanca', 'kg', 180, FALSE),
('Limón', 'kg', 90, FALSE),
('Cilantro', 'manojo', 70, FALSE);

-- Insertar precios por Grupo de cliente
-- Precios para Aeropuerto (id_grupo = 1) - Tipo1 (15% descuento)
INSERT INTO precio_por_grupo (id_grupo, id_producto, precio_base) VALUES
(1, 1, 55.00), (1, 2, 49.00), (1, 3, 46.00), (1, 4, 77.00), (1, 5, 49.00),
(1, 6, 35.50), (1, 7, 28.00), (1, 8, 22.00), (1, 9, 100.00), (1, 10, 119.00),
(1, 11, 155.00), (1, 12, 155.00), (1, 13, 20.00), (1, 14, 53.00), (1, 15, 33.00),
(1, 16, 600.00), (1, 17, 65.00), (1, 18, 32.00), (1, 19, 45.00), (1, 20, 25.00);

-- Precios para Mrl (id_grupo = 2) - Tipo2 (sin descuento)
INSERT INTO precio_por_grupo (id_grupo, id_producto, precio_base) VALUES
(2, 1, 45.00), (2, 2, 40.00), (2, 3, 38.00), (2, 4, 65.00), (2, 5, 40.00),
(2, 6, 30.00), (2, 7, 24.00), (2, 8, 18.00), (2, 9, 85.00), (2, 10, 100.00),
(2, 11, 130.00), (2, 12, 130.00), (2, 13, 16.00), (2, 14, 45.00), (2, 15, 28.00),
(2, 16, 550.00), (2, 17, 55.00), (2, 18, 28.00), (2, 19, 38.00), (2, 20, 22.00);

-- Precios para Salerosa (id_grupo = 3) - Tipo2 (sin descuento)
INSERT INTO precio_por_grupo (id_grupo, id_producto, precio_base) VALUES
(3, 1, 40.00), (3, 2, 35.00), (3, 3, 34.00), (3, 4, 60.00), (3, 5, 35.00),
(3, 6, 28.00), (3, 7, 22.00), (3, 8, 16.00), (3, 9, 80.00), (3, 10, 95.00),
(3, 11, 125.00), (3, 12, 125.00), (3, 13, 15.00), (3, 14, 42.00), (3, 15, 25.00),
(3, 16, 520.00), (3, 17, 50.00), (3, 18, 25.00), (3, 19, 35.00), (3, 20, 20.00);

-- Precios para Bocanegra (id_grupo = 4) - Tipo1 (15% descuento)
INSERT INTO precio_por_grupo (id_grupo, id_producto, precio_base) VALUES
(4, 1, 45.00), (4, 2, 45.00), (4, 3, 44.00), (4, 4, 65.00), (4, 5, 45.00),
(4, 6, 38.00), (4, 7, 32.00), (4, 8, 26.00), (4, 9, 85.00), (4, 10, 105.00),
(4, 11, 135.00), (4, 12, 135.00), (4, 13, 25.00), (4, 14, 45.00), (4, 15, 35.00),
(4, 16, 620.00), (4, 17, 58.00), (4, 18, 30.00), (4, 19, 42.00), (4, 20, 24.00);

-- Precios para General (id_grupo = 5) - Tipo2 (sin descuento)
INSERT INTO precio_por_grupo (id_grupo, id_producto, precio_base) VALUES
(5, 1, 50.00), (5, 2, 45.00), (5, 3, 44.00), (5, 4, 70.00), (5, 5, 45.00),
(5, 6, 38.00), (5, 7, 32.00), (5, 8, 26.00), (5, 9, 90.00), (5, 10, 105.00),
(5, 11, 135.00), (5, 12, 135.00), (5, 13, 25.00), (5, 14, 52.00), (5, 15, 35.00),
(5, 16, 620.00), (5, 17, 60.00), (5, 18, 32.00), (5, 19, 40.00), (5, 20, 25.00);

-- Precios para 3M (id_grupo = 6) - Tipo1 (15% descuento)
INSERT INTO precio_por_grupo (id_grupo, id_producto, precio_base) VALUES
(6, 1, 30.00), (6, 2, 25.00), (6, 3, 24.00), (6, 4, 50.00), (6, 5, 25.00),
(6, 6, 18.00), (6, 7, 12.00), (6, 8, 16.00), (6, 9, 70.00), (6, 10, 85.00),
(6, 11, 105.00), (6, 12, 115.00), (6, 13, 15.00), (6, 14, 32.00), (6, 15, 15.00),
(6, 16, 520.00), (6, 17, 45.00), (6, 18, 20.00), (6, 19, 30.00), (6, 20, 18.00);

-- Precios para Especial (id_grupo = 7) - Tipo1 (15% descuento)
INSERT INTO precio_por_grupo (id_grupo, id_producto, precio_base) VALUES
(7, 1, 33.00), (7, 2, 23.00), (7, 3, 23.00), (7, 4, 53.00), (7, 5, 23.00),
(7, 6, 13.00), (7, 7, 13.00), (7, 8, 13.00), (7, 9, 73.00), (7, 10, 83.00),
(7, 11, 103.00), (7, 12, 113.00), (7, 13, 13.00), (7, 14, 33.00), (7, 15, 13.00),
(7, 16, 523.00), (7, 17, 43.00), (7, 18, 18.00), (7, 19, 28.00), (7, 20, 16.00);

-- Insertar clientes 
INSERT INTO cliente (nombre_cliente, telefono, correo, id_grupo) VALUES
-- Grupo Aeropuerto (id_grupo = 1) - Tipo1 15%
('Sabores del Alma', '5551111111', 'contacto@saboresdelalma.com', 1),
('La Mesa Secreta', '5551111112', 'reservas@lamesasecreta.com', 1),
('Bistró del Vuelo', '5551111113', 'info@bistrodelvuelo.com', 1),

-- Grupo Mrl (id_grupo = 2) - Tipo2 0%
('Fuego & Brasa', '5552222221', 'info@fuegoybrasa.com', 2),
('El Jardín de los Platos', '5552222222', 'contacto@jardinplatos.com', 2),
('Cocina Miraflores', '5552222223', 'reservas@cocinamiraflores.com', 2),

-- Grupo Salerosa (id_grupo = 3) - Tipo2 0%
('Tinto & Trufa', '5553333331', 'reservas@tintoytrufa.com', 3),
('Sazón Nómada', '5553333332', 'hola@sazonnomada.com', 3),
('Delicias Salerosa', '5553333333', 'contacto@deliciassalerosa.com', 3),

-- Grupo Bocanegra (id_grupo = 4) - Tipo1 15%
('Cuchara Urbana', '5554444441', 'info@cucharaurbana.com', 4),
('Lumbre Cocina Viva', '5554444442', 'lumbre@cocinaviva.com', 4),
('Aromas Bocanegra', '5554444443', 'reservas@aromasbocanegra.com', 4),

-- Grupo General (id_grupo = 5) - Tipo2 0%
('Casa Mar & Tierra', '5555555551', 'contact@casamartierra.com', 5),
('Origen Ancestral', '5555555552', 'hola@origenancestral.com', 5),
('Tradición Culinaria', '5555555553', 'info@tradicionculinaria.com', 5),

-- Grupo 3M (id_grupo = 6) - Tipo1 15%
('Albahaca y Olivo', '5556666661', 'info@albahacayolivo.com', 6),
('Brío Bistrô', '5556666662', 'reservas@briobistro.com', 6),
('Mayorista Gourmet', '5556666663', 'ventas@mayoiristagourmet.com', 6),

-- Grupo Especial (id_grupo = 7) - Tipo1 15%
('Manjar Moderno', '5557777771', 'contacto@manjarmoderno.com', 7),
('Sabor Sagrado', '5557777772', 'info@saborsagrado.com', 7),
('Bocado Oculto', '5557777773', 'reservas@bocadooculto.com', 7),
('Elite Gastronómico', '5557777774', 'vip@elitegastronomico.com', 7);

-- Insertar algunas compras de ejemplo para tener historial de costos
INSERT INTO compra (fecha_compra, id_producto, cantidad_compra, precio_unitario_compra) VALUES
('2024-01-15', 1, 50, 25.00),  -- Col morado
('2024-01-15', 2, 100, 35.00), -- Huevo
('2024-01-15', 3, 75, 20.00),  -- Jitomate bola
('2024-01-15', 4, 40, 45.00),  -- Chile habanero
('2024-01-15', 5, 45, 18.00),  -- Rábano rojo
('2024-01-15', 6, 150, 22.00), -- Frijol
('2024-01-15', 7, 125, 15.00), -- Jitomate
('2024-01-15', 8, 30, 12.00),  -- Apio
('2024-01-15', 9, 20, 65.00),  -- Chorizo
('2024-01-15', 10, 25, 85.00), -- Bistec de puerco
('2024-01-20', 11, 25, 110.00), -- Tocino
('2024-01-20', 12, 35, 120.00), -- Queso Oaxaca
('2024-01-20', 13, 15, 12.00),  -- Sandía
('2024-01-20', 14, 10, 35.00),  -- Frambuesa
('2024-01-20', 15, 10, 18.00),  -- Tenedores
('2024-01-20', 16, 8, 450.00),  -- Tequila
('2024-01-25', 17, 60, 35.00),  -- Aguacate
('2024-01-25', 18, 90, 18.00),  -- Cebolla blanca
('2024-01-25', 19, 45, 25.00),  -- Limón
('2024-01-25', 20, 35, 12.00);  -- Cilantro

-- Insertar el valor inicial para la secuencia de folios
INSERT INTO folio_sequence (id, next_val) VALUES (1, 1)
ON DUPLICATE KEY UPDATE next_val = GREATEST(next_val, 1);