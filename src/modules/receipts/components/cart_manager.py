import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Dict, List, Optional
from decimal import Decimal, InvalidOperation
from ..models.receipt_models import ProductData, CartItem

class CartManager:
    """Handles shopping cart operations"""
    
    def __init__(self):
        self.cart_items: Dict[int, CartItem] = {}
    
    def add_item(self, product: ProductData, cantidad: Decimal, precio_base: float, 
                 precio_final: float, monto_descuento: float) -> bool:
        """Add item to cart"""
        try:
            if cantidad <= Decimal('0'):
                raise ValueError("Quantity must be greater than 0")
            
            cart_item = CartItem(
                producto=product,
                cantidad=cantidad,
                precio_base=precio_base,
                precio_final=precio_final,
                monto_descuento=monto_descuento
            )
            
            self.cart_items[product.id_producto] = cart_item
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el producto: {str(e)}")
            return False
    
    def remove_item(self, product_id: int) -> bool:
        """Remove item from cart"""
        if product_id in self.cart_items:
            del self.cart_items[product_id]
            return True
        return False
    
    def update_quantity(self, product_id: int, new_quantity: Decimal) -> bool:
        """Update quantity of item in cart"""
        if product_id in self.cart_items:
            if new_quantity <= Decimal('0'):
                return self.remove_item(product_id)
            
            self.cart_items[product_id].cantidad = new_quantity
            return True
        return False
    
    def clear_cart(self) -> bool:
        """Clear all items from cart"""
        if self.cart_items:
            if messagebox.askyesno("Confirmar", "¿Limpiar todo el carrito?"):
                self.cart_items.clear()
                return True
            return False
        return True
    
    def get_cart_items(self) -> Dict[int, CartItem]:
        """Get all cart items"""
        return self.cart_items.copy()
    
    def get_cart_total(self) -> Decimal:
        """Calculate total cart value"""
        total = Decimal('0')
        for item in self.cart_items.values():
            total += item.subtotal
        return total
    
    def get_cart_count(self) -> int:
        """Get number of items in cart"""
        return len(self.cart_items)
    
    def is_in_cart(self, product_id: int) -> bool:
        """Check if product is in cart"""
        return product_id in self.cart_items
    
    def get_cart_display_data(self) -> List[Dict]:
        """Get cart data formatted for display"""
        display_data = []
        
        for product_id, item in self.cart_items.items():
            product = item.producto
            nombre_producto = product.nombre_producto
            
            if product.es_especial:
                nombre_producto = f"🔒 {nombre_producto}"
            
            display_data.append({
                'id': product_id,
                'nombre': nombre_producto,
                'cantidad': f"{float(item.cantidad):.2f}",
                'unidad': product.unidad_producto,
                'precio_base': f"${item.precio_base:.2f}",
                'descuento': f"-${item.monto_descuento:.2f}",
                'precio_final': f"${item.precio_final:.2f}",
                'subtotal': f"${float(item.subtotal):.2f}"
            })
        
        return display_data
    
    def get_products_for_invoice(self) -> List[Dict]:
        """Get cart items formatted for invoice saving"""
        products_for_invoice = []
        
        for item in self.cart_items.values():
            products_for_invoice.append({
                'producto': {
                    'id_producto': item.producto.id_producto,
                    'nombre_producto': item.producto.nombre_producto,
                    'unidad_producto': item.producto.unidad_producto
                },
                'cantidad': item.cantidad,
                'precio_final': Decimal(str(item.precio_final)),
                'subtotal': item.subtotal
            })
        
        return products_for_invoice

