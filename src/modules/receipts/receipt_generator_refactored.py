# receipt_generator_refactored.py
# Versión actualizada que integra el sistema de secciones

import tkinter as tk
from tkinter import ttk, messagebox
from src.modules.receipts.components import database
from src.modules.receipts.components import generador_pdf as generador_pdf
from src.modules.receipts.components.carrito_module import CarritoConSecciones, DialogoSeccion
from src.modules.receipts.components import generador_excel

class ReciboAppMejorado:
    def __init__(self, parent=None, user_data=None):
        self.root = parent if parent else tk.Tk()
        self.user_data = user_data or {}
        
        self.root.title("Disfruleg - Sistema de Ventas con Secciones")
        self.root.geometry("1100x750")

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.style.configure("Total.TLabel", font=("Helvetica", 12, "bold"))

        self.grupos_data = {nombre: g_id for g_id, nombre in database.obtener_grupos()}
        if not self.grupos_data:
            messagebox.showerror("Error de Base de Datos", "No se pudieron cargar los grupos de clientes.")
            if parent is None:
                self.root.destroy()
            return
            
        self.contador_pestañas = 0
        self._crear_widgets_principales()
        self._agregar_pestaña()

    def _crear_widgets_principales(self):
        """Crea los widgets principales de la aplicación"""
        frame_superior = ttk.Frame(self.root, padding=(10, 10, 10, 0))
        frame_superior.pack(fill="x")
        
        btn_agregar_tab = ttk.Button(
            frame_superior, 
            text="➕ Agregar Nuevo Pedido", 
            command=self._agregar_pestaña
        )
        btn_agregar_tab.pack(side="left")
        
        # Información sobre secciones
        info_label = ttk.Label(
            frame_superior, 
            text="💡 Tip: Active 'Habilitar Secciones' para organizar productos por categorías",
            font=("Arial", 9),
            foreground="blue"
        )
        info_label.pack(side="right", padx=10)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=(5, 10), padx=10, expand=True, fill="both")

    def _agregar_pestaña(self):
        """Agrega una nueva pestaña de pedido"""
        if self.contador_pestañas >= 5:
            messagebox.showinfo("Límite Alcanzado", "No se pueden agregar más de 5 pedidos.")
            return
            
        self.contador_pestañas += 1
        nueva_pestaña = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(nueva_pestaña, text=f"Pedido {self.contador_pestañas}")
        self._crear_contenido_tab(nueva_pestaña)
        self.notebook.select(nueva_pestaña)

    def _crear_contenido_tab(self, tab_frame):
        """Crea el contenido de una pestaña"""
        widgets = {"clientes_map": {}}

        # Frame de búsqueda y cliente
        frame_busqueda = ttk.LabelFrame(tab_frame, text="1. Cliente y Búsqueda", padding="10")
        frame_busqueda.pack(fill="x")
        frame_busqueda.columnconfigure(1, weight=1)

        # Widgets de selección de cliente
        ttk.Label(frame_busqueda, text="Grupo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        widgets['combo_grupos'] = ttk.Combobox(frame_busqueda, values=list(self.grupos_data.keys()), state="readonly")
        widgets['combo_grupos'].grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame_busqueda, text="Cliente:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        widgets['combo_clientes'] = ttk.Combobox(frame_busqueda, state="disabled")
        widgets['combo_clientes'].grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Widgets de búsqueda
        ttk.Label(frame_busqueda, text="Buscar Producto:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        widgets['entry_busqueda'] = ttk.Entry(frame_busqueda)
        widgets['entry_busqueda'].grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        widgets['btn_buscar'] = ttk.Button(frame_busqueda, text="🔍 Buscar")
        widgets['btn_buscar'].grid(row=2, column=2, padx=5, pady=5)
        
        # Frame central para resultados y carrito
        frame_central = ttk.Frame(tab_frame)
        frame_central.pack(fill="both", expand=True, pady=10)
        frame_central.columnconfigure(0, weight=1)
        frame_central.columnconfigure(1, weight=2)
        frame_central.rowconfigure(1, weight=1)
        
        # Resultados de búsqueda
        ttk.Label(frame_central, text="Resultados de Búsqueda (Doble clic para agregar)").grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        
        # Frame para los resultados con scrollbar
        frame_resultados = ttk.Frame(frame_central)
        frame_resultados.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        frame_resultados.rowconfigure(0, weight=1)
        frame_resultados.columnconfigure(0, weight=1)
        
        # Modified: Added 'Es Especial' column for internal use, but not shown.
        cols_resultados = ("Producto", "Precio")
        widgets['tree_resultados'] = ttk.Treeview(
            frame_resultados, 
            columns=cols_resultados, 
            show="headings", 
            height=8
        )
        
        for col in cols_resultados: 
            widgets['tree_resultados'].heading(col, text=col)
        widgets['tree_resultados'].column("Precio", width=100, anchor="e")
        widgets['tree_resultados'].grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar para resultados
        scrollbar_resultados = ttk.Scrollbar(
            frame_resultados, 
            orient="vertical", 
            command=widgets['tree_resultados'].yview
        )
        widgets['tree_resultados'].configure(yscrollcommand=scrollbar_resultados.set)
        scrollbar_resultados.grid(row=0, column=1, sticky="ns")

        # **CARRITO CON SECCIONES**
        frame_carrito = ttk.LabelFrame(frame_central, text="Carrito de Compras", padding="5")
        frame_carrito.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(5, 0))
        
        # Crear el carrito con secciones
        widgets['carrito_obj'] = CarritoConSecciones(
            frame_carrito, 
            on_change_callback=lambda w=widgets: self._actualizar_total(w)
        )

        # Frame de total y acciones
        frame_acciones = ttk.LabelFrame(tab_frame, text="2. Total del Pedido", padding="10")
        frame_acciones.pack(fill="x", pady=(10, 0))
        
        # Total
        widgets['lbl_total_valor'] = ttk.Label(frame_acciones, text="$0.00", style="Total.TLabel")
        widgets['lbl_total_valor'].pack(side="right")
        ttk.Label(frame_acciones, text="Total:", style="Total.TLabel").pack(side="right", padx=(20, 5))
        
        # Contador de productos
        widgets['lbl_contador'] = ttk.Label(frame_acciones, text="0 productos")
        widgets['lbl_contador'].pack(side="left")
        
        # Frame de botones finales
        frame_final = ttk.LabelFrame(tab_frame, text="3. Finalizar Venta", padding="10")
        frame_final.pack(fill="x", pady=10)
        
        # Botones de acción
        frame_botones = ttk.Frame(frame_final)
        frame_botones.pack(fill="x")
        
        widgets['btn_limpiar'] = ttk.Button(
            frame_botones, 
            text="🗑️ Limpiar Carrito",
            command=lambda w=widgets: self._limpiar_carrito(w)
        )
        widgets['btn_limpiar'].pack(side="left", padx=(0, 10))

        # *** NUEVO BOTÓN DE EXCEL ***
        widgets['btn_generar_excel'] = ttk.Button(
        frame_botones, 
        text="📊 Generar Excel",
        command=lambda w=widgets: self._generar_excel(w)
        )
        widgets['btn_generar_excel'].pack(side="left", padx=(0, 10))
        
        widgets['btn_procesar_venta'] = ttk.Button(
            frame_botones, 
            text="✅ Registrar Venta y Generar Recibo",
            style="Accent.TButton"
        )
        widgets['btn_procesar_venta'].pack(side="right")

        # --- VINCULAR EVENTOS ---
        widgets['combo_grupos'].bind("<<ComboboxSelected>>", 
                                   lambda event, w=widgets: self._on_grupo_selected(event, w))
        widgets['btn_buscar'].config(command=lambda w=widgets: self._buscar_insumos(w))
        widgets['btn_procesar_venta'].config(command=lambda w=widgets: self._procesar_venta(w))
        widgets['tree_resultados'].bind("<Double-1>", 
                                      lambda event, w=widgets: self._abrir_ventana_cantidad(event, w))
        
        # Permitir búsqueda con Enter
        widgets['entry_busqueda'].bind("<Return>", 
                                     lambda event, w=widgets: self._buscar_insumos(w))

    def _abrir_ventana_cantidad(self, event, widgets):
        """Abre ventana para especificar cantidad y sección (si aplica)"""
        seleccion = widgets['tree_resultados'].focus()
        if not seleccion: 
            return

        # Modified: Retrieve all values, including the hidden 'es_especial' status.
        producto_info = widgets['tree_resultados'].item(seleccion, "values")
        # Ensure that producto_info has at least 3 elements (nombre, precio, es_especial, unidad)
        if len(producto_info) < 4:
            messagebox.showerror("Error", "Información del producto incompleta.")
            return

        nombre_prod = producto_info[0]
        precio_str = producto_info[1]
        es_especial = bool(int(producto_info[2])) # Convert '0' or '1' string to boolean
        unidad_producto = producto_info[3] 

        # Crear ventana de cantidad
        top = tk.Toplevel(self.root)
        top.title("Agregar Producto")
        top.geometry("350x250" if es_especial else "350x200") # Adjust size if price entry is shown
        top.resizable(False, False)
        top.transient(self.root)
        top.grab_set()

        # Información del producto
        ttk.Label(top, text=f"Producto: {nombre_prod}", 
                 font=("Helvetica", 10, "bold")).pack(pady=5)
        
        # Original price label, might be hidden or updated if 'es_especial'
        lbl_precio_actual = ttk.Label(top, text=f"Precio Base: {precio_str}", font=("Helvetica", 10))
        lbl_precio_actual.pack(pady=2)
        
        # Frame para cantidad
        frame_cantidad = ttk.Frame(top)
        frame_cantidad.pack(pady=5)
        
        ttk.Label(frame_cantidad, text="Cantidad:").pack(side="left", padx=5)
        entry_cantidad = ttk.Entry(frame_cantidad, width=10)
        entry_cantidad.pack(side="left", padx=5)
        entry_cantidad.focus()
        entry_cantidad.insert(0, "1.0")
        entry_cantidad.select_range(0, tk.END)

        # Modified: Price modification for special products
        entry_precio_modificable = None
        if es_especial:
            lbl_precio_actual.config(text=f"Precio Actual: {precio_str}") # Re-label for clarity
            
            frame_precio = ttk.Frame(top)
            frame_precio.pack(pady=5)
            
            ttk.Label(frame_precio, text="Nuevo Precio:").pack(side="left", padx=5)
            entry_precio_modificable = ttk.Entry(frame_precio, width=10)
            entry_precio_modificable.pack(side="left", padx=5)
            # Pre-fill with current price for easy modification
            entry_precio_modificable.insert(0, precio_str.replace('$', ''))
            
            ttk.Label(top, text="*Producto especial: puedes modificar el precio.", 
                     font=("Arial", 8), foreground="red").pack(pady=2)


        # Frame para sección (si está habilitado)
        frame_seccion = ttk.Frame(top)
        combo_seccion = None
        
        carrito = widgets['carrito_obj']
        if carrito.sectioning_enabled and carrito.secciones:
            frame_seccion.pack(pady=5)
            ttk.Label(frame_seccion, text="Sección:").pack(side="left", padx=5)
            
            secciones_nombres = [s.nombre for s in carrito.secciones.values()]
            combo_seccion = ttk.Combobox(frame_seccion, values=secciones_nombres, 
                                       state="readonly", width=15)
            combo_seccion.pack(side="left", padx=5)
            if secciones_nombres:
                combo_seccion.set(secciones_nombres[0])

        # Botones
        frame_botones = ttk.Frame(top)
        frame_botones.pack(pady=15)
        
        btn_aceptar = ttk.Button(
            frame_botones, 
            text="Agregar", 
            command=lambda: self._confirmar_agregar_al_carrito(
                nombre_prod, entry_cantidad.get(), 
                entry_precio_modificable.get() if es_especial and entry_precio_modificable else precio_str, # Pass potentially modified price
                unidad_producto,combo_seccion, top, widgets
            )
        )
        btn_aceptar.pack(side="left", padx=5)
        
        ttk.Button(frame_botones, text="Cancelar", command=top.destroy).pack(side="left", padx=5)
        
        # Permitir agregar con Enter
        entry_cantidad.bind("<Return>", 
                          lambda e: self._confirmar_agregar_al_carrito(
                              nombre_prod, entry_cantidad.get(), 
                              entry_precio_modificable.get() if es_especial and entry_precio_modificable else precio_str, # Pass potentially modified price
                              unidad_producto,combo_seccion, top, widgets
                          ))
        if es_especial and entry_precio_modificable:
            entry_precio_modificable.bind("<Return>", 
                                        lambda e: self._confirmar_agregar_al_carrito(
                                            nombre_prod, entry_cantidad.get(), 
                                            entry_precio_modificable.get() if es_especial and entry_precio_modificable else precio_str, # Pass potentially modified price
                                            unidad_producto,combo_seccion, top, widgets
                                        ))
    
    def _confirmar_agregar_al_carrito(self, nombre_prod, cantidad_str, precio_str_or_modified, unidad_producto, combo_seccion, toplevel, widgets):
        """Confirma y agrega el producto al carrito"""
        try:
            cantidad = float(cantidad_str)
            if cantidad <= 0: 
                raise ValueError("La cantidad debe ser positiva.")
        except ValueError:
            messagebox.showerror("Cantidad Inválida", 
                               "Introduce un número válido y positivo.", parent=toplevel)
            return

        try:
            # Use the passed price string, which might be the original or modified
            precio_unit = float(precio_str_or_modified.replace('$', '')) 
            if precio_unit < 0:
                raise ValueError("El precio no puede ser negativo.")
        except ValueError:
            messagebox.showerror("Precio Inválido", 
                               "Introduce un precio válido y no negativo.", parent=toplevel)
            return
        
        # Determinar sección si aplica
        seccion_id = None
        carrito = widgets['carrito_obj']
        
        if carrito.sectioning_enabled and combo_seccion:
            nombre_seccion = combo_seccion.get()
            for sid, seccion in carrito.secciones.items():
                if seccion.nombre == nombre_seccion:
                    seccion_id = sid
                    break
        
        # Agregar al carrito
        carrito.agregar_item(nombre_prod, cantidad, precio_unit, unidad_producto, seccion_id)
        toplevel.destroy()

    def _limpiar_carrito(self, widgets):
        """Limpia el carrito completo"""
        widgets['carrito_obj'].limpiar_carrito()

    def _actualizar_total(self, widgets):
        """Actualiza el total y contador del carrito"""
        carrito = widgets['carrito_obj']
        total = carrito.obtener_total()
        count = len(carrito.items)
        
        widgets['lbl_total_valor'].config(text=f"${total:.2f}")
        widgets['lbl_contador'].config(text=f"{count} producto{'s' if count != 1 else ''}")
    
    def _generar_excel(self, widgets):
            """Genera un archivo Excel con el contenido del carrito"""
            nombre_cliente = widgets['combo_clientes'].get()
            if not nombre_cliente:
                messagebox.showwarning("Falta Cliente", "Por favor, selecciona un cliente.")
                return

            carrito = widgets['carrito_obj']
            if not carrito.items:
                messagebox.showwarning("Carrito Vacío", "No hay productos en el carrito.")
                return
            
            total = carrito.obtener_total()
            
            if not messagebox.askyesno("Generar Excel", 
                                    f"¿Generar archivo Excel para '{nombre_cliente}'?\n\n"
                                    f"Total: ${total:.2f}"):
                return

            try:
                # Decidir qué tipo de Excel generar
                if carrito.sectioning_enabled and len(carrito.secciones) > 1:
                    # Generar Excel con secciones
                    items_por_seccion = carrito.obtener_items_por_seccion()
                    
                    # Verificar que realmente hay múltiples secciones con datos
                    secciones_con_datos = {k: v for k, v in items_por_seccion.items() if v['items']}
                    
                    if len(secciones_con_datos) > 1:
                        # Generar Excel con secciones
                        ruta_excel = generador_excel.crear_excel_con_secciones(
                            nombre_cliente, secciones_con_datos, total
                        )
                    else:
                        # Solo una sección con datos, usar formato simple
                        items_carrito = carrito.obtener_items()
                        ruta_excel = generador_excel.crear_excel_simple(
                            nombre_cliente, items_carrito
                        )
                else:
                    # Generar Excel simple
                    items_carrito = carrito.obtener_items()
                    ruta_excel = generador_excel.crear_excel_simple(
                        nombre_cliente, items_carrito
                    )
                
                if ruta_excel:
                    messagebox.showinfo("Excel Generado", 
                                    f"Archivo Excel generado exitosamente!\n\n"
                                    f"Guardado en: {ruta_excel}")
                else:
                    messagebox.showerror("Error", "No se pudo generar el archivo Excel.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar Excel: {str(e)}")


    def _procesar_venta(self, widgets):
        """Procesa la venta y genera el recibo"""
        nombre_cliente = widgets['combo_clientes'].get()
        if not nombre_cliente:
            messagebox.showwarning("Falta Cliente", "Por favor, selecciona un cliente.")
            return

        carrito = widgets['carrito_obj']
        if not carrito.items:
            messagebox.showwarning("Carrito Vacío", "No hay productos en el carrito.")
            return
        
        total = carrito.obtener_total()
        
        if not messagebox.askyesno("Confirmar Venta", 
                                  f"¿Registrar esta venta para '{nombre_cliente}'?\n\n"
                                  f"Total: ${total:.2f}"):
            return

        try:
            id_cliente = widgets['clientes_map'][nombre_cliente]
            
            # Decidir qué tipo de recibo generar
            if carrito.sectioning_enabled and len(carrito.secciones) > 1:
                # Generar recibo con secciones
                items_por_seccion = carrito.obtener_items_por_seccion()
                
                # Verificar que realmente hay múltiples secciones con datos
                secciones_con_datos = {k: v for k, v in items_por_seccion.items() if v['items']}
                
                if len(secciones_con_datos) > 1:
                    # Registrar en BD (formato simple para compatibilidad)
                    items_simple = []
                    for datos_seccion in secciones_con_datos.values():
                        items_simple.extend(datos_seccion['items'])
                    
                    resultado_factura = database.crear_factura_completa(id_cliente, items_simple)
                    
                    if resultado_factura:
                        id_factura = resultado_factura['id_factura']
                        folio_numero = resultado_factura['folio_numero']
                        
                        # Generar PDF con secciones y folio
                        ruta_pdf = generador_pdf.crear_recibo_con_secciones(
                            nombre_cliente, secciones_con_datos, total, folio_numero
                        )
                    else:
                        id_factura = None
                        ruta_pdf = None
                else:
                    # Solo una sección con datos, usar formato simple
                    items_carrito = carrito.obtener_items()
                    resultado_factura = database.crear_factura_completa(id_cliente, items_carrito)
                    
                    if resultado_factura:
                        id_factura = resultado_factura['id_factura']
                        folio_numero = resultado_factura['folio_numero']
                        
                        ruta_pdf = generador_pdf.crear_recibo_simple(
                            nombre_cliente, items_carrito, f"${total:.2f}", folio_numero
                        )
                    else:
                        id_factura = None
                        ruta_pdf = None
            else:
                # Generar recibo simple
                items_carrito = carrito.obtener_items()
                resultado_factura = database.crear_factura_completa(id_cliente, items_carrito)
                
                if resultado_factura:
                    id_factura = resultado_factura['id_factura']
                    folio_numero = resultado_factura['folio_numero']
                    
                    ruta_pdf = generador_pdf.crear_recibo_simple(
                        nombre_cliente, items_carrito, f"${total:.2f}", folio_numero
                    )
                else:
                    id_factura = None
                    ruta_pdf = None
            
            if id_factura and ruta_pdf:
                messagebox.showinfo("Éxito", 
                                  f"Venta registrada exitosamente!\n\n"
                                  f"Factura ID: {id_factura}\n"
                                  f"Folio: {folio_numero:06d}\n"
                                  f"PDF guardado en: {ruta_pdf}")
                
                # Limpiar carrito
                carrito.limpiar_carrito()
            else:
                messagebox.showerror("Error", "No se pudo completar la transacción.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la venta: {str(e)}")

    def _on_grupo_selected(self, event, widgets):
        """Maneja la selección de grupo"""
        widgets['combo_clientes'].set('')
        widgets['combo_clientes']['values'] = []
        
        # Limpiar resultados
        for item in widgets['tree_resultados'].get_children(): 
            widgets['tree_resultados'].delete(item)
        
        nombre_grupo = widgets['combo_grupos'].get()
        id_grupo = self.grupos_data.get(nombre_grupo)
        
        if id_grupo:
            clientes = database.obtener_clientes_por_grupo(id_grupo)
            widgets['clientes_map'] = {nombre: c_id for c_id, nombre in clientes}
            widgets['combo_clientes']['values'] = list(widgets['clientes_map'].keys())
            widgets['combo_clientes'].config(state="readonly")
        else:
            widgets['combo_clientes'].config(state="disabled")

    def _buscar_insumos(self, widgets):
        """Busca productos en la base de datos"""
        nombre_grupo = widgets['combo_grupos'].get()
        if not nombre_grupo:
            messagebox.showwarning("Falta Grupo", "Por favor, selecciona un grupo.")
            return
            
        id_grupo = self.grupos_data[nombre_grupo]
        texto_busqueda = widgets['entry_busqueda'].get()
        
        # Limpiar resultados anteriores
        for item in widgets['tree_resultados'].get_children(): 
            widgets['tree_resultados'].delete(item)
        
        # Modified: Pass the es_especial status along with product name and price
        productos = database.buscar_productos_por_grupo_con_especial(id_grupo, texto_busqueda)
        
        if productos:
            for nombre, precio, es_especial, unidad in productos:
                # Store es_especial as a hidden value in the treeview item
                widgets['tree_resultados'].insert("", "end", values=(nombre, f"${precio:.2f}", es_especial, unidad))
        else:
            # Mostrar mensaje si no hay resultados
            widgets['tree_resultados'].insert("", "end", values=("No se encontraron productos", "", "", ""))

    def run(self):
        """Run the application main loop"""
        if self.root:
            self.root.mainloop()

if __name__ == "__main__":
    app = ReciboAppMejorado()
    app.run()