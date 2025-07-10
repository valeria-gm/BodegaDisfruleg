import os
from fpdf import FPDF
from datetime import datetime
from typing import List, Tuple
from ..models.receipt_models import ReceiptData

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Register Unicode fonts with absolute path
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        font_path = os.path.join(base_path, 'data', 'fonts')
        self.add_font('DejaVu', '', os.path.join(font_path, 'DejaVuSans.ttf'), uni=True)
        self.add_font('DejaVu', 'B', os.path.join(font_path, 'DejaVuSans-Bold.ttf'), uni=True)
        self.set_font('DejaVu', '', 12)  # Default font

class PDFGenerator:
    """Handles PDF generation for receipts"""
    
    def __init__(self, output_dir: str = "output/recibos"):
        self.output_dir = output_dir
        self._ensure_output_directory()
    
    def _ensure_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_receipt_pdf(self, receipt_data: ReceiptData) -> str:
        """Generate PDF receipt from receipt data"""
        filename = self._generate_filename(receipt_data.cliente.nombre_cliente)
        
        pdf = PDF()
        pdf.add_page()
        
        # Header
        self._add_header(pdf, receipt_data)
        
        # Products table
        self._add_products_table(pdf, receipt_data.productos)
        
        # Total
        self._add_total(pdf, receipt_data.total)
        
        pdf.output(filename)
        return filename
    
    def create_pdf_from_products(self, cliente_name: str, productos_finales: List[Tuple], total_general: float) -> str:
        """Create PDF from product list (legacy method for compatibility)"""
        filename = self._generate_filename(cliente_name)
        
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("DejaVu", size=12)

        # Header
        pdf.set_font("DejaVu", "B", 16)
        pdf.cell(200, 10, txt="DISFRULEG", ln=True, align="C")
        pdf.set_font("DejaVu", size=12)
        pdf.cell(200, 10, txt=f"Recibo para: {cliente_name}", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Fecha: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align="C")
        pdf.ln(10)

        # Products table
        pdf.set_font("DejaVu", "B", 10)
        pdf.cell(60, 10, "Producto", 1)
        pdf.cell(30, 10, "Cantidad", 1)
        pdf.cell(30, 10, "Unidad", 1)
        pdf.cell(30, 10, "Precio/Unidad", 1)
        pdf.cell(40, 10, "Subtotal", 1)
        pdf.ln()

        pdf.set_font("DejaVu", size=10)
        for nombre, cantidad, unidad, precio_unitario, total in productos_finales:
            # Clean special characters for PDF
            nombre_limpio = nombre.replace('🔒', '[ESPECIAL]').encode('latin1', 'replace').decode('latin1')
            pdf.cell(60, 10, nombre_limpio, 1)
            pdf.cell(30, 10, f"{cantidad:.2f}", 1)
            pdf.cell(30, 10, f"{unidad}", 1)
            pdf.cell(30, 10, f"${precio_unitario:.2f}", 1)
            pdf.cell(40, 10, f"${total:.2f}", 1)
            pdf.ln()

        # Total
        pdf.ln(5)
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(150, 10, "TOTAL", 1)
        pdf.cell(40, 10, f"${total_general:.2f}", 1)

        pdf.output(filename)
        return filename
    
    def _generate_filename(self, cliente_name: str) -> str:
        """Generate filename for PDF"""
        fecha = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime('%H%M%S')
        return f"{self.output_dir}/recibo_{cliente_name.lower().replace(' ', '_')}_{fecha}_{timestamp}.pdf"
    
    def _add_header(self, pdf: PDF, receipt_data: ReceiptData):
        """Add header to PDF"""
        pdf.set_font("DejaVu", "B", 16)
        pdf.cell(200, 10, txt="DISFRULEG", ln=True, align="C")
        pdf.set_font("DejaVu", size=12)
        pdf.cell(200, 10, txt=f"Recibo para: {receipt_data.cliente.nombre_cliente}", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Fecha: {receipt_data.fecha}", ln=True, align="C")
        pdf.ln(10)
    
    def _add_products_table(self, pdf: PDF, productos: List):
        """Add products table to PDF"""
        # Table header
        pdf.set_font("DejaVu", "B", 10)
        pdf.cell(60, 10, "Producto", 1)
        pdf.cell(30, 10, "Cantidad", 1)
        pdf.cell(30, 10, "Unidad", 1)
        pdf.cell(30, 10, "Precio/Unidad", 1)
        pdf.cell(40, 10, "Subtotal", 1)
        pdf.ln()
        
        # Table rows
        pdf.set_font("DejaVu", size=10)
        for item in productos:
            if hasattr(item, 'producto'):  # CartItem object
                nombre = item.producto.nombre_producto
                cantidad = float(item.cantidad)
                unidad = item.producto.unidad_producto
                precio = item.precio_final
                subtotal = float(item.subtotal)
            else:  # Tuple format
                nombre, cantidad, unidad, precio, subtotal = item
            
            # Clean special characters for PDF
            nombre_limpio = nombre.replace('🔒', '[ESPECIAL]').encode('latin1', 'replace').decode('latin1')
            pdf.cell(60, 10, nombre_limpio, 1)
            pdf.cell(30, 10, f"{cantidad:.2f}", 1)
            pdf.cell(30, 10, f"{unidad}", 1)
            pdf.cell(30, 10, f"${precio:.2f}", 1)
            pdf.cell(40, 10, f"${subtotal:.2f}", 1)
            pdf.ln()
    
    def _add_total(self, pdf: PDF, total: float):
        """Add total to PDF"""
        pdf.ln(5)
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(150, 10, "TOTAL", 1)
        pdf.cell(40, 10, f"${total:.2f}", 1)