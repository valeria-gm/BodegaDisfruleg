import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import json
from decimal import Decimal
from typing import Dict, List, Optional

# Import components
from .components.database_manager import DatabaseManager
from .components.pdf_generator import PDFGenerator
from .components.auth_dialog import AuthenticationManager
from .components.ui_builder import UIBuilder
from .components.product_manager import ProductManager
from .components.cart_manager import CartManager, CartDialog
from .models.receipt_models import ProductData, ClientData, CartItem

class ReciboAppMejorado:
    """Refactored Receipt Application with modular components"""
    
    def __init__(self, root: tk.Tk, user_data):
        self.root = root
        self.root.title("Generador de Recibos - Mejorado")
        self.root.geometry("1000x700")
        
        # Initialize user data
        self.user_data = user_data if isinstance(user_data, dict) else json.loads(user_data)
        self.es_admin = (self.user_data['rol'] == 'admin')
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.pdf_generator = PDFGenerator()
        self.auth_manager = AuthenticationManager(self)
        self.ui_builder = UIBuilder(root)
        self.cart_manager = CartManager()
        
        # Initialize variables
        self.cliente_seleccionado = tk.StringVar()
        self.search_var = tk.StringVar()
        self.guardar_en_bd = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar()
        self.sectioning_var = None  # Will be set when section selection is created
        
        # Data containers
        self.clientes: List[ClientData] = []
        self.current_client: Optional[ClientData] = None
        self.product_manager: Optional[ProductManager] = None
        
        # UI components
        self.cliente_combo = None
        self.productos_tree = None
        self.carrito_tree = None
        self.total_var = None
        self.section_selection_frame = None
        self.section_management_button = None
        
        # Initialize application
        self._load_data()
        self._create_interface()
        self._setup_initial_status()
    
    def _load_data(self):
        """Load initial data from database"""
        try:
            self.clientes = self.db_manager.get_clients()
            productos = self.db_manager.get_products()
            self.product_manager = ProductManager(productos, db_manager=self.db_manager)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
    
    def _create_interface(self):
        """Create the user interface"""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create sections
        self._create_client_section(main_frame)
        self._create_section_selection(main_frame)
        self._create_products_section(main_frame)
        self._create_cart_section(main_frame)
        self._create_actions_section(main_frame)
        self._create_status_bar()
    
    def _create_client_section(self, parent):
        """Create client selection section"""
        client_names = [cliente.nombre_cliente for cliente in self.clientes]
        self.cliente_combo = self.ui_builder.create_client_section(
            parent, client_names, self.cliente_seleccionado,
            self.on_client_change, self.guardar_en_bd
        )
    
    def _create_section_selection(self, parent):
        """Create section selection section"""
        self.section_selection_frame = self.ui_builder.create_section_selection(
            parent, self.on_sectioning_toggle, self.on_manage_sections
        )
        # Connect sectioning_var to the frame's variable
        self.sectioning_var = self.section_selection_frame.sectioning_var
    
    def _create_products_section(self, parent):
        """Create products section"""
        self.productos_tree = self.ui_builder.create_products_section(
            parent, self.search_var, self.on_search_change,
            self.on_clear_search, self.on_product_double_click
        )
    
    def _create_cart_section(self, parent):
        """Create cart section"""
        self.carrito_tree, self.total_var = self.ui_builder.create_cart_section(
            parent, self.on_cart_double_click, self.on_remove_from_cart,
            self.on_clear_cart
        )
    
    def _create_actions_section(self, parent):
        """Create actions section"""
        self.ui_builder.create_actions_section(
            parent, self.generate_receipt, self.show_preview
        )
    
    def _create_status_bar(self):
        """Create status bar"""
        self.ui_builder.create_status_bar(self.root, self.status_var)
    
    def _setup_initial_status(self):
        """Setup initial status message"""
        self.status_var.set(
            f"Usuario: {self.user_data['nombre_completo']} | "
            f"Rol: {self.user_data['rol']} | "
            f"Seleccione un cliente"
        )
    
    # Event handlers
    def on_client_change(self, event=None):
        """Handle client selection change"""
        cliente_nombre = self.cliente_seleccionado.get()
        
        # Find selected client
        self.current_client = None
        for cliente in self.clientes:
            if cliente.nombre_cliente == cliente_nombre:
                self.current_client = cliente
                break
        
        if self.current_client:
            # Update product manager with client data
            self.product_manager.update_client_data(self.current_client)
            
            # Update products display
            self._update_products_display()
            
            # Clear cart
            self.cart_manager.clear_cart()
            self._update_cart_display()
            
            # Enable section selection UI
            self._enable_section_selection()
            
            # Update status
            self.status_var.set(
                f"Cliente: {cliente_nombre} | "
                f"Descuento: {float(self.current_client.descuento)}% | "
                f"{len(self.product_manager.all_products)} productos"
            )
    
    def on_search_change(self, *args):
        """Handle search text change"""
        if self.product_manager:
            search_text = self.search_var.get()
            filtered_products = self.product_manager.filter_products(search_text)
            self._update_products_display(filtered_products)
    
    def on_clear_search(self):
        """Handle clear search button"""
        self.search_var.set("")
        if self.product_manager:
            self._update_products_display()
    
    def on_product_double_click(self, event):
        """Handle product double click"""
        if not self.current_client:
            messagebox.showerror("Error", "Debe seleccionar un cliente primero")
            return
        
        item_seleccionado = self.productos_tree.focus()
        if not item_seleccionado:
            return
        
        try:
            # Get product ID from tags
            item_data = self.productos_tree.item(item_seleccionado)
            product_id = int(item_data['tags'][0])
            product = self.product_manager.get_product_by_id(product_id)
            
            if not product:
                messagebox.showerror("Error", "Producto no encontrado")
                return
            
            # Check if special product and user is not admin
            if product.es_especial and not self.es_admin:
                if not self.auth_manager.verify_admin_password(self.root):
                    return
                messagebox.showinfo("Autorizado", "Acceso autorizado. Puede agregar el producto especial.")
            
            # Check if already in cart (behavior depends on sectioning)
            if self.cart_manager.is_in_cart(product_id):
                if not self.cart_manager.sectioning_enabled:
                    # Without sectioning, edit existing quantity
                    if messagebox.askyesno("Producto en carrito", 
                                         "Este producto ya está en el carrito. ¿Desea editar la cantidad?"):
                        self._edit_cart_quantity(product_id)
                    return
                else:
                    # With sectioning, allow adding to different sections
                    # The dialog will handle section selection
                    pass
            
            # Show add to cart dialog
            self._show_add_to_cart_dialog(product)
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
    
    def on_cart_double_click(self, event):
        """Handle cart item double click"""
        item_seleccionado = self.carrito_tree.focus()
        if not item_seleccionado:
            return
        
        try:
            cart_key = self.carrito_tree.item(item_seleccionado, "tags")[0]
            self._edit_cart_quantity(cart_key)
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Error al obtener información del producto")
    
    def on_remove_from_cart(self):
        """Handle remove from cart button"""
        item_seleccionado = self.carrito_tree.focus()
        if not item_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un producto del carrito para eliminar")
            return
        
        try:
            cart_key = self.carrito_tree.item(item_seleccionado, "tags")[0]
            cart_items = self.cart_manager.get_cart_items()
            
            if cart_key in cart_items:
                product_name = cart_items[cart_key].producto.nombre_producto
                if messagebox.askyesno("Confirmar", f"¿Eliminar {product_name} del carrito?"):
                    self.cart_manager.remove_item(cart_key)
                    self._update_cart_display()
                    self._update_products_display()
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Error al eliminar producto")
    
    def on_clear_cart(self):
        """Handle clear cart button"""
        if self.cart_manager.clear_cart():
            self._update_cart_display()
            self._update_products_display()
    
    def on_sectioning_toggle(self):
        """Handle sectioning toggle"""
        enabled = self.sectioning_var.get()
        self.cart_manager.enable_sectioning(enabled)
        
        # Show/hide section management button
        if enabled:
            self.ui_builder.show_section_management_button(self.section_selection_frame)
        else:
            self.ui_builder.hide_section_management_button(self.section_selection_frame)
        
        self._update_cart_display()
    
    def on_manage_sections(self):
        """Handle section management button"""
        if not self.cart_manager.sectioning_enabled:
            messagebox.showwarning("Advertencia", "Las secciones no están habilitadas")
            return
        
        def get_updated_sections():
            return self.cart_manager.get_sections()
        
        self.ui_builder.create_section_management_dialog(
            self.root, get_updated_sections,
            self.cart_manager.add_section,
            self.cart_manager.remove_section,
            self.cart_manager.rename_section,
            self._refresh_section_management
        )
    
    def _enable_section_selection(self):
        """Enable section selection UI after client is selected"""
        self.ui_builder.enable_section_controls(self.section_selection_frame)
    
    def _refresh_section_management(self):
        """Refresh section management after changes"""
        # This method can be used to refresh UI elements when sections change
        # For now, it's not needed as the dialog updates automatically
        pass
    
    # Helper methods
    def _show_add_to_cart_dialog(self, product: ProductData):
        """Show dialog to add product to cart"""
        price_info = self.product_manager.get_price_info(product)
        
        def on_add_callback(product, cantidad, price_info, section_id=None):
            """Callback when product is added to cart"""
            success = self.cart_manager.add_item(
                product, cantidad,
                float(price_info['precio_base']),
                float(price_info['precio_final']),
                float(price_info['monto_descuento']),
                section_id
            )
            
            if success:
                self._update_cart_display()
                self._update_products_display()
        
        # Create dialog
        CartDialog(self.root, product, price_info, on_add_callback,
                  self.cart_manager.get_sections(),
                  self.cart_manager.sectioning_enabled)
    
    def _edit_cart_quantity(self, cart_key: str):
        """Edit quantity of product in cart"""
        cart_items = self.cart_manager.get_cart_items()
        if cart_key not in cart_items:
            return
        
        item = cart_items[cart_key]
        nueva_cantidad = simpledialog.askfloat(
            "Editar Cantidad",
            f"Nueva cantidad para {item.producto.nombre_producto}:",
            initialvalue=float(item.cantidad),
            minvalue=0.01
        )
        
        if nueva_cantidad:
            if self.cart_manager.update_quantity(cart_key, Decimal(str(nueva_cantidad))):
                self._update_cart_display()
    
    def _update_products_display(self, products: List[ProductData] = None):
        """Update products display"""
        if not self.product_manager:
            return
        
        if products is None:
            products = self.product_manager.filtered_products
        
        display_data = []
        for product in products:
            in_cart = self.cart_manager.is_in_cart(product.id_producto)
            display_info = self.product_manager.get_product_display_info(product, in_cart)
            display_data.append(display_info)
        
        self.ui_builder.populate_treeview(self.productos_tree, display_data, 'id_producto')
    
    def _update_cart_display(self):
        """Update cart display"""
        if self.cart_manager.sectioning_enabled:
            # Use sectioned display
            sectioned_data = self.cart_manager.get_sectioned_cart_data()
            self.ui_builder.populate_sectioned_treeview(self.carrito_tree, sectioned_data, 'id')
        else:
            # Use regular display
            display_data = self.cart_manager.get_cart_display_data()
            self.ui_builder.populate_treeview(self.carrito_tree, display_data, 'id')
        
        # Update total
        total = self.cart_manager.get_cart_total()
        self.total_var.set(f"Total: ${float(total):.2f}")
        
        # Update status
        count = self.cart_manager.get_cart_count()
        self.status_var.set(f"Carrito: {count} productos | Total: ${float(total):.2f}")
    
    def show_preview(self):
        """Show receipt preview"""
        if not self.current_client:
            messagebox.showerror("Error", "Debe seleccionar un cliente")
            return
        
        if self.cart_manager.get_cart_count() == 0:
            messagebox.showerror("Error", "El carrito está vacío")
            return
        
        # Generate preview content
        content = f"RECIBO PARA: {self.current_client.nombre_cliente}\n"
        content += f"Fecha: {datetime.now().strftime('%Y-%m-%d')}\n"
        content += "="*50 + "\n"
        
        if self.cart_manager.sectioning_enabled:
            # Sectioned preview
            sectioned_data = self.cart_manager.get_sectioned_cart_data()
            for section_id, section_data in sectioned_data.items():
                if section_id != "default":
                    content += f"\n═══ {section_data['name']} ═══\n"
                    
                    for item_data in section_data['items']:
                        nombre_producto = item_data['nombre']
                        cantidad = item_data['cantidad']
                        unidad = item_data['unidad']
                        precio_final = item_data['precio_final']
                        subtotal = item_data['subtotal']
                        
                        content += f"{nombre_producto}\n"
                        content += f"  {cantidad} {unidad} x {precio_final} = {subtotal}\n\n"
                    
                    content += f"Subtotal {section_data['name']}: ${section_data['subtotal']:.2f}\n"
                    content += "-"*30 + "\n"
        else:
            # Regular preview
            cart_items = self.cart_manager.get_cart_items()
            for item in cart_items.values():
                nombre_producto = item.producto.nombre_producto
                if item.producto.es_especial:
                    nombre_producto = f"🔒 {nombre_producto} (ESPECIAL)"
                
                content += f"{nombre_producto}\n"
                content += f"  {float(item.cantidad):.2f} {item.producto.unidad_producto} x ${item.precio_final:.2f} = ${float(item.subtotal):.2f}\n\n"
        
        content += "="*50 + "\n"
        content += f"TOTAL: ${float(self.cart_manager.get_cart_total()):.2f}"
        
        # Show preview window
        self.ui_builder.create_preview_window(self.root, content)
    
    def generate_receipt(self):
        """Generate final receipt"""
        if not self.current_client:
            messagebox.showerror("Error", "Debe seleccionar un cliente")
            return
        
        if self.cart_manager.get_cart_count() == 0:
            messagebox.showerror("Error", "El carrito está vacío")
            return
        
        total = float(self.cart_manager.get_cart_total())
        
        if not messagebox.askyesno("Confirmar", f"¿Generar recibo por ${total:.2f}?"):
            return
        
        # Save to database if enabled
        if self.guardar_en_bd.get():
            try:
                products_data = self.cart_manager.get_products_for_invoice()
                sections_data = self.cart_manager.get_sections_for_invoice()
                invoice_id = self.db_manager.save_invoice(
                    self.current_client.id_cliente, 
                    products_data, 
                    sections_data
                )
                if invoice_id:
                    messagebox.showinfo("Éxito", f"Recibo guardado correctamente (ID: {invoice_id})")
                    self.status_var.set(f"Factura #{invoice_id} guardada en base de datos")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar en base de datos: {str(e)}")
        
        # Generate PDF
        try:
            if self.cart_manager.sectioning_enabled:
                # Generate sectioned PDF
                sectioned_data = self.cart_manager.get_sectioned_cart_data()
                filename = self.pdf_generator.generate_sectioned_pdf(
                    self.current_client.nombre_cliente,
                    sectioned_data,
                    total
                )
            else:
                # Generate regular PDF
                cart_items = self.cart_manager.get_cart_items()
                productos_finales = []
                
                for item in cart_items.values():
                    productos_finales.append((
                        item.producto.nombre_producto,
                        float(item.cantidad),
                        item.producto.unidad_producto,
                        item.precio_final,
                        float(item.subtotal)
                    ))
                
                filename = self.pdf_generator.create_pdf_from_products(
                    self.current_client.nombre_cliente,
                    productos_finales,
                    total
                )
            
            messagebox.showinfo("Éxito", f"Recibo guardado en {filename}")
            
        except Exception as e:
            messagebox.showerror("Error PDF", f"No se pudo generar el PDF: {e}")
        
        # Clear cart option
        if messagebox.askyesno("Limpiar Carrito", "¿Desea limpiar el carrito para un nuevo recibo?"):
            self.cart_manager.clear_cart()
            self._update_cart_display()
            self._update_products_display()
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()

# Legacy support - keep the old class name as alias
ReciboApp = ReciboAppMejorado

if __name__ == "__main__":
    root = tk.Tk()
    user_data = {
        'nombre_completo': 'Usuario Prueba',
        'rol': 'usuario'  # Change to 'admin' to test special products
    }
    app = ReciboAppMejorado(root, user_data)
    root.mainloop()