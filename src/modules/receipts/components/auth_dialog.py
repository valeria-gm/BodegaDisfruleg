import tkinter as tk
from tkinter import messagebox
from src.auth.auth_manager import AuthManager

class AdminPasswordDialog:
    """Dialog for administrator password verification"""
    
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app_instance = app_instance
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Autenticación de Administrador")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the window
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self._create_widgets()
        self._setup_bindings()
        
        # Make modal
        self.dialog.wait_window()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="🔒 Producto Especial", 
                             font=("Arial", 14, "bold"), fg="#f44336")
        title_label.pack(pady=(0, 10))
        
        # Message
        message_label = tk.Label(main_frame, 
                               text="Este producto requiere permisos de administrador.\nIngrese las credenciales de un administrador:",
                               font=("Arial", 10), justify="center")
        message_label.pack(pady=(0, 20))
        
        # Username
        tk.Label(main_frame, text="Usuario:", font=("Arial", 11)).pack(anchor="w")
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(main_frame, textvariable=self.username_var, width=30)
        self.username_entry.pack(fill="x", pady=(0, 10))
        
        # Password
        tk.Label(main_frame, text="Contraseña:", font=("Arial", 11)).pack(anchor="w")
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(main_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.pack(fill="x", pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        tk.Button(button_frame, text="Cancelar", command=self.cancel,
                 bg="#f44336", fg="white", padx=15, pady=5).pack(side="right", padx=5)
        tk.Button(button_frame, text="Verificar", command=self.verify,
                 bg="#4CAF50", fg="white", padx=15, pady=5).pack(side="right", padx=5)
    
    def _setup_bindings(self):
        """Setup keyboard bindings"""
        self.username_entry.focus_set()
        self.password_entry.bind("<Return>", lambda e: self.verify())
        self.dialog.bind("<Escape>", lambda e: self.cancel())
    
    def verify(self):
        """Verify admin credentials"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor ingrese usuario y contraseña")
            return
        
        auth_result = self.app_instance.auth_manager.authenticate(username, password)

        if auth_result['success'] and auth_result['user_data']['rol'] == 'admin':
            self.result = True
            self.dialog.destroy()
            return
        
        messagebox.showerror("Error", auth_result.get('message', 'Credenciales inválidas'))
        self.password_entry.delete(0, tk.END)
        self.password_entry.focus_set()
    
    def cancel(self):
        """Cancel authentication"""
        self.result = False
        self.dialog.destroy()

class AuthenticationManager:
    """Handles authentication operations for receipts"""
    
    def __init__(self, app_instance):
        self.app_instance = app_instance
        self.auth_manager = AuthManager()
    
    def verify_admin_password(self, parent_window) -> bool:
        """Verify administrator password through dialog"""
        dialog = AdminPasswordDialog(parent_window, self.app_instance)
        return dialog.result if dialog.result is not None else False