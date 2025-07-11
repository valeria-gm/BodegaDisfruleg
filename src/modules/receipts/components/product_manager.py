import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Any, Optional
from decimal import Decimal
from ..models.receipt_models import ProductData, ClientData

class ProductManager:
    """Handles product operations and filtering"""
    
    def __init__(self, products: List[ProductData], client_data: Optional[ClientData] = None, db_manager=None):
        self.all_products = products
        self.client_data = client_data
        self.filtered_products = products.copy()
        self.db_manager = db_manager
        self._price_cache = {}  # Cache for prices to avoid repeated DB queries
    
    def update_client_data(self, client_data: ClientData):
        """Update client data for discount calculations"""
        self.client_data = client_data
        # Clear price cache when client changes
        self._price_cache = {}
    
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
    
    def get_product_base_price(self, product: ProductData) -> Decimal:
        """Get base price for product based on client type"""
        if not self.client_data or not self.client_data.id_tipo_cliente or not self.db_manager:
            return Decimal('0')
        
        # Check cache first
        cache_key = f"{product.id_producto}_{self.client_data.id_tipo_cliente}"
        if cache_key in self._price_cache:
            return self._price_cache[cache_key]
        
        # Get price from database
        price = self.db_manager.get_product_price(product.id_producto, self.client_data.id_tipo_cliente)
        if price is None:
            price = Decimal('0')
        
        # Cache the result
        self._price_cache[cache_key] = price
        return price
    
    def calculate_discounted_price(self, product: ProductData) -> Decimal:
        """Calculate price with client discount"""
        base_price = self.get_product_base_price(product)
        
        if not self.client_data:
            return base_price
        
        discount_amount = base_price * (self.client_data.descuento / 100)
        return base_price - discount_amount
    
    def get_price_info(self, product: ProductData) -> Dict[str, Decimal]:
        """Get detailed price information for a product"""
        precio_base = self.get_product_base_price(product)
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