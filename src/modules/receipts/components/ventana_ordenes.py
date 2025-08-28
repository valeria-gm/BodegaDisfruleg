# src/modules/receipts/components/ventana_ordenes.py
# Ventana principal de gestión de órdenes guardadas - Actualizada para nueva estructura DB

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Callable, Any
import threading
from datetime import datetime

from .orden_manager import obtener_manager


class VentanaOrdenes:
    """
    Ventana principal para gestión de órdenes guardadas.
    
    Funcionalidades:
    - Vista de órdenes activas y historial
    - Búsqueda por folio
    - Creación, edición y eliminación de órdenes
    - Auto-refresh y filtros en tiempo real
    """
    
    def __init__(self, parent=None, user_data=None, on_nueva_orden=None, on_editar_orden=None):
        """
        Inicializa la ventana de gestión de órdenes.
        
        Args:
            parent: Ventana padre (opcional)
            user_data: Datos del usuario autenticado
            on_nueva_orden: Callback para crear nueva orden
            on_editar_orden: Callback para editar orden existente
        """
        self.parent = parent
        self.user_data = user_data or {}
        self.on_nueva_orden = on_nueva_orden
        self.on_editar_orden = on_editar_orden
        
        # Configuración de usuario
        self.username = self.user_data.get('username', 'usuario')
        self.es_admin = self.user_data.get('rol', '').lower() == 'admin'
        
        # Manager de órdenes
        self.orden_manager = obtener_manager()
        
        # Variables de control
        self.auto_refresh_active = True
        self.filtro_busqueda = tk.StringVar()
        self.filtro_busqueda.trace('w', self._on_filtro_changed)
        
        # Crear ventana
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self._configurar_ventana()
        self._crear_interfaz()
        self._cargar_datos_iniciales()
        self._iniciar_auto_refresh()
    
    def _configurar_ventana(self):
        """Configura las propiedades básicas de la ventana"""
        self.root.title("Gestión de Órdenes - Disfruleg")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        # Configurar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Configurar eventos de enfoque para auto-actualización
        self.root.bind("<FocusIn>", self._on_focus_in)
        self.root.bind("<<OrdenCambiada>>", self._on_orden_cambiada)
        
        # Centrar ventana
        self.root.transient(self.parent) if self.parent else None
        self.root.grab_set() if self.parent else None
    
    def _crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        # Estilo
        style = ttk.Style()
        style.configure("Heading.TLabel", font=("Arial", 11, "bold"))
        style.configure("Green.TButton", foreground="white")
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Header con información del usuario
        self._crear_header(main_frame)
        
        # Barra de herramientas
        self._crear_toolbar(main_frame)
        
        # Notebook con pestañas
        self._crear_notebook(main_frame)
        
        # Barra de estado
        self._crear_status_bar(main_frame)
    
    def _crear_header(self, parent):
        """Crea el header con información del usuario"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Título principal
        titulo = ttk.Label(header_frame, 
                          text="Gestión de Órdenes",
                          style="Heading.TLabel",
                          font=("Arial", 16, "bold"))
        titulo.pack(side="left")
        
        # Información del usuario
        user_info = f"Usuario: {self.user_data.get('nombre_completo', self.username)}"
        if self.es_admin:
            user_info += " (ADMIN)"
        
        user_label = ttk.Label(header_frame, text=user_info, font=("Arial", 10))
        user_label.pack(side="right")
    
    def _crear_toolbar(self, parent):
        """Crea la barra de herramientas superior"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill="x", pady=(0, 10))
        
        # Frame izquierdo - Búsqueda
        search_frame = ttk.Frame(toolbar_frame)
        search_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(search_frame, text="Buscar por folio:").pack(side="left", padx=(0, 5))
        
        self.entry_busqueda = ttk.Entry(search_frame, textvariable=self.filtro_busqueda, width=15)
        self.entry_busqueda.pack(side="left", padx=(0, 5))
        
        btn_buscar = ttk.Button(search_frame, text="Buscar", 
                               command=self._buscar_por_folio)
        btn_buscar.pack(side="left", padx=(0, 5))
        
        btn_limpiar = ttk.Button(search_frame, text="Limpiar",
                                command=self._limpiar_busqueda)
        btn_limpiar.pack(side="left")
        
        # Frame derecho - Acciones
        actions_frame = ttk.Frame(toolbar_frame)
        actions_frame.pack(side="right")
        
        # Botón Nueva Orden (prominente)
        self.btn_nueva_orden = ttk.Button(actions_frame, 
                                         text="Nueva Orden",
                                         command=self._nueva_orden,
                                         style="Accent.TButton")
        self.btn_nueva_orden.pack(side="right", padx=(10, 0))
        
        # Botón Actualizar
        btn_actualizar = ttk.Button(actions_frame, 
                                   text="Actualizar",
                                   command=self._actualizar_listas)
        btn_actualizar.pack(side="right", padx=(5, 0))
    
    def _crear_notebook(self, parent):
        """Crea el notebook con las pestañas de órdenes"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # Pestaña Órdenes Activas
        self.frame_activas = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.frame_activas, text="Órdenes Activas")
        
        # Pestaña Historial
        self.frame_historial = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.frame_historial, text="Historial")
        
        # Crear contenido de cada pestaña
        self._crear_lista_ordenes(self.frame_activas, "activas")
        self._crear_lista_ordenes(self.frame_historial, "historial")
        
        # Evento de cambio de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _crear_lista_ordenes(self, parent, tipo):
        """Crea la lista de órdenes para una pestaña específica"""
        # Configurar columnas según el tipo
        if tipo == "activas":
            columnas = ("folio", "cliente", "total", "fecha_mod", "usuario", "acciones")
            headings = {
                "folio": "Folio",
                "cliente": "Cliente", 
                "total": "Total",
                "fecha_mod": "Última Modificación",
                "usuario": "Usuario",
                "acciones": "Acciones"
            }
            tree_name = "tree_activas"
        else:
            columnas = ("folio", "cliente", "total", "fecha_reg", "usuario")
            headings = {
                "folio": "Folio",
                "cliente": "Cliente",
                "total": "Total", 
                "fecha_reg": "Fecha Registro",
                "usuario": "Usuario"
            }
            tree_name = "tree_historial"
        
        # Frame para la lista
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill="both", expand=True)
        
        # Treeview
        tree = ttk.Treeview(list_frame, columns=columnas, show="headings", height=15)
        
        # Configurar columnas
        for col in columnas:
            tree.heading(col, text=headings[col])
            
            # Configurar ancho según la columna
            if col == "folio":
                tree.column(col, width=80, anchor="center")
            elif col == "cliente":
                tree.column(col, width=200, anchor="w")
            elif col == "total":
                tree.column(col, width=100, anchor="e")
            elif col in ["fecha_mod", "fecha_reg"]:
                tree.column(col, width=150, anchor="center")
            elif col == "usuario":
                tree.column(col, width=100, anchor="center")
            elif col == "acciones":
                tree.column(col, width=150, anchor="center")
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        scrollbar_h = ttk.Scrollbar(list_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Pack treeview y scrollbars
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_v.grid(row=0, column=1, sticky="ns")
        scrollbar_h.grid(row=1, column=0, sticky="ew")
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Guardar referencia al tree
        setattr(self, tree_name, tree)
        
        # Eventos para órdenes activas
        if tipo == "activas":
            tree.bind("<Double-1>", self._on_doble_click_activas)
            tree.bind("<Button-1>", self._on_click_activas)
    
    def _crear_status_bar(self, parent):
        """Crea la barra de estado"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill="x")
        
        # Información de conteo
        self.lbl_count_activas = ttk.Label(status_frame, text="Órdenes activas: 0")
        self.lbl_count_activas.pack(side="left")
        
        self.lbl_count_historial = ttk.Label(status_frame, text="| Historial: 0")
        self.lbl_count_historial.pack(side="left", padx=(10, 0))
        
        # Información de última actualización
        self.lbl_ultima_actualizacion = ttk.Label(status_frame, text="")
        self.lbl_ultima_actualizacion.pack(side="right")
    
    # ==================== EVENTOS Y CALLBACKS ====================
    
    def _nueva_orden(self):
        """Callback para crear una nueva orden"""
        if self.on_nueva_orden:
            try:
                self.on_nueva_orden()
                # Actualizar lista después de crear
                self.root.after(1000, self._actualizar_listas)
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear nueva orden: {str(e)}")
        else:
            messagebox.showinfo("No Implementado", 
                              "Callback de nueva orden no configurado")
    
    def _on_doble_click_activas(self, event):
        """Maneja doble clic en órdenes activas para editar"""
        item = self.tree_activas.selection()[0] if self.tree_activas.selection() else None
        if item:
            valores = self.tree_activas.item(item, "values")
            if valores:
                folio = int(valores[0])  # Primera columna es el folio
                self._editar_orden(folio)
    
    def _on_click_activas(self, event):
        """Maneja clic simple en órdenes activas para acciones"""
        # Identificar si se hizo clic en la columna de acciones
        item = self.tree_activas.identify_row(event.y)
        if not item:
            return
        
        column = self.tree_activas.identify_column(event.x)
        if column == "#6":  # Columna de acciones (índice 6)
            valores = self.tree_activas.item(item, "values")
            if valores:
                folio = int(valores[0])
                self._mostrar_menu_acciones(event, folio)
    
    def _mostrar_menu_acciones(self, event, folio):
        """Muestra menú contextual con acciones para una orden"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Editar", command=lambda: self._editar_orden(folio))
        menu.add_separator()
        menu.add_command(label="Eliminar", command=lambda: self._eliminar_orden(folio))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _editar_orden(self, folio):
        """Callback para editar una orden específica"""
        if self.on_editar_orden:
            try:
                self.on_editar_orden(folio)
                # Actualizar lista después de editar
                self.root.after(1000, self._actualizar_listas)
            except Exception as e:
                messagebox.showerror("Error", f"Error al editar orden {folio}: {str(e)}")
        else:
            messagebox.showinfo("No Implementado", 
                              f"Callback de edición no configurado para folio {folio}")
    
    def _eliminar_orden(self, folio):
        """Elimina una orden después de confirmación"""
        if messagebox.askyesno("Confirmar Eliminación", 
                              f"¿Está seguro de que desea eliminar la orden con folio {folio:06d}?\n\n"
                              f"Esta acción liberará el folio y no se puede deshacer."):
            try:
                if self.orden_manager.liberar_folio(folio):
                    messagebox.showinfo("Éxito", f"Orden {folio:06d} eliminada exitosamente")
                    self._actualizar_listas()
                else:
                    messagebox.showerror("Error", f"No se pudo eliminar la orden {folio}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar orden: {str(e)}")
    
    def _on_tab_changed(self, event):
        """Maneja cambio de pestaña"""
        tab_actual = self.notebook.index(self.notebook.select())
        if tab_actual == 0:  # Pestaña activas
            self._cargar_ordenes_activas()
        else:  # Pestaña historial
            self._cargar_historial()
    
    def _on_filtro_changed(self, *args):
        """Maneja cambios en el filtro de búsqueda"""
        # Auto-filtrar después de un breve delay
        if hasattr(self, '_filter_job'):
            self.root.after_cancel(self._filter_job)
        self._filter_job = self.root.after(300, self._aplicar_filtro)
    
    def _buscar_por_folio(self):
        """Busca una orden específica por folio"""
        texto_busqueda = self.filtro_busqueda.get().strip()
        if not texto_busqueda:
            self._aplicar_filtro()
            return
        
        try:
            folio = int(texto_busqueda)
            # Buscar en órdenes activas
            for item in self.tree_activas.get_children():
                valores = self.tree_activas.item(item, "values")
                if valores and int(valores[0]) == folio:
                    self.notebook.select(0)  # Cambiar a pestaña activas
                    self.tree_activas.selection_set(item)
                    self.tree_activas.focus(item)
                    self.tree_activas.see(item)
                    return
            
            # Buscar en historial
            for item in self.tree_historial.get_children():
                valores = self.tree_historial.item(item, "values")
                if valores and int(valores[0]) == folio:
                    self.notebook.select(1)  # Cambiar a pestaña historial
                    self.tree_historial.selection_set(item)
                    self.tree_historial.focus(item)
                    self.tree_historial.see(item)
                    return
            
            messagebox.showinfo("No Encontrado", f"No se encontró orden con folio {folio:06d}")
            
        except ValueError:
            messagebox.showwarning("Folio Inválido", "Por favor ingrese un número de folio válido")
    
    def _limpiar_busqueda(self):
        """Limpia el filtro de búsqueda"""
        self.filtro_busqueda.set("")
        self._aplicar_filtro()
    
    def _aplicar_filtro(self):
        """Aplica filtro a las listas según el texto de búsqueda"""
        filtro = self.filtro_busqueda.get().strip().lower()
        
        # Filtrar órdenes activas
        self._filtrar_tree(self.tree_activas, filtro)
        
        # Filtrar historial
        self._filtrar_tree(self.tree_historial, filtro)
    
    def _filtrar_tree(self, tree, filtro):
        """Aplica filtro a un treeview específico"""
        if not filtro:
            # Mostrar todos los items
            for item in tree.get_children():
                tree.item(item, tags=())
        else:
            # Filtrar items
            for item in tree.get_children():
                valores = tree.item(item, "values")
                texto_completo = " ".join(str(v).lower() for v in valores)
                
                if filtro in texto_completo:
                    tree.item(item, tags=())
                else:
                    tree.item(item, tags=("hidden",))
        
        # Configurar tag para ocultar items
        tree.tag_configure("hidden", foreground="lightgray")
    
    # ==================== CARGA DE DATOS ====================
    
    def _cargar_datos_iniciales(self):
        """Carga los datos iniciales en ambas pestañas"""
        self._cargar_ordenes_activas()
        self._cargar_historial()
    
    def _cargar_ordenes_activas(self):
        """Carga las órdenes activas en el treeview"""
        try:
            # Limpiar tree
            for item in self.tree_activas.get_children():
                self.tree_activas.delete(item)
            
            # Obtener datos
            ordenes = self.orden_manager.obtener_ordenes_activas(self.username, self.es_admin)
            
            # Poblar tree
            for orden in ordenes:
                folio_str = f"{orden['folio_numero']:06d}"
                cliente = orden['nombre_cliente']
                total = f"${orden['total_estimado']:.2f}"
                fecha = orden.get('fecha_modificacion_str', 'N/A')
                usuario = orden['usuario_creador']
                acciones = "[Clic para acciones]"
                
                self.tree_activas.insert("", "end", values=(
                    folio_str, cliente, total, fecha, usuario, acciones
                ))
            
            # Actualizar contador
            self.lbl_count_activas.config(text=f"Órdenes activas: {len(ordenes)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar órdenes activas: {str(e)}")
    
    def _cargar_historial(self):
        """Carga el historial de órdenes en el treeview"""
        try:
            # Limpiar tree
            for item in self.tree_historial.get_children():
                self.tree_historial.delete(item)
            
            # Obtener datos
            historial = self.orden_manager.obtener_historial(self.username, self.es_admin, limite=100)
            
            # Poblar tree
            for orden in historial:
                folio_str = f"{orden['folio_numero']:06d}"
                cliente = orden['nombre_cliente']
                total = f"${orden['total_estimado']:.2f}"
                fecha = orden.get('fecha_modificacion_str', 'N/A')
                usuario = orden['usuario_creador']
                
                self.tree_historial.insert("", "end", values=(
                    folio_str, cliente, total, fecha, usuario
                ))
            
            # Actualizar contador
            self.lbl_count_historial.config(text=f"| Historial: {len(historial)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar historial: {str(e)}")
    
    def _actualizar_listas(self):
        """Actualiza ambas listas de órdenes"""
        self._cargar_ordenes_activas()
        self._cargar_historial()
        
        # Actualizar timestamp
        ahora = datetime.now().strftime("%H:%M:%S")
        self.lbl_ultima_actualizacion.config(text=f"Actualizado: {ahora}")
    
    def forzar_actualizacion(self):
        """Fuerza la actualización de las listas desde el exterior"""
        try:
            self._actualizar_listas()
            print("Lista de órdenes actualizada desde ventana externa")
        except Exception as e:
            print(f"Error al forzar actualización: {e}")
    
    def _on_focus_in(self, event):
        """Se ejecuta cuando la ventana recibe el foco"""
        # Solo actualizar si el evento es para la ventana principal, no widgets internos
        if event.widget == self.root:
            # Actualizar con un pequeño delay para evitar múltiples actualizaciones
            self.root.after(100, self.forzar_actualizacion)
    
    def _on_orden_cambiada(self, event):
        """Maneja el evento personalizado de orden cambiada"""
        print("Evento OrdenCambiada recibido en VentanaOrdenes")
        self.forzar_actualizacion()
    
    # ==================== AUTO-REFRESH ====================
    
    def _iniciar_auto_refresh(self):
        """Inicia el auto-refresh cada 30 segundos"""
        if self.auto_refresh_active:
            self._actualizar_listas()
            self.root.after(30000, self._iniciar_auto_refresh)
    
    def _detener_auto_refresh(self):
        """Detiene el auto-refresh"""
        self.auto_refresh_active = False
    
    # ==================== CLEANUP ====================
    
    def _on_closing(self):
        """Maneja el cierre de la ventana"""
        self._detener_auto_refresh()
        if self.parent:
            self.root.destroy()
        else:
            self.root.quit()
    
    def show(self):
        """Muestra la ventana"""
        self.root.mainloop()
    
    def destroy(self):
        """Destruye la ventana"""
        self._detener_auto_refresh()
        self.root.destroy()


# ==================== FUNCIÓN DE CONVENIENCIA ====================

def abrir_ventana_ordenes(parent=None, user_data=None, on_nueva_orden=None, on_editar_orden=None):
    """
    Función de conveniencia para abrir la ventana de gestión de órdenes.
    
    Args:
        parent: Ventana padre
        user_data: Datos del usuario autenticado
        on_nueva_orden: Callback para crear nueva orden
        on_editar_orden: Callback para editar orden (recibe folio)
        
    Returns:
        VentanaOrdenes: Instancia de la ventana creada
    """
    ventana = VentanaOrdenes(parent, user_data, on_nueva_orden, on_editar_orden)
    return ventana


# ==================== BLOQUE DE PRUEBA ====================

if __name__ == '__main__':
    """Bloque de pruebas para verificar la interfaz"""
    
    # Datos de prueba
    user_data_test = {
        'username': 'test_user',
        'nombre_completo': 'Usuario de Prueba',
        'rol': 'admin'
    }
    
    def callback_nueva_orden():
        print("Callback: Nueva orden solicitada")
        messagebox.showinfo("Prueba", "Callback de nueva orden ejecutado")
    
    def callback_editar_orden(folio):
        print(f"Callback: Editar orden {folio}")
        messagebox.showinfo("Prueba", f"Callback de edición ejecutado para folio {folio}")
    
    # Crear ventana de prueba
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    ventana = abrir_ventana_ordenes(
        parent=None,
        user_data=user_data_test,
        on_nueva_orden=callback_nueva_orden,
        on_editar_orden=callback_editar_orden
    )
    
    ventana.show()