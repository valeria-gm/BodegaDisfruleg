# Module Launcher System

## Problem Solved

The original modules had import issues when launched as separate processes because:
1. **Relative imports** (`from src.database.conexion`) don't work when running scripts directly
2. **Hard-coded paths** (`fonts/`, `recibos/`) don't match the new folder structure
3. **Missing context** - modules need proper Python path setup

## Solution

### New Launcher Script: `launch_module.py`

This script properly:
- ✅ Sets up the Python path
- ✅ Changes to the correct working directory
- ✅ Handles imports correctly
- ✅ Passes user data to modules
- ✅ Provides proper error handling

### Module Keys vs File Paths

Instead of launching files directly:
```python
# OLD - doesn't work with new structure
subprocess.Popen([python, "src/modules/receipts/receipt_generator.py"])

# NEW - uses launcher with module key
subprocess.Popen([python, "launch_module.py", "receipts", user_data_json])
```

### Available Module Keys

- `receipts` - Receipt generator
- `pricing` - Price editor  
- `inventory` - Purchase registration
- `analytics` - Profit analysis
- `clients` - Client management

### Usage

**From command line:**
```bash
python launch_module.py receipts
python launch_module.py pricing '{"nombre_completo":"Juan","rol":"admin"}'
```

**From main application:**
```python
module_launcher.launch_module("receipts", user_data)
```

## Fixed Issues

✅ **Import paths** - All `src.` imports now work correctly  
✅ **File paths** - Updated to use `data/fonts/` and `output/recibos/`  
✅ **Module execution** - Modules now launch properly with GUI  
✅ **User data** - Passed correctly to each module  
✅ **Error handling** - Better error messages and debugging  

## Module Structure

Each module function in `launch_module.py`:
1. Sets working directory to project root
2. Imports the module class correctly
3. Creates tkinter root window
4. Passes user data (with defaults)
5. Launches the application
6. Handles errors gracefully