from dataclasses import dataclass, field
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
    id_grupo: int  # Now mandatory - all clients must have a group
    id_tipo_cliente: int  # Now mandatory - all clients must have a type
    descuento: Decimal = Decimal('0')
    
    def __post_init__(self):
        """Validate that all required fields are present"""
        if self.id_tipo_cliente is None:
            raise ValueError(f"Client {self.nombre_cliente} must have a type assigned")
        if self.id_grupo is None:
            raise ValueError(f"Client {self.nombre_cliente} must have a group assigned")

@dataclass
class CartItem:
    """Data model for shopping cart items"""
    producto: ProductData
    cantidad: Decimal
    precio_base: float
    precio_final: float
    monto_descuento: float
    section_id: Optional[str] = None  # Add section support
    
    @property
    def subtotal(self) -> Decimal:
        return self.cantidad * Decimal(str(self.precio_final))

@dataclass
class InvoiceSection:
    """Data model for invoice sections"""
    id: str
    name: str
    items: List[CartItem] = field(default_factory=list)
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate section subtotal"""
        return sum(item.subtotal for item in self.items)
    
    @property
    def item_count(self) -> int:
        """Get number of items in section"""
        return len(self.items)

@dataclass
class ReceiptData:
    """Data model for receipt information"""
    cliente: ClientData
    productos: List[CartItem]
    total: Decimal
    fecha: str
    sections: Optional[List[InvoiceSection]] = None  # Add sections support
    
    @property
    def total_items(self) -> int:
        return len(self.productos)
    
    @property
    def is_sectioned(self) -> bool:
        """Check if receipt uses sections"""
        return self.sections is not None and len(self.sections) > 0