class CartDialog:
    """Dialog for adding products to cart"""
    
    def __init__(self, parent, product: ProductData, price_info: Dict, on_add_callback):
        self.parent = parent
        self.product = product
        self.price_info = price_info
        self.on_add_callback = on_add_callback
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Agregar Producto")
        self.dialog.transient(parent)
        self.dialog.resizable(False, False)
        
        self._create_widgets()
        self._setup_bindings()
        self._center_dialog()
        
        # Make modal
        self.dialog.grab_set()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        # Product name
        nombre_producto = self.product.nombre_producto
        if self.product.es_especial:
            nombre_producto = f"🔒 {nombre_producto} (ESPECIAL)"
        
        tk.Label(self.dialog, text=nombre_producto, 
                font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 5))
        
        # Price information
        tk.Label(self.dialog, text=f"Precio base: ${float(self.price_info['precio_base']):.2f}", 
                font=("Arial", 10)).grid(row=1, column=0, columnspan=2, sticky="w", padx=20)
        
        if self.price_info['descuento'] > 0:
            tk.Label(self.dialog, 
                    text=f"Descuento ({float(self.price_info['descuento']):.1f}%): -${float(self.price_info['monto_descuento']):.2f}",
                    font=("Arial", 10), fg="red").grid(row=2, column=0, columnspan=2, sticky="w", padx=20)
        
        tk.Label(self.dialog, text=f"Precio final: ${float(self.price_info['precio_final']):.2f}", 
                font=("Arial", 11, "bold")).grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=5)
        
        tk.Label(self.dialog, text=f"Unidad: {self.product.unidad_producto}",
                font=("Arial", 10)).grid(row=4, column=0, columnspan=2, sticky="w", padx=20)
        
        # Quantity input
        tk.Label(self.dialog, text="Cantidad:", font=("Arial", 11)).grid(row=5, column=0, sticky="e", padx=20)
        
        self.cantidad_var = tk.StringVar(value="1.0")
        self.cantidad_entry = tk.Entry(self.dialog, textvariable=self.cantidad_var, 
                                      width=10, font=("Arial", 11))
        self.cantidad_entry.grid(row=5, column=1, sticky="w", padx=5)
        
        # Total
        self.total_var = tk.StringVar(value=f"Total: ${float(self.price_info['precio_final']):.2f}")
        tk.Label(self.dialog, textvariable=self.total_var, 
                font=("Arial", 11, "bold"), fg="#2196F3").grid(row=6, column=0, columnspan=2, pady=(10, 20))
        
        # Buttons
        botones_frame = tk.Frame(self.dialog)
        botones_frame.grid(row=7, column=0, columnspan=2, pady=(0, 15))
        
        tk.Button(botones_frame, text="Agregar", 
                 command=self._add_to_cart, bg="#4CAF50", fg="white",
                 padx=15, pady=3).pack(side="left", padx=5)
        
        tk.Button(botones_frame, text="Cancelar", 
                 command=self._cancel, bg="#f44336", fg="white",
                 padx=15, pady=3).pack(side="left", padx=5)
    
    def _setup_bindings(self):
        """Setup keyboard bindings and event handlers"""
        self.cantidad_entry.focus_set()
        self.cantidad_entry.select_range(0, tk.END)
        self.cantidad_entry.bind("<Return>", lambda e: self._add_to_cart())
        self.cantidad_var.trace("w", self._calculate_total)
    
    def _center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_reqwidth()
        height = self.dialog.winfo_reqheight()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def _calculate_total(self, *args):
        """Calculate total based on quantity"""
        try:
            cantidad = Decimal(self.cantidad_var.get().strip())
            total = cantidad * self.price_info['precio_final']
            self.total_var.set(f"Total: ${float(total):.2f}")
        except (ValueError, InvalidOperation):
            self.total_var.set("Total: $0.00")
    
    def _add_to_cart(self):
        """Add product to cart"""
        try:
            cantidad = Decimal(self.cantidad_var.get().strip())
            if cantidad <= Decimal('0'):
                messagebox.showerror("Error", "La cantidad debe ser mayor que 0")
                return
            
            self.result = {
                'cantidad': cantidad,
                'precio_info': self.price_info
            }
            
            if self.on_add_callback:
                self.on_add_callback(self.product, cantidad, self.price_info)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar: {str(e)}")
    
    def _cancel(self):
        """Cancel dialog"""
        self.result = None
        self.dialog.destroy()