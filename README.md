# DISFRULEG - Sistema de Gestión Comercial

Sistema de gestión comercial desarrollado en Python con interfaz gráfica Tkinter.

## Estructura del Proyecto

```
Dashboard-bodega/
├── main.py                          # Punto de entrada principal
├── requirements.txt                 # Dependencias del proyecto
│
├── src/                            # Código fuente
│   ├── config.py                   # Configuración y ajustes
│   ├── main_application.py         # Aplicación principal
│   │
│   ├── auth/                       # Autenticación y seguridad
│   │   ├── auth_manager.py         # Gestor de autenticación
│   │   ├── login_window.py         # Ventana de login
│   │   ├── session_manager.py      # Gestor de sesiones
│   │   └── hash_passwords.py       # Utilidades de hash
│   │
│   ├── database/                   # Operaciones de base de datos
│   │   ├── db_manager.py           # Gestor de base de datos
│   │   └── conexion.py             # Conexión a BD
│   │
│   ├── ui/                         # Interfaz de usuario
│   │   ├── ui_components.py        # Componentes UI
│   │   └── module_launcher.py      # Lanzador de módulos
│   │
│   └── modules/                    # Módulos de negocio
│       ├── receipts/               # Generación de recibos
│       ├── inventory/              # Gestión de inventario
│       ├── pricing/                # Editor de precios
│       ├── analytics/              # Análisis de ganancias
│       └── clients/                # Gestión de clientes
│
├── data/                           # Archivos de datos
│   ├── sql/                        # Scripts SQL
│   └── fonts/                      # Fuentes del sistema
│
├── output/                         # Archivos generados
│   ├── recibos/                    # Recibos PDF generados
│   └── reportes/                   # Reportes generados
│
├── scripts/                        # Scripts de utilidad
│   ├── install_auth.py             # Instalador de autenticación
│   ├── diagnostico.py              # Herramientas de diagnóstico
│   └── trabajador.py               # Scripts de trabajador
│
└── archive/                        # Archivos antiguos/backup
    └── ... (archivos de respaldo)
```

## Instalación y Uso

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar base de datos:**
   - Instalar MySQL/MariaDB
   - Crear la base de datos usando `data/sql/disfruleg.sql`
   - Configurar credenciales en los archivos de conexión

3. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```

## Dependencias

- **GUI**: tkinter (incluido en Python)
- **Base de datos**: mysql-connector-python
- **Gráficos**: matplotlib
- **PDFs**: fpdf, reportlab
- **Imágenes**: Pillow
- **Seguridad**: bcrypt

## Módulos Disponibles

- **Generar Recibos**: Crear recibos para clientes y gestionar facturación
- **Editor de Precios**: Gestionar productos y precios por tipo de cliente (Solo Admin)
- **Registro de Compras**: Registrar compras y gestionar inventario
- **Análisis de Ganancias**: Ver reportes detallados de ganancias y pérdidas
- **Administrar Clientes**: Gestionar clientes y tipos de cliente (Solo Admin)

## Configuración

Los ajustes de la aplicación se pueden modificar en `src/config.py`:

- `DEBUG_MODE`: Activar/desactivar modo debug
- `USE_LOGIN`: Usar sistema de autenticación
- `USE_SESSION_MANAGER`: Gestión de sesiones
- `USE_CANVAS_SCROLL`: Scroll en la interfaz
- `USE_HOVER_EFFECTS`: Efectos hover en botones

## Características

- ✅ Sistema de autenticación con roles (admin/usuario)
- ✅ Gestión de sesiones con timeout automático
- ✅ Interfaz modular y escalable
- ✅ Generación de recibos en PDF
- ✅ Análisis de ganancias y reportes
- ✅ Gestión de inventario y precios
- ✅ Base de datos SQL integrada