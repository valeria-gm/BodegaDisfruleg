from typing import Callable, Any
from functools import wraps


class MethodMonitor:
    """Decorator class for monitoring method calls with session tracking"""
    
    def __init__(self, tab_session, update_callback: Callable = None):
        self.tab_session = tab_session
        self.update_callback = update_callback
    
    def monitor_method(self, method_name: str, update_func: Callable):
        """Create a monitoring decorator for a specific method"""
        def decorator(original_method):
            @wraps(original_method)
            def monitored_wrapper(*args, **kwargs):
                try:
                    # Call original method
                    result = original_method(*args, **kwargs)
                    
                    # Call update function
                    if update_func:
                        update_func()
                    
                    return result
                    
                except Exception as e:
                    print(f"Error in monitored {method_name} for tab {self.tab_session.tab_id[-8:]}: {e}")
                    raise
            
            return monitored_wrapper
        return decorator


def setup_tab_monitoring(tab_session, app_instance, update_tab_title_func, update_tab_info_func):
    """Setup monitoring for a tab session using decorator pattern"""
    if not app_instance:
        return
    
    monitor = MethodMonitor(tab_session)
    
    # Monitor cart updates
    if hasattr(app_instance, '_update_cart_display'):
        original_update_cart = app_instance._update_cart_display
        
        @monitor.monitor_method('_update_cart_display', lambda: None)
        def monitored_update_cart():
            original_update_cart()
            
            # Update tab session status
            cart_count = getattr(app_instance, 'cart_manager', None)
            cart_count = cart_count.get_cart_count() if cart_count else 0
            
            client_name = ""
            if hasattr(app_instance, 'current_client') and app_instance.current_client:
                client_name = app_instance.current_client.nombre_cliente
            
            # Update session based on type
            if hasattr(tab_session, 'has_unsaved_changes'):
                tab_session.update_status(client_name, cart_count, cart_count > 0)
            else:
                tab_session.update_status(client_name, cart_count)
            
            # Update UI
            if update_tab_title_func:
                update_tab_title_func(tab_session.tab_id)
            if update_tab_info_func:
                update_tab_info_func()
        
        app_instance._update_cart_display = monitored_update_cart
    
    # Monitor client changes
    if hasattr(app_instance, 'on_client_change'):
        original_client_change = app_instance.on_client_change
        
        @monitor.monitor_method('on_client_change', lambda: None)
        def monitored_client_change(event=None):
            original_client_change(event)
            
            # Update tab session status
            client_name = ""
            if hasattr(app_instance, 'current_client') and app_instance.current_client:
                client_name = app_instance.current_client.nombre_cliente
            
            # Update session based on type
            if hasattr(tab_session, 'has_unsaved_changes'):
                tab_session.update_status(client_name, tab_session.cart_count, tab_session.has_unsaved_changes)
            else:
                tab_session.update_status(client_name, tab_session.cart_count)
            
            # Update UI
            if update_tab_title_func:
                update_tab_title_func(tab_session.tab_id)
            if update_tab_info_func:
                update_tab_info_func()
        
        app_instance.on_client_change = monitored_client_change


def monitor_app_method(app_instance, method_name: str, monitoring_func: Callable):
    """Generic method monitoring utility"""
    if not hasattr(app_instance, method_name):
        return False
    
    original_method = getattr(app_instance, method_name)
    
    @wraps(original_method)
    def monitored_method(*args, **kwargs):
        try:
            result = original_method(*args, **kwargs)
            monitoring_func()
            return result
        except Exception as e:
            print(f"Error in monitored {method_name}: {e}")
            raise
    
    setattr(app_instance, method_name, monitored_method)
    return True