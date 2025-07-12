import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
from functools import wraps

from ..receipt_generator_refactored import ReciboAppMejorado
from .tab_wrappers import TabRootWrapper, IsolatedRootWrapper


def handle_app_creation_errors(func):
    """Decorator for handling app creation errors"""
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
    
    @staticmethod
    @handle_app_creation_errors
    def create_standard_app(root_wrapper, user_data: Dict[str, Any]) -> ReciboAppMejorado:
        """Create a standard receipt app instance"""
        return ReciboAppMejorado(root_wrapper, user_data)
    
    @staticmethod
    @handle_app_creation_errors
    def create_isolated_app(main_window: tk.Tk, tab_frame: ttk.Frame, 
                           user_data: Dict[str, Any], tab_id: str) -> ReciboAppMejorado:
        """Create an isolated receipt app instance with proper content reparenting"""
        # Create temporary window for initial app creation
        temp_window = tk.Toplevel(main_window)
        temp_window.withdraw()  # Hide immediately
        
        # Create app instance with isolated user data
        app_instance = ReciboAppMejorado(temp_window, user_data)
        
        # Find and reparent the main content frame
        main_content = AppFactory._find_main_content_frame(temp_window)
        
        if main_content:
            # Reparent content to the tab frame
            main_content.pack_forget()
            main_content.master = tab_frame
            main_content.pack(in_=tab_frame, fill="both", expand=True)
        
        # Destroy temporary window
        temp_window.destroy()
        
        # Create isolated root wrapper
        isolated_wrapper = IsolatedRootWrapper(tab_frame, main_window, tab_id)
        app_instance.root = isolated_wrapper
        
        return app_instance
    
    @staticmethod
    def _find_main_content_frame(window: tk.Tk) -> tk.Frame:
        """Find the main content frame in a window"""
        for child in window.winfo_children():
            if isinstance(child, tk.Frame):
                return child
        return None
    
    @staticmethod
    @handle_app_creation_errors
    def create_app_for_mode(mode: str, root_or_frame, user_data: Dict[str, Any], 
                           tab_id: str = "", main_window: tk.Tk = None) -> ReciboAppMejorado:
        """Create app instance based on mode"""
        if mode == "isolated":
            if not main_window:
                raise ValueError("main_window is required for isolated mode")
            return AppFactory.create_isolated_app(main_window, root_or_frame, user_data, tab_id)
        else:
            # Standard mode
            if isinstance(root_or_frame, ttk.Frame):
                # Create wrapper for frame
                root_wrapper = TabRootWrapper(root_or_frame, main_window or root_or_frame, tab_id)
            else:
                # Direct root window
                root_wrapper = root_or_frame
            
            return AppFactory.create_standard_app(root_wrapper, user_data)