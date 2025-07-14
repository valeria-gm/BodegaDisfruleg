import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import json
from decimal import Decimal
from typing import Dict, List, Optional
from typing import Dict, List, Optional, Any, Callable

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
    
    def __init__(self, root: tk.Tk, user_data,
                 db_manager: DatabaseManager,
                 pdf_generator: PDFGenerator,
                 cart_manager:CartManager,
                 product_manager: ProductManager,
                 on_state_change: Optional[Callable] = None):
        print(f"[DEBUG] ===== CREANDO NUEVA INSTANCIA DE ReciboAppMejorado =====\n")
        print(f"[DEBUG] ReciboAppMejorado instance id: {id(self)}")
        
        self.root = root
        self.root.title("Generador de Recibos")
        self.root.geometry("1000x1000")
        
        # Initialize user data
        self.user_data = user_data if isinstance(user_data, dict) else json.loads(user_data)
        self.es_admin = (self.user_data['rol'] == 'admin')
        
        # Initialize components
        self.db_manager = db_manager
        self.pdf_generator = pdf_generator
        self.cart_manager = cart_manager
        self.product_manager = product_manager
        self.auth_manager = AuthenticationManager(self)
        self.ui_builder = UIBuilder(root)
        self.on_state_change = on_state_change # <-- NUEVA LÍNEA
        
        print(f"[DEBUG] Callback on_state_change recibido:")
        if on_state_change:
            print(f"[DEBUG]   - Es una función válida: {callable(on_state_change)}")
            print(f"[DEBUG]   - Callback function object id: {id(on_state_change)}")
        else:
            print(f"[DEBUG]   - Es None: {on_state_change is None}")
            
        print(f"[DEBUG] ===== INSTANCIA CREADA EXITOSAMENTE =====\n")

        
        # Initialize variables
        self.grupo_seleccionado = tk.StringVar()
        self.cliente_seleccionado = tk.StringVar()
        self.search_var = tk.StringVar()
        self.guardar_en_bd = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar()
        self.sectioning_var = None  # Will be set when section selection is created
        
        # Data containers
        self.grupos: List[Dict[str, Any]] = []
        self.clientes: List[ClientData] = []
        self.current_group: Optional[Dict[str, Any]] = None
        self.current_client: Optional[ClientData] = None
        
        # UI components
        self.grupo_combo = None
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

    def _notify_state_change(self):
        """Helper method to call the callback if it exists."""
        print(f"[DEBUG] ===== NOTIFICANDO CAMBIO DE ESTADO =====\n")
        print(f"[DEBUG] ReciboAppMejorado instance id: {id(self)} está notificando cambio de estado")
        
        if self.on_state_change:
            print(f"[DEBUG]   - Callback es válido, llamando función...")
            print(f"[DEBUG]   - Callback function object id: {id(self.on_state_change)}")
            self.on_state_change()
            print(f"[DEBUG]   - Callback ejecutado exitosamente")
        else:
            print(f"[DEBUG]   - ERROR: No hay callback configurado (on_state_change es None)")
            
        print(f"[DEBUG] ===== NOTIFICACIÓN COMPLETADA =====\n")

    def on_client_change(self, event=None):
        """Handle client selection change"""
        # ... (toda tu lógica existente en on_client_change) ...
        cliente_display = self.cliente_seleccionado.get()
        cliente_nombre = cliente_display.split(' (')[0] if ' (' in cliente_display else cliente_display
        self.current_client = next((c for c in self.clientes if c.nombre_cliente == cliente_nombre), None)

        if self.current_client:
            self.product_manager.update_client_data(self.current_client)
            self._update_products_display()
            self.cart_manager.clear_cart()
            self._update_cart_display() # Esto ya notificará el cambio de estado del carrito
            self._enable_section_selection()
            
            client_type = self.db_manager.get_client_type_name(self.current_client.id_tipo_cliente)
            self.ui_builder.update_client_type_display(
                self.cliente_combo, client_type, float(self.current_client.descuento)
            )
            
            self.status_var.set(
                f"Cliente: {cliente_nombre} | Descuento: {float(self.current_client.descuento)}% | "
                f"{len(self.product_manager.all_products)} productos"
            )
            # CAMBIO 3: Notificar explícitamente que el cliente ha cambiado
            self._notify_state_change()
    
    def _load_data(self):
        """Load initial data from database"""
        try:
            self.grupos = self.db_manager.get_groups()
            # Don't load clients initially - they'll be loaded when group is selected
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
    
    def _create_interface(self):
        """Create the user interface"""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create sections
        self._create_group_section(main_frame)
        self._create_client_section(main_frame)
        self._create_section_selection(main_frame)
        self._create_products_section(main_frame)
        self._create_cart_section(main_frame)
        self._create_actions_section(main_frame)
        self._create_status_bar()
    
    def _create_group_section(self, parent):
        """Create group selection section"""
        group_names = [grupo['clave_grupo'] for grupo in self.grupos]
        self.grupo_combo = self.ui_builder.create_group_selection(
            parent, group_names, self.grupo_seleccionado,
            self.on_group_change, self.guardar_en_bd
        )
    
    def _create_client_section(self, parent):
        """Create client selection section"""
        # Start with empty client list - will be populated when group is selected
        self.cliente_combo = self.ui_builder.create_client_section(
            parent, [], self.cliente_seleccionado, self.on_client_change
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
            f"Seleccione un grupo"
        )
    
    # Event handlers
    def on_group_change(self, event=None):
        """Handle group selection change"""
        grupo_nombre = self.grupo_seleccionado.get()
        
        # Find selected group
        self.current_group = None
        for grupo in self.grupos:
            if grupo['clave_grupo'] == grupo_nombre:
                self.current_group = grupo
                break
        
        if self.current_group:
            try:
                # Load clients for this group
                self.clientes = self.db_manager.get_clients_by_group(self.current_group['id_grupo'])
                
                # Update client combo with filtered clients
                client_names = []
                for cliente in self.clientes:
                    client_type = self.db_manager.get_client_type_name(cliente.id_tipo_cliente)
                    display_name = f"{cliente.nombre_cliente} ({client_type})"
                    client_names.append(display_name)
                
                self.ui_builder.populate_combobox(self.cliente_combo, client_names)
                self.ui_builder.enable_client_selection(self.cliente_combo)
                
                # Clear current client and reset UI
                self.current_client = None
                self.cliente_seleccionado.set("")
                self.cart_manager.clear_cart()
                self._update_cart_display()
                self._clear_products_display()
                
                # Update status
                self.status_var.set(
                    f"Grupo: {grupo_nombre} | "
                    f"{len(self.clientes)} clientes disponibles | "
                    f"Seleccione un cliente"
                )
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar clientes: {str(e)}")
        else:
            # Clear everything when no group is selected
            self.clientes = []
            self.current_client = None
            self.ui_builder.populate_combobox(self.cliente_combo, [])
            self.ui_builder.disable_client_selection(self.cliente_combo)
            self.cart_manager.clear_cart()
            self._update_cart_display()
            self._clear_products_display()
    
    def on_client_change(self, event=None):
        """Handle client selection change"""
        cliente_display = self.cliente_seleccionado.get()
        
        # Extract client name from display (remove type info)
        if ' (' in cliente_display:
            cliente_nombre = cliente_display.split(' (')[0]
        else:
            cliente_nombre = cliente_display
        
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
            
            # Update client type display
            client_type = self.db_manager.get_client_type_name(self.current_client.id_tipo_cliente)
            self.ui_builder.update_client_type_display(
                self.cliente_combo, client_type, float(self.current_client.descuento)
            )
            
            # Update status
            self.status_var.set(
                f"Grupo: {self.current_group['clave_grupo']} | "
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
        if not self.current_group:
            messagebox.showerror("Error", "Debe seleccionar un grupo primero")
            return
        
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
        
        def get_section_item_count(section_id: str) -> int:
            return len(self.cart_manager.get_section_items(section_id))

        self.ui_builder.create_section_management_dialog(
            self.root, get_updated_sections,
            self.cart_manager.add_section,
            self.cart_manager.remove_section,
            self.cart_manager.rename_section,
            self._refresh_section_management,
            get_section_item_count
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
    
    def _clear_products_display(self):
        """Clear products display"""
        self.ui_builder.populate_treeview(self.productos_tree, [], 'id_producto')
    
    def _update_cart_display(self):
        """Update cart display"""
        print(f"[DEBUG] _update_cart_display llamado en instancia {id(self)}")
        
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
        
        print(f"[DEBUG] Cart actualizado: {count} productos, total: ${float(total):.2f}")
        print(f"[DEBUG] Notificando cambio de estado desde _update_cart_display...")
        self._notify_state_change()
    
    def show_preview(self):
        """Show receipt preview"""
        if not self.current_group:
            messagebox.showerror("Error", "Debe seleccionar un grupo")
            return
        
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
        if not self.current_group:
            messagebox.showerror("Error", "Debe seleccionar un grupo")
            return
        
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