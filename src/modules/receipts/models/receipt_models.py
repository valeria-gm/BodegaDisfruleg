from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional, Any

@dataclass
class ProductData:
    """Data model for product information"""
    id_producto: int
    nombre_producto: str
    unidad_producto: str
    precio_base: Decimal
    es_especial: bool = False

@dataclass
class ClientData:
    """Data model for client information"""
    id_cliente: int
    nombre_cliente: str
    id_grupo: Optional[int]
    descuento: Decimal = Decimal('0')

@dataclass
class CartItem:
    """Data model for shopping cart items"""
    producto: ProductData
    cantidad: Decimal
    precio_base: float
    precio_final: float
    monto_descuento: float
    
    @property
    def subtotal(self) -> Decimal:
        return self.cantidad * Decimal(str(self.precio_final))

@dataclass
class ReceiptData:
    """Data model for receipt information"""
    cliente: ClientData
    productos: List[CartItem]
    total: Decimal
    fecha: str
    
    @property
    def total_items(self) -> int:
        return len(self.productos)