-- Crear tablas para el manejo de secciones en facturas
USE disfruleg;

-- Tabla para almacenar secciones de factura
CREATE TABLE IF NOT EXISTS seccion_factura (
    id_seccion INT AUTO_INCREMENT PRIMARY KEY,
    id_factura INT NOT NULL,
    nombre_seccion VARCHAR(100) NOT NULL,
    orden_seccion INT NOT NULL DEFAULT 0,
    FOREIGN KEY (id_factura) REFERENCES factura(id_factura) ON DELETE CASCADE,
    INDEX idx_factura_seccion (id_factura)
);

-- Modificar tabla detalle_factura para incluir sección
ALTER TABLE detalle_factura 
ADD COLUMN id_seccion INT NULL,
ADD FOREIGN KEY (id_seccion) REFERENCES seccion_factura(id_seccion) ON DELETE SET NULL;

-- Crear índice para mejor rendimiento
CREATE INDEX idx_detalle_seccion ON detalle_factura(id_seccion);

-- Tabla para metadatos de facturas seccionales
CREATE TABLE IF NOT EXISTS factura_metadata (
    id_factura INT PRIMARY KEY,
    usa_secciones BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_factura) REFERENCES factura(id_factura) ON DELETE CASCADE
);