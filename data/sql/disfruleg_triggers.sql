USE disfruleg;

-- Trigger para asignar folio único automático a órdenes
DELIMITER //
CREATE TRIGGER before_orden_insert
BEFORE INSERT ON ordenes_guardadas
FOR EACH ROW
BEGIN
    DECLARE next_folio INT;
    
    -- Si no se especifica folio, obtener el siguiente disponible
    IF NEW.folio_numero IS NULL THEN
        -- Obtener y actualizar el siguiente folio
        SELECT next_val INTO next_folio FROM folio_sequence FOR UPDATE;
        SET NEW.folio_numero = next_folio;
        UPDATE folio_sequence SET next_val = next_val + 1;
    END IF;
END //
DELIMITER ;

-- Trigger para registrar deuda automáticamente al crear factura
DELIMITER //
CREATE TRIGGER after_factura_insert
AFTER INSERT ON factura
FOR EACH ROW
BEGIN
    -- Calcular el total de la factura
    DECLARE total_factura DECIMAL(10,2);
    
    -- Usar un pequeño delay para asegurar que los detalles se hayan insertado
    SELECT SUM(cantidad_factura * precio_unitario_venta) INTO total_factura
    FROM detalle_factura
    WHERE id_factura = NEW.id_factura;
    
    -- Solo insertar deuda si hay un total calculado
    IF total_factura IS NOT NULL AND total_factura > 0 THEN
        -- Insertar la deuda
        INSERT INTO deuda (id_cliente, id_factura, monto, fecha_generada, monto_pagado, pagado, descripcion)
        VALUES (NEW.id_cliente, NEW.id_factura, total_factura, CURDATE(), 0.00, FALSE,
                CONCAT('Deuda por factura #', NEW.id_factura));
    END IF;
END //
DELIMITER ;

-- Trigger para evitar modificación de órdenes registradas
DELIMITER //
CREATE TRIGGER before_orden_update
BEFORE UPDATE ON ordenes_guardadas
FOR EACH ROW
BEGIN
    IF OLD.estado = 'registrada' AND NEW.estado != OLD.estado THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'No se puede modificar una orden ya registrada';
    END IF;
    
    -- Actualizar automáticamente la fecha de modificación
    SET NEW.fecha_modificacion = CURRENT_TIMESTAMP;
END //
DELIMITER ;

-- Trigger para actualizar stock al registrar compras
DELIMITER //
CREATE TRIGGER after_compra_insert
AFTER INSERT ON compra
FOR EACH ROW
BEGIN
    UPDATE producto 
    SET stock = stock + NEW.cantidad_compra
    WHERE id_producto = NEW.id_producto;
END //
DELIMITER ;

-- Trigger para actualizar stock al registrar ventas
DELIMITER //
CREATE TRIGGER after_detalle_factura_insert
AFTER INSERT ON detalle_factura
FOR EACH ROW
BEGIN
    UPDATE producto 
    SET stock = stock - NEW.cantidad_factura
    WHERE id_producto = NEW.id_producto;
END //
DELIMITER ;

-- Trigger para validar stock antes de vender (CORREGIDO)
DELIMITER //
CREATE TRIGGER before_detalle_factura_insert
BEFORE INSERT ON detalle_factura
FOR EACH ROW
BEGIN
    DECLARE current_stock DECIMAL(10,2);
    DECLARE producto_nombre VARCHAR(250);
    DECLARE mensaje_error TEXT;
    
    SELECT stock, nombre_producto INTO current_stock, producto_nombre
    FROM producto 
    WHERE id_producto = NEW.id_producto;
    
    IF current_stock < NEW.cantidad_factura THEN
        SET mensaje_error = CONCAT('Stock insuficiente para el producto: ', producto_nombre, 
                                  '. Stock disponible: ', current_stock, 
                                  ', Cantidad solicitada: ', NEW.cantidad_factura);
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = mensaje_error;
    END IF;
END //
DELIMITER ;

-- Trigger para validar eliminación de órdenes activas
DELIMITER //
CREATE TRIGGER before_orden_delete
BEFORE DELETE ON ordenes_guardadas
FOR EACH ROW
BEGIN
    -- Prevenir eliminación física de órdenes registradas
    IF OLD.estado = 'registrada' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'No se pueden eliminar órdenes registradas. Use soft delete (activo = FALSE)';
    END IF;
END //
DELIMITER ;

-- Trigger para validar datos de carrito JSON antes de insertar (CORREGIDO)
DELIMITER //
CREATE TRIGGER before_orden_insert_validate
BEFORE INSERT ON ordenes_guardadas
FOR EACH ROW
BEGIN
    DECLARE mensaje_error TEXT;
    
    -- Validar que datos_carrito sea JSON válido
    IF NOT JSON_VALID(NEW.datos_carrito) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Los datos del carrito deben ser un JSON válido';
    END IF;
    
    -- Validar que el total estimado sea positivo
    IF NEW.total_estimado <= 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'El total estimado debe ser mayor que cero';
    END IF;
    
    -- Asegurar que el usuario existe
    IF NOT EXISTS (SELECT 1 FROM usuarios_sistema WHERE username = NEW.usuario_creador AND activo = TRUE) THEN
        SET mensaje_error = CONCAT('Usuario no válido: ', NEW.usuario_creador);
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = mensaje_error;
    END IF;
END //
DELIMITER ;