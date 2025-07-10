# 🛠️ Testing & Troubleshooting Guide

## 📋 **Complete Testing Workflow**

### **Step 1: Basic Setup Verification**
```bash
# 1. Check file structure
ls -la src/modules/receipts/components/
ls -la src/modules/receipts/models/

# 2. Check Python path
python -c "import sys; print(sys.path)"

# 3. Verify database connection
python -c "from src.database.conexion import conectar; print('DB OK' if conectar() else 'DB FAIL')"
```

### **Step 2: Run Automated Tests**
```bash
# Run all tests in sequence
python test_refactored_receipt.py
python test_components.py
python integration_test.py
```

### **Step 3: Manual GUI Testing**
```bash
# Interactive testing
python manual_gui_test.py
```

### **Step 4: Comparison Testing**
```bash
# Test both versions side by side
python manual_gui_test.py
# Choose option 1 for refactored, option 2 for original
```

---

## 🚨 **Common Issues & Solutions**

### **Import Errors**

**Problem:** `ModuleNotFoundError: No module named 'src.modules.receipts'`
```bash
# Solution 1: Check current directory
pwd  # Should be in project root

# Solution 2: Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Solution 3: Use absolute imports
python -c "import sys; sys.path.insert(0, 'src')"
```

**Problem:** `ImportError: cannot import name 'ReciboAppMejorado'`
```bash
# Check if refactored file exists
ls -la src/modules/receipts/receipt_generator_refactored.py

# Check syntax
python -m py_compile src/modules/receipts/receipt_generator_refactored.py
```

### **Database Connection Issues**

**Problem:** `mysql.connector.Error: Can't connect to MySQL server`
```bash
# Check database service
sudo systemctl status mysql

# Test connection manually
python -c "from src.database.conexion import conectar; print(conectar())"

# Check database credentials in conexion.py
```

**Problem:** `No clients/products loaded`
```sql
-- Check database contents
SELECT COUNT(*) FROM cliente;
SELECT COUNT(*) FROM producto;
SELECT COUNT(*) FROM grupo;
```

### **GUI Issues**

**Problem:** `tkinter.TclError: no display name and no $DISPLAY environment variable`
```bash
# For WSL/Remote systems
export DISPLAY=:0

# For headless testing
python test_refactored_receipt.py  # Use this instead of GUI
```

**Problem:** `Window appears but is empty/frozen`
```python
# Add debug prints to identify where it's failing
print("Creating client section...")
print("Creating products section...")
print("Creating cart section...")
```

### **PDF Generation Issues**

**Problem:** `FileNotFoundError: [Errno 2] No such file or directory: 'output/recibos/'`
```bash
# Create output directory
mkdir -p output/recibos

# Check permissions
ls -la output/
chmod 755 output/recibos/
```

**Problem:** `UnicodeEncodeError` in PDF
```python
# Check font files exist
ls -la data/fonts/DejaVuSans*.ttf

# Verify font paths in pdf_generator.py
```

### **Performance Issues**

**Problem:** Application loads slowly
```python
# Add timing to identify bottlenecks
import time
start = time.time()
# ... code ...
print(f"Operation took {time.time() - start:.2f}s")
```

**Problem:** Database queries are slow
```sql
-- Check for missing indexes
SHOW INDEX FROM cliente;
SHOW INDEX FROM producto;
SHOW INDEX FROM factura;
```

---

## 🔧 **Debugging Tools**

### **Debug Mode Script**
```python
# Create debug_receipt.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import logging
logging.basicConfig(level=logging.DEBUG)

from src.modules.receipts.receipt_generator_refactored import ReciboAppMejorado
import tkinter as tk

# Enable debug mode
debug_user_data = {
    'nombre_completo': 'DEBUG USER',
    'rol': 'admin'
}

root = tk.Tk()
app = ReciboAppMejorado(root, debug_user_data)
root.mainloop()
```

### **Component Testing**
```python
# Test individual components
from src.modules.receipts.components.database_manager import DatabaseManager
db = DatabaseManager()
print("Clients:", len(db.get_clients()))
print("Products:", len(db.get_products()))
```

### **Memory Testing**
```python
# Check for memory leaks
import tracemalloc
tracemalloc.start()

# ... run your code ...

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
```

---

## 📊 **Test Results Interpretation**

### **Expected Test Results**
```
✅ Import Tests: All modules should import successfully
✅ Database Tests: Should connect and load data
✅ Component Tests: All components should initialize
✅ Integration Tests: Full workflow should work
✅ GUI Tests: Interface should display correctly
```

### **Acceptable Warnings**
```
⚠️  Font warnings: Usually safe to ignore
⚠️  Tkinter geometry warnings: Usually cosmetic
⚠️  MySQL connector warnings: Check but often non-critical
```

### **Critical Errors**
```
❌ Import failures: Must be fixed before proceeding
❌ Database connection failures: Check credentials/service
❌ GUI crashes: Check display/tkinter installation
❌ PDF generation failures: Check fonts/permissions
```

---

## 🎯 **Performance Benchmarks**

### **Acceptable Performance**
- **Application startup:** < 3 seconds
- **Client loading:** < 1 second
- **Product search:** < 0.5 seconds
- **Cart operations:** < 0.1 seconds
- **PDF generation:** < 2 seconds
- **Database save:** < 1 second

### **Monitoring Commands**
```bash
# Monitor resource usage
top -p $(pgrep -f "python.*receipt")

# Check disk usage
df -h output/

# Monitor database connections
mysql -e "SHOW PROCESSLIST;"
```

---

## 📞 **Getting Help**

### **If Tests Fail**
1. **Check Prerequisites:** Database running, Python packages installed
2. **Review Error Messages:** Look for specific error patterns above
3. **Run Individual Tests:** Isolate the failing component
4. **Check Logs:** Look in database logs, system logs
5. **Compare with Original:** Use original version to verify database/setup

### **Debug Information to Collect**
```bash
# System info
python --version
pip list | grep mysql
pip list | grep tkinter

# Database info
mysql --version
systemctl status mysql

# File permissions
ls -la src/modules/receipts/
ls -la output/
```

### **Recovery Steps**
1. **Backup current work:** `git stash` or copy files
2. **Reset to working state:** Use original receipt_generator.py
3. **Identify specific issue:** Use individual component tests
4. **Fix incrementally:** One component at a time
5. **Re-test:** After each fix