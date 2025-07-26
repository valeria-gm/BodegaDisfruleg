USE disfruleg;

CREATE TABLE IF NOT EXISTS ordenes_guardadas (
    id_orden INT AUTO_INCREMENT PRIMARY KEY,  
    folio_numero INT UNIQUE NOT NULL,         -- Folio reservado (único en el sistema)
    id_cliente INT NOT NULL,                  
    usuario_creador VARCHAR(50) NOT NULL,     -- Usuario que creó la orden
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    estado ENUM('guardada', 'registrada') DEFAULT 'guardada', 
    datos_carrito JSON NOT NULL,              -- Carrito (items, cantidades, secciones, etc.)
    total_estimado DECIMAL(10,2) NOT NULL,    
    activo BOOLEAN DEFAULT TRUE,              -- Para soft delete

    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
    FOREIGN KEY (usuario_creador) REFERENCES usuarios_sistema(username)
);


CREATE INDEX idx_estado_activo ON ordenes_guardadas(estado, activo);
CREATE INDEX idx_usuario ON ordenes_guardadas(usuario_creador);
