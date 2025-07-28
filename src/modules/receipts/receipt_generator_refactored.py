# receipt_generator_refactored.py
# Versión actualizada que integra el sistema de órdenes guardadas

import tkinter as tk
from tkinter import ttk, messagebox
from src.modules.receipts.components import database
from src.modules.receipts.components import generador_pdf as generador_pdf
from src.modules.receipts.components.carrito_module import CarritoConSecciones, DialogoSeccion
from src.modules.receipts.components import generador_excel
from src.modules.receipts.components.orden_manager import obtener_manager, OrdenManager
from src.modules.receipts.components.ventana_ordenes import abrir_ventana_ordenes

class ReciboAppMejorado:
    def __init__(self, parent=None, user_data=None, orden_folio=None):
        """
        Inicializa la aplicación de recibos con soporte para órdenes guardadas.
        
        Args:
            parent: Ventana padre
            user_data: Datos del usuario autenticado
            orden_folio: Folio de orden existente a cargar (opcional)
        """
        self.root = parent if parent else tk.Tk()
        self.user_data = user_data or {}
        
        # Detectar si estamos en contexto de launcher (parent existe = Toplevel window)
        self.is_launcher_context = parent is not None
        
        # Atributos para órdenes guardadas
        self.folio_actual = orden_folio
        self.orden_guardada = None
        self.orden_manager = obtener_manager()
        
        # Configuración de usuario
        self.username = self.user_data.get('username', 'usuario')
        self.es_admin = self.user_data.get('rol', '').lower() == 'admin'
        
        self.root.title("Disfruleg - Sistema de Ventas con Órdenes Guardadas")
        self.root.geometry("1100x750")

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.style.configure("Total.TLabel", font=("Helvetica", 12, "bold"))
        self.style.configure("Success.TButton", foreground="white")
        
        # Crear canvas scrolleable para todo el contenido
        self._setup_scrollable_interface()

        self.grupos_data = {nombre: g_id for g_id, nombre in database.obtener_grupos()}
        if not self.grupos_data:
            messagebox.showerror("Error de Base de Datos", "No se pudieron cargar los grupos de clientes.")
            if parent is None:
                self.root.destroy()
            return
            
        self.contador_pestañas = 0
        self._crear_widgets_principales()
        self._agregar_pestaña()
        
        # Cargar orden existente si se especificó
        if self.folio_actual:
            self._cargar_orden_al_inicio()
    
    def _setup_scrollable_interface(self):
        """Configura la interfaz scrolleable con Canvas y Scrollbar"""
        # Crear el canvas principal que ocupará toda la ventana
        self.main_canvas = tk.Canvas(self.root, highlightthickness=0)
        
        # Crear scrollbar vertical
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        
        # Crear frame scrolleable que contendrá todo el contenido
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        
        # Configurar el scrolling
        def on_frame_configure(event):
            # Actualizar scroll region
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
            # Mostrar/ocultar scrollbar según sea necesario
            self._update_scrollbar_visibility()
        
        self.scrollable_frame.bind("<Configure>", on_frame_configure)
        
        # Crear ventana en el canvas para el frame scrolleable
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configurar el scrollbar
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack del canvas y scrollbar
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind para redimensionar el frame scrolleable cuando cambia el canvas
        def on_canvas_configure(event):
            self._on_canvas_configure(event)
            self._update_scrollbar_visibility()
        
        self.main_canvas.bind("<Configure>", on_canvas_configure)
        
        # Bind para mouse wheel scrolling
        self._bind_mousewheel()
    
    def _update_scrollbar_visibility(self):
        """Muestra u oculta la scrollbar según sea necesario"""
        try:
            bbox = self.main_canvas.bbox("all")
            if bbox:
                content_height = bbox[3] - bbox[1]
                canvas_height = self.main_canvas.winfo_height()
                
                # Si el contenido es más alto que el canvas, mostrar scrollbar
                if content_height > canvas_height:
                    if not self.scrollbar.winfo_viewable():
                        self.scrollbar.pack(side="right", fill="y")
                else:
                    # Si el contenido cabe, ocultar scrollbar
                    if self.scrollbar.winfo_viewable():
                        self.scrollbar.pack_forget()
                        # Resetear scroll position al inicio
                        self.main_canvas.yview_moveto(0)
        except (tk.TclError, AttributeError):
            # Ignorar errores durante la inicialización
            pass
    
    def _on_canvas_configure(self, event):
        """Ajusta el ancho del frame scrolleable al ancho del canvas"""
        canvas_width = event.width
        self.main_canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def _bind_mousewheel(self):
        """Configura el scroll con mouse wheel"""
        def _on_mousewheel(event):
            # Solo hacer scroll si hay contenido que excede la vista
            bbox = self.main_canvas.bbox("all")
            if bbox and bbox[3] > self.main_canvas.winfo_height():
                # Scroll más suave ajustando la velocidad
                delta = -1 * (event.delta / 120) if hasattr(event, 'delta') else -1 if event.num == 4 else 1
                self.main_canvas.yview_scroll(int(delta), "units")
        
        def _on_mousewheel_linux(event):
            # Manejo específico para Linux
            bbox = self.main_canvas.bbox("all")
            if bbox and bbox[3] > self.main_canvas.winfo_height():
                if event.num == 4:
                    self.main_canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.main_canvas.yview_scroll(1, "units")
        
        # Función para aplicar bindings a un widget y sus hijos
        def bind_to_mousewheel(widget):
            # Windows/Mac
            widget.bind("<MouseWheel>", _on_mousewheel)
            # Linux
            widget.bind("<Button-4>", _on_mousewheel_linux)
            widget.bind("<Button-5>", _on_mousewheel_linux)
            
            # Aplicar recursivamente a todos los widgets hijos
            for child in widget.winfo_children():
                bind_to_mousewheel(child)
        
        # Aplicar bindings al canvas y frame scrolleable
        bind_to_mousewheel(self.main_canvas)
        bind_to_mousewheel(self.root)
        
        # También bindear cuando se agreguen nuevos widgets
        original_bind = self.scrollable_frame.bind
        def enhanced_bind(*args, **kwargs):
            result = original_bind(*args, **kwargs)
            # Re-aplicar mouse wheel bindings cuando se modifique el contenido
            self.root.after_idle(lambda: bind_to_mousewheel(self.scrollable_frame))
            return result
        self.scrollable_frame.bind = enhanced_bind

    def _cargar_orden_al_inicio(self):
        """Carga una orden existente al inicializar la aplicación"""
        try:
            # Cargar datos de la orden
            self.orden_guardada = self.orden_manager.cargar_orden(self.folio_actual)
            
            if self.orden_guardada:
                # Obtener la primera pestaña (que acabamos de crear)
                primera_pestaña = list(self.notebook.tabs())[0]
                widgets = getattr(self, f'widgets_{primera_pestaña.split(".")[-1]}', None)
                
                if widgets:
                    # Usar root.after para asegurar que la interfaz esté completamente inicializada
                    self.root.after(100, lambda: self._cargar_orden_existente(self.folio_actual, widgets))
                    
                    # Actualizar título de la ventana
                    self.root.title(f"Disfruleg - Editando Orden {self.folio_actual:06d}")
            else:
                messagebox.showerror("Error", f"No se pudo cargar la orden con folio {self.folio_actual}")
                self.folio_actual = None
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar orden: {str(e)}")
            self.folio_actual = None

    def _crear_widgets_principales(self):
        """Crea los widgets principales de la aplicación"""
        frame_superior = ttk.Frame(self.scrollable_frame, padding=(10, 10, 10, 0))
        frame_superior.pack(fill="x")
        
        # Información de orden actual
        info_frame = ttk.Frame(frame_superior)
        info_frame.pack(fill="x")
        
        # Label para mostrar información de la orden
        self.lbl_orden_info = ttk.Label(
            info_frame, 
            text="Nueva Orden", 
            font=("Arial", 12, "bold"),
            foreground="blue"
        )
        self.lbl_orden_info.pack(side="left")
        
        btn_agregar_tab = ttk.Button(
            info_frame, 
            text="➕ Agregar Nuevo Pedido", 
            command=self._agregar_pestaña
        )
        btn_agregar_tab.pack(side="right")
        
        # Información sobre secciones
        info_label = ttk.Label(
            frame_superior, 
            text="💡 Tip: Active 'Habilitar Secciones' para organizar productos por categorías",
            font=("Arial", 9),
            foreground="gray"
        )
        info_label.pack(pady=(5, 0))
        
        self.notebook = ttk.Notebook(self.scrollable_frame)
        self.notebook.pack(pady=(5, 10), padx=10, expand=True, fill="both")

    def _agregar_pestaña(self):
        """Agrega una nueva pestaña de pedido"""
        if self.contador_pestañas >= 5:
            messagebox.showinfo("Límite Alcanzado", "No se pueden agregar más de 5 pedidos.")
            return
            
        self.contador_pestañas += 1
        nueva_pestaña = ttk.Frame(self.notebook, padding="10")
        
        # Determinar título de la pestaña
        if self.folio_actual and self.contador_pestañas == 1:
            titulo_tab = f"Orden {self.folio_actual:06d}"
        else:
            titulo_tab = f"Pedido {self.contador_pestañas}"
            
        self.notebook.add(nueva_pestaña, text=titulo_tab)
        widgets = self._crear_contenido_tab(nueva_pestaña)
        
        # Guardar referencia a los widgets de esta pestaña
        tab_id = nueva_pestaña.winfo_name()
        setattr(self, f'widgets_{tab_id}', widgets)
        
        self.notebook.select(nueva_pestaña)
        return widgets

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
        
        # *** BOTONES EXISTENTES Y NUEVOS ***
        frame_botones = ttk.Frame(frame_final)
        frame_botones.pack(fill="x")
        
        # Fila superior - Acciones de orden
        frame_botones_superior = ttk.Frame(frame_botones)
        frame_botones_superior.pack(fill="x", pady=(0, 10))
        
        # NUEVOS BOTONES DE ÓRDENES
        widgets['btn_guardar_orden'] = ttk.Button(
            frame_botones_superior, 
            text="💾 Guardar Orden",
            command=lambda w=widgets: self._guardar_orden_actual(w),
            style="Success.TButton"
        )
        widgets['btn_guardar_orden'].pack(side="left", padx=(0, 10))
        
        widgets['btn_ver_ordenes'] = ttk.Button(
            frame_botones_superior, 
            text="📋 Ver Órdenes",
            command=self._abrir_ventana_ordenes
        )
        widgets['btn_ver_ordenes'].pack(side="left", padx=(0, 10))
        
        # Separador visual
        ttk.Separator(frame_botones_superior, orient="vertical").pack(side="left", fill="y", padx=10)
        
        # Información de orden actual
        widgets['lbl_folio_info'] = ttk.Label(
            frame_botones_superior, 
            text="Nueva orden", 
            font=("Arial", 10, "italic"),
            foreground="blue"
        )
        widgets['lbl_folio_info'].pack(side="left", padx=(10, 0))
        
        # Fila inferior - Acciones tradicionales
        frame_botones_inferior = ttk.Frame(frame_botones)
        frame_botones_inferior.pack(fill="x")
        
        widgets['btn_limpiar'] = ttk.Button(
            frame_botones_inferior, 
            text="🗑️ Limpiar Carrito",
            command=lambda w=widgets: self._limpiar_carrito(w)
        )
        widgets['btn_limpiar'].pack(side="left", padx=(0, 10))

        widgets['btn_generar_excel'] = ttk.Button(
            frame_botones_inferior, 
            text="📊 Generar Excel",
            command=lambda w=widgets: self._generar_excel(w)
        )
        widgets['btn_generar_excel'].pack(side="left", padx=(0, 10))
        
        widgets['btn_generar_pdf'] = ttk.Button(
            frame_botones_inferior, 
            text="📄 Generar PDF",
            command=lambda w=widgets: self._generar_pdf_solo(w)
        )
        widgets['btn_generar_pdf'].pack(side="left", padx=(0, 10))
        
        widgets['btn_procesar_venta'] = ttk.Button(
            frame_botones_inferior, 
            text="✅ Registrar Venta",
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

        return widgets

    # ==================== NUEVOS MÉTODOS PARA ÓRDENES GUARDADAS ====================

    def _guardar_orden_actual(self, widgets):
        """Guarda el estado actual del carrito como una orden"""
        try:
            # Verificar que hay cliente seleccionado
            nombre_cliente = widgets['combo_clientes'].get()
            if not nombre_cliente:
                messagebox.showwarning("Falta Cliente", "Por favor, selecciona un cliente antes de guardar.")
                return

            # Verificar que el carrito no está vacío
            carrito = widgets['carrito_obj']
            if not carrito.items:
                messagebox.showwarning("Carrito Vacío", "No hay productos en el carrito para guardar.")
                return

            id_cliente = widgets['clientes_map'][nombre_cliente]
            total = carrito.obtener_total()

            # Si no tiene folio, obtener uno nuevo con reintentos
            if not self.folio_actual:
                max_reintentos = 5
                for intento in range(max_reintentos):
                    folio_sugerido = self.orden_manager.obtener_siguiente_folio_disponible()
                    if not folio_sugerido:
                        messagebox.showerror("Error", "No se pudo obtener un folio disponible.")
                        return
                    
                    # Verificar que el folio esté realmente disponible
                    if self.orden_manager._verificar_folio_disponible(folio_sugerido):
                        self.folio_actual = folio_sugerido
                        break
                    else:
                        print(f"Folio {folio_sugerido} ya no está disponible, reintentando... ({intento + 1}/{max_reintentos})")
                        if intento == max_reintentos - 1:
                            messagebox.showerror("Error", 
                                               f"No se pudo obtener un folio disponible después de {max_reintentos} intentos. "
                                               f"Por favor, inténtelo de nuevo.")
                            return

            # Serializar estado del carrito
            datos_carrito = self._serializar_estado_carrito(widgets)

            # Guardar en base de datos
            if self.orden_guardada:
                # Actualizar orden existente
                exito = self.orden_manager.actualizar_orden(self.folio_actual, datos_carrito, total)
                mensaje_exito = "Orden actualizada exitosamente"
            else:
                # Crear nueva orden con manejo de race conditions
                exito = False
                max_reintentos_reserva = 3
                
                for intento_reserva in range(max_reintentos_reserva):
                    exito = self.orden_manager.reservar_folio(
                        self.folio_actual, id_cliente, self.username, datos_carrito, total
                    )
                    
                    if exito:
                        mensaje_exito = "Orden guardada exitosamente"
                        break
                    else:
                        print(f"Fallo al reservar folio {self.folio_actual}, intento {intento_reserva + 1}/{max_reintentos_reserva}")
                        
                        # Si no es el último intento, obtener un nuevo folio
                        if intento_reserva < max_reintentos_reserva - 1:
                            nuevo_folio = self.orden_manager.obtener_siguiente_folio_disponible()
                            if nuevo_folio and nuevo_folio != self.folio_actual:
                                self.folio_actual = nuevo_folio
                                print(f"Intentando con nuevo folio: {self.folio_actual}")
                            else:
                                print("No se pudo obtener un folio alternativo")
                                break

            if exito:
                # Marcar como orden guardada
                self.orden_guardada = True
                
                # Actualizar interfaz
                widgets['lbl_folio_info'].config(
                    text=f"Orden guardada - Folio: {self.folio_actual:06d}",
                    foreground="green"
                )
                
                # Actualizar título de ventana y pestaña
                self.root.title(f"Disfruleg - Editando Orden {self.folio_actual:06d}")
                tab_actual = self.notebook.select()
                self.notebook.tab(tab_actual, text=f"Orden {self.folio_actual:06d}")
                
                # Actualizar label principal
                self.lbl_orden_info.config(
                    text=f"Editando Orden {self.folio_actual:06d}",
                    foreground="green"
                )

                messagebox.showinfo("Éxito", 
                                  f"{mensaje_exito}\n\n"
                                  f"Folio asignado: {self.folio_actual:06d}\n"
                                  f"Cliente: {nombre_cliente}\n"
                                  f"Total: ${total:.2f}")
                
                # Notificar al padre sobre el cambio si estamos en contexto de launcher
                if self.is_launcher_context:
                    self._notificar_cambio_orden()
            else:
                messagebox.showerror("Error", "No se pudo guardar la orden.")

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar orden: {str(e)}")
    
    def _notificar_cambio_orden(self):
        """Notifica a la ventana principal sobre cambios en la orden"""
        try:
            # Crear evento personalizado en la ventana raíz
            if hasattr(self.root, 'master') and self.root.master:
                self.root.master.event_generate("<<OrdenCambiada>>")
                print("📤 Notificación de cambio de orden enviada")
        except Exception as e:
            print(f"Error al notificar cambio de orden: {e}")

    def _cargar_orden_existente(self, folio, widgets):
        """Carga una orden existente en la interfaz"""
        try:
            # Cargar datos de la orden
            orden_data = self.orden_manager.cargar_orden(folio)
            
            if not orden_data:
                messagebox.showerror("Error", f"No se encontró la orden con folio {folio}")
                return False

            # Actualizar estado interno
            self.folio_actual = folio
            self.orden_guardada = True

            # Restaurar cliente seleccionado
            id_cliente = orden_data['id_cliente']
            nombre_cliente = orden_data['nombre_cliente']
            
            # Buscar y seleccionar el grupo del cliente
            grupo_encontrado = None
            for nombre_grupo, id_grupo in self.grupos_data.items():
                clientes = database.obtener_clientes_por_grupo(id_grupo)
                if any(c_id == id_cliente for c_id, c_nombre in clientes):
                    grupo_encontrado = nombre_grupo
                    break
            
            if grupo_encontrado:
                # Seleccionar grupo
                widgets['combo_grupos'].set(grupo_encontrado)
                self._on_grupo_selected(None, widgets)
                
                # Seleccionar cliente
                widgets['combo_clientes'].set(nombre_cliente)

            # Restaurar estado del carrito
            datos_carrito_obj = orden_data.get('datos_carrito_obj')
            if datos_carrito_obj:
                OrdenManager.json_a_carrito(datos_carrito_obj, widgets['carrito_obj'])
            
            # Actualizar interfaz
            widgets['lbl_folio_info'].config(
                text=f"Orden cargada - Folio: {folio:06d}",
                foreground="green"
            )
            
            self.lbl_orden_info.config(
                text=f"Editando Orden {folio:06d}",
                foreground="green"
            )

            # Actualizar total
            self._actualizar_total(widgets)

            print(f"Orden {folio} cargada exitosamente")
            return True

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar orden: {str(e)}")
            return False

    def _serializar_estado_carrito(self, widgets):
        """Convierte el estado actual del carrito a formato JSON serializable"""
        try:
            carrito = widgets['carrito_obj']
            
            # Obtener información del cliente
            nombre_cliente = widgets['combo_clientes'].get()
            id_cliente = widgets['clientes_map'].get(nombre_cliente)
            
            # Usar el método estático del OrdenManager
            datos_carrito = OrdenManager.carrito_a_json(carrito)
            
            # Agregar información adicional
            datos_carrito['cliente_info'] = {
                'id_cliente': id_cliente,
                'nombre_cliente': nombre_cliente,
                'grupo_seleccionado': widgets['combo_grupos'].get()
            }
            
            return datos_carrito

        except Exception as e:
            print(f"Error al serializar carrito: {e}")
            return {}

    def _abrir_ventana_ordenes(self):
        """Abre la ventana de gestión de órdenes o retorna al hub del launcher"""
        try:
            # Si estamos en contexto de launcher, simplemente cerrar esta ventana
            # para retornar al hub principal de VentanaOrdenes
            if self.is_launcher_context:
                print("🔄 Retornando al hub principal de órdenes...")
                self.root.destroy()
                return
            
            # Si no estamos en contexto de launcher, usar el comportamiento original
            # Callbacks para la ventana de órdenes
            def callback_nueva_orden():
                # Cerrar ventana actual si es modal
                if hasattr(self, '_ventana_ordenes'):
                    self._ventana_ordenes.destroy()
                
                # Crear nueva instancia sin folio
                nueva_app = ReciboAppMejorado(
                    parent=self.root.master if self.root.master else None,
                    user_data=self.user_data
                )
                
                # Cerrar ventana actual
                self.root.destroy()
                
                # Mostrar nueva ventana
                nueva_app.run()

            def callback_editar_orden(folio):
                # Cerrar ventana de órdenes si existe
                if hasattr(self, '_ventana_ordenes'):
                    self._ventana_ordenes.destroy()
                
                # Crear nueva instancia con el folio específico
                nueva_app = ReciboAppMejorado(
                    parent=self.root.master if self.root.master else None,
                    user_data=self.user_data,
                    orden_folio=folio
                )
                
                # Cerrar ventana actual
                self.root.destroy()
                
                # Mostrar nueva ventana
                nueva_app.run()

            # Abrir ventana de órdenes (solo en modo standalone)
            self._ventana_ordenes = abrir_ventana_ordenes(
                parent=self.root,
                user_data=self.user_data,
                on_nueva_orden=callback_nueva_orden,
                on_editar_orden=callback_editar_orden
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir ventana de órdenes: {str(e)}")

    # ==================== MÉTODOS EXISTENTES (MODIFICADOS PARA ÓRDENES) ====================

    def _procesar_venta(self, widgets):
        """Registra la venta en la base de datos y opcionalmente genera PDF"""
        nombre_cliente = widgets['combo_clientes'].get()
        if not nombre_cliente:
            messagebox.showwarning("Falta Cliente", "Por favor, selecciona un cliente.")
            return

        carrito = widgets['carrito_obj']
        if not carrito.items:
            messagebox.showwarning("Carrito Vacío", "No hay productos en el carrito.")
            return
        
        total = carrito.obtener_total()
        
        # Mensaje diferente si es una orden guardada
        if self.folio_actual and self.orden_guardada:
            mensaje_confirmacion = f"¿Registrar la orden {self.folio_actual:06d} como venta completada?\n\n"
        else:
            mensaje_confirmacion = f"¿Registrar esta venta para '{nombre_cliente}'?\n\n"
        
        mensaje_confirmacion += f"Total: ${total:.2f}"
        
        if not messagebox.askyesno("Confirmar Venta", mensaje_confirmacion):
            return

        try:
            id_cliente = widgets['clientes_map'][nombre_cliente]
            
            # Preparar items para registrar en BD
            if carrito.sectioning_enabled and len(carrito.secciones) > 1:
                items_por_seccion = carrito.obtener_items_por_seccion()
                secciones_con_datos = {k: v for k, v in items_por_seccion.items() if v['items']}
                
                if len(secciones_con_datos) > 1:
                    items_simple = []
                    for datos_seccion in secciones_con_datos.values():
                        items_simple.extend(datos_seccion['items'])
                    items_carrito = items_simple
                else:
                    items_carrito = carrito.obtener_items()
            else:
                items_carrito = carrito.obtener_items()
            
            # Si es una orden guardada, usar su folio y marcarla como registrada
            if self.folio_actual and self.orden_guardada:
                # Registrar venta en base de datos con el folio específico
                resultado_factura = database.crear_factura_completa(id_cliente, items_carrito)
                
                if resultado_factura:
                    # Marcar orden como registrada
                    self.orden_manager.marcar_como_registrada(self.folio_actual)
                    
                    id_factura = resultado_factura['id_factura']
                    folio_numero = self.folio_actual  # Usar el folio de la orden
                    
                    mensaje_exito = (f"Orden {self.folio_actual:06d} registrada como venta!\n\n"
                                   f"Factura ID: {id_factura}")
                else:
                    messagebox.showerror("Error", "No se pudo registrar la venta en la base de datos.")
                    return
            else:
                # Registrar venta normal
                resultado_factura = database.crear_factura_completa(id_cliente, items_carrito)
                
                if resultado_factura:
                    id_factura = resultado_factura['id_factura']
                    folio_numero = resultado_factura['folio_numero']
                    
                    mensaje_exito = (f"Venta registrada exitosamente!\n\n"
                                   f"Factura ID: {id_factura}\n"
                                   f"Folio: {folio_numero:06d}")
                else:
                    messagebox.showerror("Error", "No se pudo registrar la venta en la base de datos.")
                    return
            
            # Preguntar si también quiere generar PDF
            generar_pdf = messagebox.askyesno("Generar PDF", 
                                            f"{mensaje_exito}\n\n"
                                            f"¿Desea generar también el PDF del recibo?")
            
            ruta_pdf = None
            if generar_pdf:
                # Generar PDF con el folio asignado
                if carrito.sectioning_enabled and len(carrito.secciones) > 1:
                    items_por_seccion = carrito.obtener_items_por_seccion()
                    secciones_con_datos = {k: v for k, v in items_por_seccion.items() if v['items']}
                    
                    if len(secciones_con_datos) > 1:
                        ruta_pdf = generador_pdf.crear_recibo_con_secciones(
                            nombre_cliente, secciones_con_datos, total, folio_numero
                        )
                    else:
                        ruta_pdf = generador_pdf.crear_recibo_simple(
                            nombre_cliente, items_carrito, f"${total:.2f}", folio_numero
                        )
                else:
                    ruta_pdf = generador_pdf.crear_recibo_simple(
                        nombre_cliente, items_carrito, f"${total:.2f}", folio_numero
                    )
            
            # Mostrar mensaje final
            mensaje_final = mensaje_exito
            if ruta_pdf:
                mensaje_final += f"\nPDF guardado en: {ruta_pdf}"
            
            messagebox.showinfo("Éxito", mensaje_final)
            
            # Limpiar carrito y resetear estado
            carrito.limpiar_carrito()
            self._resetear_estado_orden(widgets)
            
            # Notificar cambio si estamos en contexto de launcher
            if self.is_launcher_context:
                self._notificar_cambio_orden()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la venta: {str(e)}")

    def _resetear_estado_orden(self, widgets):
        """Resetea el estado de la orden después de completar una venta"""
        self.folio_actual = None
        self.orden_guardada = None
        
        # Actualizar interfaz
        widgets['lbl_folio_info'].config(
            text="Nueva orden",
            foreground="blue"
        )
        
        self.lbl_orden_info.config(
            text="Nueva Orden",
            foreground="blue"
        )
        
        # Actualizar título de ventana y pestaña
        self.root.title("Disfruleg - Sistema de Ventas con Órdenes Guardadas")
        tab_actual = self.notebook.select()
        tab_index = self.notebook.index(tab_actual)
        self.notebook.tab(tab_actual, text=f"Pedido {tab_index + 1}")

    # ==================== MÉTODOS EXISTENTES (SIN CAMBIOS) ====================

    def _abrir_ventana_cantidad(self, event, widgets):
        """Abre ventana para especificar cantidad y sección (si aplica)"""
        seleccion = widgets['tree_resultados'].focus()
        if not seleccion: 
            return

        producto_info = widgets['tree_resultados'].item(seleccion, "values")
        if len(producto_info) < 4:
            messagebox.showerror("Error", "Información del producto incompleta.")
            return

        nombre_prod = producto_info[0]
        precio_str = producto_info[1]
        es_especial = bool(int(producto_info[2]))
        unidad_producto = producto_info[3] 

        # Crear ventana de cantidad
        top = tk.Toplevel(self.root)
        top.title("Agregar Producto")
        top.geometry("350x250" if es_especial else "350x200")
        top.resizable(False, False)
        top.transient(self.root)
        top.grab_set()

        # Información del producto
        ttk.Label(top, text=f"Producto: {nombre_prod}", 
                 font=("Helvetica", 10, "bold")).pack(pady=5)
        
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

        entry_precio_modificable = None
        if es_especial:
            lbl_precio_actual.config(text=f"Precio Actual: {precio_str}")
            
            frame_precio = ttk.Frame(top)
            frame_precio.pack(pady=5)
            
            ttk.Label(frame_precio, text="Nuevo Precio:").pack(side="left", padx=5)
            entry_precio_modificable = ttk.Entry(frame_precio, width=10)
            entry_precio_modificable.pack(side="left", padx=5)
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
                entry_precio_modificable.get() if es_especial and entry_precio_modificable else precio_str,
                unidad_producto, combo_seccion, top, widgets
            )
        )
        btn_aceptar.pack(side="left", padx=5)
        
        ttk.Button(frame_botones, text="Cancelar", command=top.destroy).pack(side="left", padx=5)
        
        # Permitir agregar con Enter
        entry_cantidad.bind("<Return>", 
                          lambda e: self._confirmar_agregar_al_carrito(
                              nombre_prod, entry_cantidad.get(), 
                              entry_precio_modificable.get() if es_especial and entry_precio_modificable else precio_str,
                              unidad_producto, combo_seccion, top, widgets
                          ))
        if es_especial and entry_precio_modificable:
            entry_precio_modificable.bind("<Return>", 
                                        lambda e: self._confirmar_agregar_al_carrito(
                                            nombre_prod, entry_cantidad.get(), 
                                            entry_precio_modificable.get() if es_especial and entry_precio_modificable else precio_str,
                                            unidad_producto, combo_seccion, top, widgets
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
            if carrito.sectioning_enabled and len(carrito.secciones) > 1:
                items_por_seccion = carrito.obtener_items_por_seccion()
                secciones_con_datos = {k: v for k, v in items_por_seccion.items() if v['items']}
                
                if len(secciones_con_datos) > 1:
                    ruta_excel = generador_excel.crear_excel_con_secciones(
                        nombre_cliente, secciones_con_datos, total
                    )
                else:
                    items_carrito = carrito.obtener_items()
                    ruta_excel = generador_excel.crear_excel_simple(
                        nombre_cliente, items_carrito
                    )
            else:
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

    def _generar_pdf_solo(self, widgets):
        """Genera solo el PDF sin registrar la venta en la base de datos"""
        nombre_cliente = widgets['combo_clientes'].get()
        if not nombre_cliente:
            messagebox.showwarning("Falta Cliente", "Por favor, selecciona un cliente.")
            return

        carrito = widgets['carrito_obj']
        if not carrito.items:
            messagebox.showwarning("Carrito Vacío", "No hay productos en el carrito.")
            return
        
        total = carrito.obtener_total()
        
        if not messagebox.askyesno("Generar PDF", 
                                  f"¿Generar PDF para '{nombre_cliente}' sin registrar la venta?\n\n"
                                  f"Total: ${total:.2f}"):
            return

        try:
            if carrito.sectioning_enabled and len(carrito.secciones) > 1:
                items_por_seccion = carrito.obtener_items_por_seccion()
                secciones_con_datos = {k: v for k, v in items_por_seccion.items() if v['items']}
                
                if len(secciones_con_datos) > 1:
                    ruta_pdf = generador_pdf.crear_recibo_con_secciones(
                        nombre_cliente, secciones_con_datos, total, folio_numero=None
                    )
                else:
                    items_carrito = carrito.obtener_items()
                    ruta_pdf = generador_pdf.crear_recibo_simple(
                        nombre_cliente, items_carrito, f"${total:.2f}", folio_numero=None
                    )
            else:
                items_carrito = carrito.obtener_items()
                ruta_pdf = generador_pdf.crear_recibo_simple(
                    nombre_cliente, items_carrito, f"${total:.2f}", folio_numero=None
                )
            
            if ruta_pdf:
                messagebox.showinfo("PDF Generado", 
                                  f"PDF generado exitosamente!\n\n"
                                  f"Guardado en: {ruta_pdf}\n\n"
                                  f"Nota: Esta venta NO ha sido registrada en la base de datos.")
            else:
                messagebox.showerror("Error", "No se pudo generar el PDF.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")

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
        
        productos = database.buscar_productos_por_grupo_con_especial(id_grupo, texto_busqueda)
        
        if productos:
            for nombre, precio, es_especial, unidad in productos:
                widgets['tree_resultados'].insert("", "end", values=(nombre, f"${precio:.2f}", es_especial, unidad))
        else:
            widgets['tree_resultados'].insert("", "end", values=("No se encontraron productos", "", "", ""))

    def run(self):
        """Run the application main loop"""
        if self.root:
            self.root.mainloop()

if __name__ == "__main__":
    app = ReciboAppMejorado()
    app.run()