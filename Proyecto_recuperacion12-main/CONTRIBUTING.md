# Guía de Desarrollo - Mi Emprendimiento

## Cómo Contribuir

Este documento describe cómo configurar el entorno de desarrollo y contribuir al proyecto.

### Configuración del Entorno

1. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar migraciones:
```bash
python manage.py migrate
```

4. Crear superusuario:
```bash
python manage.py createsuperuser
```

### Estructura de Archivos

- `models.py`: Define los modelos de datos
- `views.py`: Vistas y lógica de negocio
- `urls.py`: URLs y rutas
- `admin.py`: Configuración del panel admin
- `forms.py`: Formularios
- `signals.py`: Señales Django
- `utils.py`: Funciones auxiliares
- `constants.py`: Constantes del proyecto

### Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ejecutar servidor
python manage.py runserver

# Ejecutar tests
python manage.py test

# Acceder al shell Django
python manage.py shell

# Crear superusuario
python manage.py createsuperuser
```

### Recomendaciones de Código

- Usar nombres descriptivos para modelos, vistas y funciones
- Agregar docstrings a las funciones
- Seguir PEP 8
- Escribir tests para funcionalidades nuevas
- Mantener los templates simples y reutilizables

### Primeros Pasos

1. Crear productos de prueba
2. Crear clientes de prueba
3. Registrar ventas
4. Revisar reportes

¡Gracias por contribuir! 🚀
