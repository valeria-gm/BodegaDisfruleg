import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Any, Optional
from decimal import Decimal
from ..models.receipt_models import ProductData, ClientData

class ProductManager:
    """Handles product operations and filtering"""
    
    def __init__(self, products: List[ProductData], client_data: Optional[ClientData] = None):
        self.all_products = products
        self.client_data = client_data
        self.filtered_products = products.copy()
    
    def update_client_data(self, client_data: ClientData):
        """Update client data for discount calculations"""
        self.client_data = client_data
    
    def filter_products(self, search_text: str) -> List[ProductData]:
        """Filter products by search text"""
        if not search_text:
            self.filtered_products = self.all_products.copy()
        else:
            search_lower = search_text.lower()
            self.filtered_products = [
                product for product in self.all_products
                if search_lower in product.nombre_producto.lower()
            ]
        return self.filtered_products
    
    def get_product_by_id(self, product_id: int) -> Optional[ProductData]:
        """Get product by ID"""
        return next((p for p in self.all_products if p.id_producto == product_id), None)
    
    def calculate_discounted_price(self, product: ProductData) -> Decimal:
        """Calculate price with client discount"""
        if not self.client_data:
            return product.precio_base
        
        discount_amount = product.precio_base * (self.client_data.descuento / 100)
        return product.precio_base - discount_amount
    
    def get_price_info(self, product: ProductData) -> Dict[str, Decimal]:
        """Get detailed price information for a product"""
        precio_base = product.precio_base
        descuento = self.client_data.descuento if self.client_data else Decimal('0')
        monto_descuento = precio_base * (descuento / 100)
        precio_final = precio_base - monto_descuento
        
        return {
            'precio_base': precio_base,
            'descuento': descuento,
            'monto_descuento': monto_descuento,
            'precio_final': precio_final
        }
    
    def is_special_product(self, product: ProductData) -> bool:
        """Check if product is special (requires admin access)"""
        return product.es_especial
    
    def format_product_name(self, product: ProductData) -> str:
        """Format product name with special indicator"""
        if product.es_especial:
            return f"🔒 {product.nombre_producto}"
        return product.nombre_producto
    
    def get_product_display_info(self, product: ProductData, in_cart: bool = False) -> Dict[str, Any]:
        """Get product information for display"""
        price_info = self.get_price_info(product)
        
        display_name = self.format_product_name(product)
        
        if in_cart:
            action_text = "✓ En carrito"
        else:
            action_text = "Doble-click para agregar"
        
        if product.es_especial:
            action_text = "ESPECIAL - " + action_text
        
        return {
            'nombre': display_name,
            'unidad': product.unidad_producto,
            'precio': f"${price_info['precio_final']:.2f}",
            'accion': action_text,
            'id_producto': product.id_producto
        }