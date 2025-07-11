import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Dict, List, Optional
from decimal import Decimal, InvalidOperation
from ..models.receipt_models import ProductData, CartItem, InvoiceSection
import uuid

class CartManager:
    """Handles shopping cart operations"""
    
    def __init__(self):
        self.cart_items: Dict[str, CartItem] = {}  # Changed to string keys for composite keys
        self.sections: Dict[str, InvoiceSection] = {}
        self.sectioning_enabled = False
        self.default_section_id = "default"
    
    def _get_cart_key(self, product_id: int, section_id: Optional[str] = None) -> str:
        """Generate cart key for product. If sectioning is enabled, include section_id"""
        if self.sectioning_enabled and section_id:
            return f"{product_id}_{section_id}"
        return str(product_id)
    
    def add_item(self, product: ProductData, cantidad: Decimal, precio_base: float, 
                 precio_final: float, monto_descuento: float, section_id: Optional[str] = None) -> bool:
        """Add item to cart"""
        try:
            if cantidad <= Decimal('0'):
                raise ValueError("Quantity must be greater than 0")
            
            # Handle section assignment
            if self.sectioning_enabled and section_id:
                assigned_section_id = section_id
            elif self.sectioning_enabled and not section_id:
                assigned_section_id = self._get_first_section_id()
            else:
                assigned_section_id = None
            
            # Generate cart key
            cart_key = self._get_cart_key(product.id_producto, assigned_section_id)
            
            # Check if item already exists in this section
            if cart_key in self.cart_items:
                # Update quantity instead of replacing
                self.cart_items[cart_key].cantidad += cantidad
                return True
            
            cart_item = CartItem(
                producto=product,
                cantidad=cantidad,
                precio_base=precio_base,
                precio_final=precio_final,
                monto_descuento=monto_descuento,
                section_id=assigned_section_id
            )
            
            self.cart_items[cart_key] = cart_item
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el producto: {str(e)}")
            return False
    
    def remove_item(self, cart_key: str) -> bool:
        """Remove item from cart using cart key"""
        if cart_key in self.cart_items:
            del self.cart_items[cart_key]
            return True
        return False
    
    def update_quantity(self, cart_key: str, new_quantity: Decimal) -> bool:
        """Update quantity of item in cart using cart key"""
        if cart_key in self.cart_items:
            if new_quantity <= Decimal('0'):
                return self.remove_item(cart_key)
            
            self.cart_items[cart_key].cantidad = new_quantity
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
        """Check if product is in cart (any section)"""
        if not self.sectioning_enabled:
            return str(product_id) in self.cart_items
        
        # Check if product exists in any section
        for key in self.cart_items:
            if key.startswith(f"{product_id}_") or key == str(product_id):
                return True
        return False
    
    def is_in_cart_section(self, product_id: int, section_id: Optional[str] = None) -> bool:
        """Check if product is in cart for a specific section"""
        cart_key = self._get_cart_key(product_id, section_id)
        return cart_key in self.cart_items
    
    def get_cart_display_data(self) -> List[Dict]:
        """Get cart data formatted for display"""
        display_data = []
        
        for cart_key, item in self.cart_items.items():
            product = item.producto
            nombre_producto = product.nombre_producto
            
            if product.es_especial:
                nombre_producto = f"🔒 {nombre_producto}"
            
            display_data.append({
                'id': cart_key,  # Use cart key instead of product_id
                'producto': nombre_producto,
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
                'subtotal': item.subtotal,
                'section_id': item.section_id
            })
        
        return products_for_invoice
    
    def get_sections_for_invoice(self) -> List[InvoiceSection]:
        """Get sections data for invoice saving"""
        if not self.sectioning_enabled:
            return []
        
        sections_list = []
        for section in self.sections.values():
            # Create section with items
            section_items = self.get_section_items(section.id)
            invoice_section = InvoiceSection(
                id=section.id,
                name=section.name,
                items=section_items
            )
            sections_list.append(invoice_section)
        
        return sections_list
    
    # Section management methods
    def enable_sectioning(self, enabled: bool = True):
        """Enable or disable sectioning mode"""
        if enabled and not self.sectioning_enabled:
            # Create default section if enabling
            if not self.sections:
                self.add_section("General")
            # Assign all existing items to first section
            first_section_id = self._get_first_section_id()
            for item in self.cart_items.values():
                item.section_id = first_section_id
        elif not enabled and self.sectioning_enabled:
            # Remove section assignments
            for item in self.cart_items.values():
                item.section_id = None
        
        self.sectioning_enabled = enabled
    
    def add_section(self, name: str) -> str:
        """Add a new section"""
        section_id = str(uuid.uuid4())
        section = InvoiceSection(id=section_id, name=name)
        self.sections[section_id] = section
        return section_id
    
    def remove_section(self, section_id: str) -> bool:
        """Remove a section"""
        if section_id not in self.sections:
            return False
        
        # Check if section has items
        items_in_section = [item for item in self.cart_items.values() if item.section_id == section_id]
        
        if items_in_section:
            # If this is the only section, don't allow removal
            if len(self.sections) == 1:
                messagebox.showerror("Error", "No se puede eliminar la única sección")
                return False
            
            # Ask user what to do with items
            if messagebox.askyesno("Sección con productos", 
                                  f"La sección '{self.sections[section_id].name}' contiene {len(items_in_section)} productos. "
                                  "¿Mover productos a otra sección?"):
                # Move items to first available section
                target_section_id = self._get_first_section_id(exclude=section_id)
                if target_section_id:
                    for item in items_in_section:
                        item.section_id = target_section_id
                else:
                    messagebox.showerror("Error", "No hay otra sección disponible")
                    return False
            else:
                # Remove items from cart
                for item in items_in_section:
                    self.remove_item(item.producto.id_producto)
        
        del self.sections[section_id]
        return True
    
    def rename_section(self, section_id: str, new_name: str) -> bool:
        """Rename a section"""
        if section_id in self.sections:
            self.sections[section_id].name = new_name
            return True
        return False
    
    def move_item_to_section(self, cart_key: str, new_section_id: str) -> bool:
        """Move an item to a different section"""
        if cart_key in self.cart_items and new_section_id in self.sections:
            item = self.cart_items[cart_key]
            
            # Remove item from current location
            del self.cart_items[cart_key]
            
            # Update section_id
            item.section_id = new_section_id
            
            # Add item to new location
            new_cart_key = self._get_cart_key(item.producto.id_producto, new_section_id)
            self.cart_items[new_cart_key] = item
            
            return True
        return False
    
    def get_sections(self) -> Dict[str, InvoiceSection]:
        """Get all sections"""
        return self.sections.copy()
    
    def get_section_items(self, section_id: str) -> List[CartItem]:
        """Get items in a specific section"""
        return [item for item in self.cart_items.values() if item.section_id == section_id]
    
    def get_sectioned_cart_data(self) -> Dict[str, List[Dict]]:
        """Get cart data organized by sections"""
        if not self.sectioning_enabled:
            return {"default": self.get_cart_display_data()}
        
        sectioned_data = {}
        for section_id, section in self.sections.items():
            items_in_section = self.get_section_items(section_id)
            display_data = []
            
            for item in items_in_section:
                product = item.producto
                nombre_producto = product.nombre_producto
                
                if product.es_especial:
                    nombre_producto = f"🔒 {nombre_producto}"
                
                # Find the cart key for this item
                cart_key = self._get_cart_key(product.id_producto, item.section_id)
                
                display_data.append({
                    'id': cart_key,
                    'producto': nombre_producto,
                    'cantidad': f"{float(item.cantidad):.2f}",
                    'unidad': product.unidad_producto,
                    'precio_base': f"${item.precio_base:.2f}",
                    'descuento': f"-${item.monto_descuento:.2f}",
                    'precio_final': f"${item.precio_final:.2f}",
                    'subtotal': f"${float(item.subtotal):.2f}"
                })
            
            sectioned_data[section_id] = {
                'name': section.name,
                'items': display_data,
                'subtotal': float(sum(item.subtotal for item in items_in_section))
            }
        
        return sectioned_data
    
    def _get_first_section_id(self, exclude: str = None) -> Optional[str]:
        """Get the first available section ID"""
        for section_id in self.sections:
            if section_id != exclude:
                return section_id
        return None

