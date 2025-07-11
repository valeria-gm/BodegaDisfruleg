-- Crear base de datos
CREATE DATABASE IF NOT EXISTS disfruleg;
USE disfruleg;

-- Tabla TIPO_CLIENTE (define categorías de clientes)
CREATE TABLE tipo_cliente (
    id_tipo_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre_tipo VARCHAR(100) NOT NULL UNIQUE,
    descuento DECIMAL(5,2) NOT NULL DEFAULT 0.00 CHECK (descuento BETWEEN 0 AND 100)-- porcentaje (ej. 10.00 = 10%)
);

-- Tabla GRUPO (para descuentos)
CREATE TABLE grupo (
    id_grupo INT AUTO_INCREMENT PRIMARY KEY,
    clave_grupo VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255) -- Opcional
);

-- Tabla CLIENTE
CREATE TABLE cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cliente VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100),
    id_grupo INT NOT NULL, -- Obligatorio
    id_tipo_cliente INT NOT NULL, -- Obligatorio
    FOREIGN KEY (id_grupo) REFERENCES grupo(id_grupo),
    FOREIGN KEY (id_tipo_cliente) REFERENCES tipo_cliente(id_tipo_cliente)
);

-- Tabla PRODUCTO (sin precio_base)
CREATE TABLE producto (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre_producto VARCHAR(250) NOT NULL,
    unidad_producto VARCHAR(50) NOT NULL,
    stock DECIMAL(10,2) NOT NULL,
    es_especial BOOLEAN DEFAULT FALSE
);

-- Tabla PRECIO_POR_GRUPO (precios específicos por Grupo de cliente)
CREATE TABLE precio_por_grupo (
    id_precio_grupo INT AUTO_INCREMENT PRIMARY KEY,
    id_grupo INT NOT NULL,
    id_producto INT NOT NULL,
    precio_base DECIMAL(10,2) NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_grupo) REFERENCES grupo(id_grupo),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto),
    UNIQUE KEY (id_grupo, id_producto) -- Cada combinación grupo-producto es única
);

-- Tabla FACTURA
CREATE TABLE factura (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    fecha_factura DATE NOT NULL,
    id_cliente INT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
);

-- Tabla DETALLE_FACTURA
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

-- Tabla de deudas
CREATE TABLE deuda (
    id_deuda INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_factura INT NOT NULL UNIQUE, -- Una factura solo genera una deuda
    monto DECIMAL(10,2) NOT NULL,
    fecha_generada DATE NOT NULL,
    pagado BOOLEAN DEFAULT FALSE,
    fecha_pago DATE NULL,
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
    FOREIGN KEY (id_factura) REFERENCES factura(id_factura)
);

-- Tabla de usuarios
CREATE TABLE usuarios_sistema (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    rol ENUM('admin', 'usuario') DEFAULT 'usuario',
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP NULL,
    intentos_fallidos INT DEFAULT 0,
    bloqueado_hasta TIMESTAMP NULL
);

-- Tabla de logs
CREATE TABLE log_accesos (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NULL,
    username_intento VARCHAR(50),
    ip_address VARCHAR(45) DEFAULT 'localhost',
    exito BOOLEAN,
    fecha_intento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detalle VARCHAR(255),
    FOREIGN KEY (id_usuario) REFERENCES usuarios_sistema(id_usuario) ON DELETE SET NULL
);

-- Índices
CREATE INDEX idx_username ON usuarios_sistema(username);
CREATE INDEX idx_activo ON usuarios_sistema(activo);
