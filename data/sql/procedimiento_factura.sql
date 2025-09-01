USE disfruleg;

DELIMITER $$

DROP PROCEDURE IF EXISTS CrearFacturaCompleta$$

CREATE PROCEDURE CrearFacturaCompleta(
    IN p_id_cliente INT,
    IN p_items_json JSON,
    IN p_folio_personalizado INT,
    IN p_fecha_personalizada DATE
)
BEGIN
    DECLARE v_id_factura INT;
    DECLARE v_folio_numero INT;
    DECLARE v_total DECIMAL(10,2) DEFAULT 0;
    DECLARE v_item_count INT;
    DECLARE i INT DEFAULT 0;
    DECLARE v_id_producto INT;
    DECLARE v_cantidad DECIMAL(10,2);
    DECLARE v_precio_unitario DECIMAL(10,2);
    DECLARE v_subtotal DECIMAL(10,2);
    DECLARE v_nombre_producto VARCHAR(255);
    DECLARE v_current_stock DECIMAL(10,2);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- Obtener o generar folio
    IF p_folio_personalizado IS NOT NULL THEN
        SET v_folio_numero = p_folio_personalizado;
    ELSE
        -- Generar nuevo folio (usando AUTO_INCREMENT de la tabla factura)
        SELECT COALESCE(MAX(id_factura), 0) + 1 INTO v_folio_numero FROM factura;
    END IF;
    
    -- Crear la factura principal (sin las columnas total y estado que no existen)
    INSERT INTO factura (id_factura, fecha_factura, id_cliente)
    VALUES (
        v_folio_numero,
        COALESCE(p_fecha_personalizada, CURDATE()),
        p_id_cliente
    );
    
    SET v_id_factura = v_folio_numero;
    
    -- Procesar items JSON
    SET v_item_count = JSON_LENGTH(p_items_json);
    
    WHILE i < v_item_count DO
        -- Extraer datos del item
        SET v_nombre_producto = JSON_UNQUOTE(JSON_EXTRACT(p_items_json, CONCAT('$[', i, '].nombre')));
        SET v_cantidad = JSON_EXTRACT(p_items_json, CONCAT('$[', i, '].cantidad'));
        SET v_precio_unitario = JSON_EXTRACT(p_items_json, CONCAT('$[', i, '].precio_unitario'));
        SET v_subtotal = v_cantidad * v_precio_unitario;
        
        -- Obtener id_producto y validar stock
        SELECT id_producto, stock INTO v_id_producto, v_current_stock 
        FROM producto WHERE nombre_producto = v_nombre_producto;
        
        IF v_id_producto IS NOT NULL THEN
            -- Validar stock
            IF v_current_stock < v_cantidad THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = CONCAT('Stock insuficiente para: ', v_nombre_producto, 
                                        '. Disponible: ', v_current_stock, ', Solicitado: ', v_cantidad);
            END IF;
            
            -- Insertar detalle de factura
            INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta)
            VALUES (v_id_factura, v_id_producto, v_cantidad, v_precio_unitario);
            
            -- Actualizar stock manualmente
            UPDATE producto 
            SET stock = stock - v_cantidad
            WHERE id_producto = v_id_producto;
            
            SET v_total = v_total + v_subtotal;
        END IF;
        
        SET i = i + 1;
    END WHILE;
    
    -- NOTA: En tu esquema actual, la tabla factura no tiene columna 'total'
    -- El total se calcula dinámicamente desde los detalles
    
    COMMIT;
    
    -- Devolver resultados
    SELECT v_id_factura as id_factura, v_folio_numero as folio_numero, v_total as total;
END$$

DELIMITER ;