class CartDialog:
    """Dialog for adding products to cart"""
    
    def __init__(self, parent, product: ProductData, price_info: Dict, on_add_callback, 
                 sections: Dict[str, InvoiceSection] = None, sectioning_enabled: bool = False):
        self.parent = parent
        self.product = product
        self.price_info = price_info
        self.on_add_callback = on_add_callback
        self.sections = sections or {}
        self.sectioning_enabled = sectioning_enabled
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
        current_row = 0
        
        # Product name
        nombre_producto = self.product.nombre_producto
        if self.product.es_especial:
            nombre_producto = f"🔒 {nombre_producto} (ESPECIAL)"
        
        tk.Label(self.dialog, text=nombre_producto, 
                font=("Arial", 12, "bold")).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 5))
        current_row += 1
        
        # Price information
        tk.Label(self.dialog, text=f"Precio base: ${float(self.price_info['precio_base']):.2f}", 
                font=("Arial", 10)).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=20)
        current_row += 1
        
        if self.price_info['descuento'] > 0:
            tk.Label(self.dialog, 
                    text=f"Descuento ({float(self.price_info['descuento']):.1f}%): -${float(self.price_info['monto_descuento']):.2f}",
                    font=("Arial", 10), fg="red").grid(row=current_row, column=0, columnspan=2, sticky="w", padx=20)
            current_row += 1
        
        tk.Label(self.dialog, text=f"Precio final: ${float(self.price_info['precio_final']):.2f}", 
                font=("Arial", 11, "bold")).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=20, pady=5)
        current_row += 1
        
        tk.Label(self.dialog, text=f"Unidad: {self.product.unidad_producto}",
                font=("Arial", 10)).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=20)
        current_row += 1
        
        # Section selection (if sectioning is enabled)
        self.section_var = tk.StringVar()
        self.section_combo = None
        if self.sectioning_enabled and self.sections:
            tk.Label(self.dialog, text="Sección:", font=("Arial", 11)).grid(row=current_row, column=0, sticky="e", padx=20)
            
            from tkinter import ttk
            section_names = [section.name for section in self.sections.values()]
            self.section_combo = ttk.Combobox(self.dialog, textvariable=self.section_var, 
                                       values=section_names, state="readonly", width=15)
            self.section_combo.grid(row=current_row, column=1, sticky="w", padx=5)
            
            if section_names:
                self.section_combo.set(section_names[0])
            
            current_row += 1
        
        # Quantity input
        tk.Label(self.dialog, text="Cantidad:", font=("Arial", 11)).grid(row=current_row, column=0, sticky="e", padx=20)
        
        self.cantidad_var = tk.StringVar(value="1.0")
        self.cantidad_entry = tk.Entry(self.dialog, textvariable=self.cantidad_var, 
                                      width=10, font=("Arial", 11))
        self.cantidad_entry.grid(row=current_row, column=1, sticky="w", padx=5)
        current_row += 1
        
        # Total
        self.total_var = tk.StringVar(value=f"Total: ${float(self.price_info['precio_final']):.2f}")
        tk.Label(self.dialog, textvariable=self.total_var, 
                font=("Arial", 11, "bold"), fg="#2196F3").grid(row=current_row, column=0, columnspan=2, pady=(10, 20))
        current_row += 1
        
        # Buttons
        botones_frame = tk.Frame(self.dialog)
        botones_frame.grid(row=current_row, column=0, columnspan=2, pady=(0, 15))
        
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
            
            # Get selected section ID
            section_id = None
            if self.sectioning_enabled and self.sections:
                selected_section_name = self.section_var.get()
                for sid, section in self.sections.items():
                    if section.name == selected_section_name:
                        section_id = sid
                        break
            
            self.result = {
                'cantidad': cantidad,
                'precio_info': self.price_info,
                'section_id': section_id
            }
            
            if self.on_add_callback:
                self.on_add_callback(self.product, cantidad, self.price_info, section_id)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar: {str(e)}")
    
    def _cancel(self):
        """Cancel dialog"""
        self.result = None
        self.dialog.destroy()