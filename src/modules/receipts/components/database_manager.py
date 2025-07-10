import mysql.connector
from datetime import datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal
from src.database.conexion import conectar
from ..models.receipt_models import ClientData, ProductData

class DatabaseManager:
    """Handles database operations for receipts"""
    
    def __init__(self):
        self.conn = conectar()
        self.cursor = self.conn.cursor(dictionary=True)
    
    def get_clients(self) -> List[ClientData]:
        """Get all clients with their group discount information"""
        query = """
            SELECT c.id_cliente, c.nombre_cliente, c.id_grupo, g.descuento 
            FROM cliente c
            LEFT JOIN grupo g ON c.id_grupo = g.id_grupo
        """
        self.cursor.execute(query)
        clients_data = self.cursor.fetchall()
        
        clients = []
        for client_data in clients_data:
            clients.append(ClientData(
                id_cliente=client_data['id_cliente'],
                nombre_cliente=client_data['nombre_cliente'],
                id_grupo=client_data['id_grupo'],
                descuento=Decimal(str(client_data['descuento'])) if client_data['descuento'] else Decimal('0')
            ))
        
        return clients
    
    def get_products(self) -> List[ProductData]:
        """Get all products including special ones"""
        query = """
            SELECT p.id_producto, p.nombre_producto, p.unidad_producto, 
                   p.precio_base, p.es_especial
            FROM producto p
            ORDER BY p.es_especial ASC, p.nombre_producto ASC
        """
        self.cursor.execute(query)
        products_data = self.cursor.fetchall()
        
        products = []
        for product_data in products_data:
            products.append(ProductData(
                id_producto=product_data['id_producto'],
                nombre_producto=product_data['nombre_producto'],
                unidad_producto=product_data['unidad_producto'],
                precio_base=Decimal(str(product_data['precio_base'])),
                es_especial=bool(product_data['es_especial'])
            ))
        
        return products
    
    def save_invoice(self, client_id: int, products_data: List[Dict[str, Any]]) -> Optional[int]:
        """Save invoice to database"""
        try:
            # Clear any pending results
            while self.cursor.nextset():
                pass
                
            self.cursor.execute("START TRANSACTION")
            
            # Insert invoice
            self.cursor.execute(
                "INSERT INTO factura (fecha_factura, id_cliente) VALUES (%s, %s)",
                (datetime.now().strftime('%Y-%m-%d'), client_id)
            )
            invoice_id = self.cursor.lastrowid
            
            # Insert invoice details
            for item in products_data:
                if isinstance(item, dict):
                    id_producto = item['producto']['id_producto']
                    cantidad = item['cantidad']
                    precio = item['precio_final']
                else:
                    id_producto = item[0]
                    cantidad = item[1]
                    precio = item[3]

                self.cursor.execute(
                    """INSERT INTO detalle_factura 
                    (id_factura, id_producto, cantidad_factura, precio_unitario_venta) 
                     VALUES (%s, %s, %s, %s)""",
                    (invoice_id, id_producto, float(cantidad), float(precio))
                )
            
            self.conn.commit()
            return invoice_id
        
        except mysql.connector.Error as err:
            self.conn.rollback()
            raise Exception(f"Database error: {err}")
        
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Unexpected error: {str(e)}")
        
        finally:
            try:
                while self.cursor.nextset():
                    pass
            except:
                pass
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()