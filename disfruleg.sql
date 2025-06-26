-- Crear base de datos
CREATE DATABASE IF NOT EXISTS disfruleg;
USE disfruleg;

-- Tabla GRUPO
CREATE TABLE grupo (
    id_grupo INT AUTO_INCREMENT PRIMARY KEY,
    clave_grupo VARCHAR(50) NOT NULL UNIQUE,
    descuento DECIMAL(5,2) NOT NULL DEFAULT 0.00 -- porcentaje (ej. 10.00 = 10%)
);

-- Tabla CLIENTE
CREATE TABLE cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cliente VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100),
    id_grupo INT,
    FOREIGN KEY (id_grupo) REFERENCES grupo(id_grupo)
);

-- Tabla PRODUCTO
CREATE TABLE producto (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre_producto VARCHAR(250) NOT NULL,
    unidad_producto VARCHAR(50) NOT NULL,
    stock DECIMAL(10,2) NOT NULL,
    es_especial BOOLEAN DEFAULT FALSE
);

-- Tabla PRECIO
CREATE TABLE precio (
    id_precio INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    id_grupo INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (id_grupo) REFERENCES grupo(id_grupo) ON DELETE CASCADE
);

-- Tabla FACTURA
CREATE TABLE factura (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    fecha_factura DATE NOT NULL,
    id_cliente INT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
);

-- Tabla DETALLE_FACTURA (sin subtotal generado)
CREATE TABLE detalle_factura (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_factura INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad_factura DECIMAL(10,2) NOT NULL,
    precio_unitario_venta DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_factura) REFERENCES factura(id_factura),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);

-- Tabla COMPRA
CREATE TABLE compra (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    fecha_compra DATE NOT NULL,
    id_producto INT NOT NULL,
    cantidad_compra DECIMAL(10,2) NOT NULL,
    precio_unitario_compra DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);

