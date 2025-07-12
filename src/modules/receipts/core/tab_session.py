import uuid
import copy
from typing import Dict, Any, Optional
from datetime import datetime

from ..receipt_generator_refactored import ReciboAppMejorado


class BaseTabSession:
    """Base class for managing the state of a single receipt generation session"""
    
    def __init__(self, tab_id: str, user_data: Dict[str, Any], isolated: bool = False):
        self.tab_id = tab_id
        self.user_data = copy.deepcopy(user_data) if isolated else user_data
        self.app_instance: Optional[ReciboAppMejorado] = None
        self.tab_frame = None
        self.client_name = ""
        self.cart_count = 0
        self.created_at = datetime.now()
        self.isolated = isolated
        
    def get_tab_title(self) -> str:
        """Get the display title for this tab"""
        if self.client_name:
            return f"{self.client_name}"
        if self.isolated:
            return f"Sesión #{self.tab_id[-4:]}"
        return "Nueva Sesión"
    
    def has_data(self) -> bool:
        """Check if this tab has any data that would be lost on close"""
        return self.cart_count > 0
    
    def update_status(self, client_name: str = "", cart_count: int = 0):
        """Update the tab's status"""
        self.client_name = client_name
        self.cart_count = cart_count
    
    def cleanup(self):
        """Cleanup resources when closing the tab"""
        if self.app_instance and hasattr(self.app_instance, 'db_manager'):
            try:
                self.app_instance.db_manager.close()
            except Exception as e:
                print(f"Warning: Error closing database for tab {self.tab_id[-8:]}: {e}")


class TabSession(BaseTabSession):
    """Standard tab session with full functionality"""
    
    def __init__(self, tab_id: str, user_data: Dict[str, Any]):
        super().__init__(tab_id, user_data, isolated=False)
        self.has_unsaved_changes = False
    
    def has_data(self) -> bool:
        """Check if this tab has any data that would be lost on close"""
        return self.cart_count > 0 or self.has_unsaved_changes
    
    def update_status(self, client_name: str = "", cart_count: int = 0, has_changes: bool = False):
        """Update the tab's status including unsaved changes"""
        super().update_status(client_name, cart_count)
        self.has_unsaved_changes = has_changes


class IsolatedTabSession(BaseTabSession):
    """Isolated tab session with complete data isolation"""
    
    def __init__(self, tab_id: str, user_data: Dict[str, Any]):
        super().__init__(tab_id, user_data, isolated=True)


class TabSessionFactory:
    """Factory for creating tab sessions"""
    
    @staticmethod
    def create_session(session_type: str, user_data: Dict[str, Any]) -> BaseTabSession:
        """Create a tab session of the specified type"""
        tab_id = str(uuid.uuid4())
        
        if session_type == "isolated":
            return IsolatedTabSession(tab_id, user_data)
        else:
            return TabSession(tab_id, user_data)