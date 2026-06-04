# Mi Emprendimiento - Panel de Administración

Sistema de gestión simple para pequeños emprendimientos desarrollado con Django.

## Características

- ✅ Gestión de Productos
- ✅ Gestión de Clientes
- ✅ Registro de Ventas
- ✅ Reportes Básicos
- ✅ Panel de Control Intuitivo
- ✅ Interfaz Responsiva

## Requisitos

- Python 3.12+
- Django 6.0.6

## Instalación

1. Clonar el repositorio:
```bash
git clone <repositorio>
cd Proyecto_recuperacion12
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Dependencias adicionales:
- `reportlab` es necesario para generar archivos PDF de recibos y reportes.

5. Si usa Windows, active el entorno virtual con:
```bash
venv\Scripts\activate
```

4. Hacer migraciones:
```bash
python manage.py migrate
```

5. Configurar variables de entorno:
```bash
cp .env.example .env
# En Windows PowerShell:
# copy .env.example .env
```

6. Crear superusuario:
```bash
python manage.py createsuperuser
```

7. Ejecutar servidor:
```bash
python manage.py runserver
```

7. Correr pruebas:
```bash
python manage.py test
```

Acceder a: http://127.0.0.1:8000/

## Estructura del Proyecto

```
Proyecto_recuperacion12/
├── config/           # Configuración principal
├── inicio/           # Aplicación principal
│   ├── models.py     # Modelos de datos
│   ├── views.py      # Vistas
│   ├── urls.py       # URLs
│   ├── admin.py      # Admin
│   └── templates/    # Templates HTML
├── static/           # Archivos estáticos (CSS, JS)
├── manage.py         # Gestor de Django
└── requirements.txt  # Dependencias
```

## Modelos

- **Producto**: Nombre, descripción, precio, stock, categoría
- **Cliente**: Nombre, email, teléfono, dirección, ciudad
- **Venta**: Cliente, producto, cantidad, precio, estado

## Autor

Desarrollado con Django

## Licencia

MIT
