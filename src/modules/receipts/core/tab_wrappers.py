import tkinter as tk
from tkinter import ttk
from typing import Any


class BaseRootWrapper:
    """Base root wrapper that provides minimal root window interface without conflicts"""
    
    def __init__(self, parent_window: tk.Tk, tab_id: str = ""):
        self.parent_window = parent_window
        self.tab_id = tab_id
        self.title_text = f"Tab {tab_id[-4:]}" if tab_id else ""
    
    def title(self, text=None):
        if text is not None:
            self.title_text = text
        return self.title_text
    
    def geometry(self, geom=None):
        pass
    
    def protocol(self, protocol, callback):
        pass
    
    def winfo_toplevel(self):
        return self.parent_window
    
    def winfo_x(self):
        return self.parent_window.winfo_x()
    
    def winfo_y(self):
        return self.parent_window.winfo_y()
    
    def winfo_width(self):
        return self.parent_window.winfo_width()
    
    def winfo_height(self):
        return self.parent_window.winfo_height()
    
    def winfo_screenwidth(self):
        return self.parent_window.winfo_screenwidth()
    
    def winfo_screenheight(self):
        return self.parent_window.winfo_screenheight()
    
    def winfo_rootx(self):
        return self.parent_window.winfo_rootx()
    
    def winfo_rooty(self):
        return self.parent_window.winfo_rooty()
    
    def update(self):
        return self.parent_window.update()
    
    def update_idletasks(self):
        return self.parent_window.update_idletasks()
    
    def after(self, ms, func=None, *args):
        return self.parent_window.after(ms, func, *args)
    
    def after_idle(self, func, *args):
        return self.parent_window.after_idle(func, *args)
    
    def after_cancel(self, id):
        return self.parent_window.after_cancel(id)
    
    def bell(self):
        return self.parent_window.bell()
    
    def report_callback_exception(self, *args):
        return self.parent_window.report_callback_exception(*args)
    
    def iconname(self, name=None):
        return self.parent_window.iconname(name)
    
    def grab_set(self):
        return self.parent_window.grab_set()
    
    def grab_release(self):
        return self.parent_window.grab_release()
    
    def grab_current(self):
        return self.parent_window.grab_current()
    
    @property
    def tk(self):
        return self.parent_window.tk
    
    @property
    def master(self):
        return self.parent_window.master
    
    def __str__(self):
        return str(self.parent_window)
    
    def __getattr__(self, name):
        """Delegate any missing attributes to the parent window"""
        try:
            return getattr(self.parent_window, name)
        except AttributeError:
            if name.startswith('_'):
                return None
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


class TabRootWrapper(BaseRootWrapper):
    """Standard tab root wrapper for normal operation"""
    
    def __init__(self, tab_frame: ttk.Frame, main_window: tk.Tk, tab_id: str):
        super().__init__(main_window, tab_id)
        self.tab_frame = tab_frame


class IsolatedRootWrapper(BaseRootWrapper):
    """Isolated root wrapper with additional isolation features"""
    
    def __init__(self, tab_frame: ttk.Frame, main_window: tk.Tk, tab_id: str):
        super().__init__(main_window, tab_id)
        self.tab_frame = tab_frame
        self._tab_widgets = {}
    
    def __getattr__(self, name):
        """Enhanced delegation with isolation features"""
        main_window_attrs = {
            'winfo_reqwidth', 'winfo_reqheight', 'winfo_parent', 'winfo_pathname',
            'winfo_class', 'children', 'nametowidget', 'winfo_name', 'winfo_id', 
            'winfo_children', 'winfo_exists', 'winfo_fpixels', 'winfo_pixels', 
            'winfo_rgb', 'winfo_server', 'winfo_visual', 'winfo_visualid', 
            'winfo_vrootheight', 'winfo_vrootwidth', 'winfo_vrootx', 'winfo_vrooty',
            'focus_set', 'focus_get', 'focus_force', 'focus_lastfor', 'selection_clear',
            'selection_get', 'selection_handle', 'selection_own', 'selection_own_get',
            'send', 'tkraise', 'lower', 'colormodel', 'getvar', 'setvar', 
            'globalgetvar', 'globalsetvar', 'getboolean', 'getdouble', 'getint',
            'image_names', 'image_types', 'mainloop', 'quit', 'wait_variable', 
            'wait_window', 'wait_visibility', 'event_add', 'event_delete', 
            'event_generate', 'event_info', 'bind', 'bind_all', 'bind_class', 
            'unbind', 'unbind_all', 'unbind_class', 'bindtags'
        }
        
        if name in main_window_attrs:
            return getattr(self.parent_window, name)
        
        try:
            return getattr(self.tab_frame, name)
        except AttributeError:
            try:
                return getattr(self.parent_window, name)
            except AttributeError:
                return None