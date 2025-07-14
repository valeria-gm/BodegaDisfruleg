import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable
from functools import wraps

from ..receipt_generator_refactored import ReciboAppMejorado
from .tab_wrappers import TabRootWrapper, IsolatedRootWrapper

from ..components.database_manager import DatabaseManager
from ..components.pdf_generator import PDFGenerator
from ..components.cart_manager import CartManager
from ..components.product_manager import ProductManager


def handle_app_creation_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error creating app with {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
    return wrapper


class AppFactory:
    """Factory for creating receipt application instances"""
    
    # CAMBIO 1: Añadir el parámetro del callback
    @staticmethod
    @handle_app_creation_errors
    def create_standard_app(root_wrapper, user_data: Dict[str, Any], 
                            on_state_change: Optional[Callable] = None) -> ReciboAppMejorado:
        db_man = DatabaseManager()
        pdf_gen = PDFGenerator()
        cart_man = CartManager()
        initial_products = db_man.get_products()
        prod_man = ProductManager(products=initial_products, db_manager=db_man)

        # CAMBIO 2: Pasar el callback al constructor
        return ReciboAppMejorado(
            root=root_wrapper, 
            user_data=user_data,
            db_manager=db_man,
            pdf_generator=pdf_gen,
            cart_manager=cart_man,
            product_manager=prod_man,
            on_state_change=on_state_change # <-- PASAR CALLBACK
        )
    
    # ... (El resto de la clase necesita cambios similares) ...
    
    @staticmethod
    @handle_app_creation_errors
    def create_app_for_mode(mode: str, root_or_frame, user_data: Dict[str, Any], 
                            tab_id: str = "", main_window: tk.Tk = None,
                            on_state_change: Optional[Callable] = None) -> ReciboAppMejorado:
        # (Nota: Se omite create_isolated_app por brevedad, pero aplicaría el mismo cambio)
        if mode == "isolated":
            # ... (Lógica para modo aislado, también necesitaría pasar el callback) ...
            raise NotImplementedError("Isolated mode needs callback implementation")
        else:
            if isinstance(root_or_frame, ttk.Frame):
                root_wrapper = TabRootWrapper(root_or_frame, main_window or root_or_frame, tab_id)
            else:
                root_wrapper = root_or_frame
            
            # CAMBIO 3: Pasar el callback a la función de creación
            return AppFactory.create_standard_app(root_wrapper, user_data, on_state_change)

