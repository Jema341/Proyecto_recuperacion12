# API Documentation

## Endpoints de la Aplicación

### Productos

**GET** `/productos/`
- Retorna: Lista de todos los productos
- Parámetros: ninguno

**GET** `/producto/<id>/`
- Retorna: Detalle de un producto específico
- Parámetros: id (entero)

### Clientes

**GET** `/clientes/`
- Retorna: Lista de todos los clientes
- Parámetros: ninguno

**GET** `/cliente/<id>/`
- Retorna: Detalle de un cliente específico
- Parámetros: id (entero)

### Ventas

**GET** `/ventas/`
- Retorna: Historial de todas las ventas
- Parámetros: ninguno

### Reportes

**GET** `/reportes/`
- Retorna: Datos estadísticos y reportes
- Parámetros: ninguno

## Modelos de Datos

### Producto
```json
{
  "id": 1,
  "nombre": "Laptop",
  "descripcion": "Laptop de prueba",
  "precio": 1500.00,
  "stock": 5,
  "categoria": "Electrónica",
  "fecha_creacion": "2026-06-04T10:30:00"
}
```

### Cliente
```json
{
  "id": 1,
  "nombre": "Juan García",
  "email": "juan@example.com",
  "telefono": "0987654321",
  "direccion": "Calle Principal 123",
  "ciudad": "Quito",
  "fecha_registro": "2026-06-04T10:30:00"
}
```

### Venta
```json
{
  "id": 1,
  "cliente": "Juan García",
  "producto": "Laptop",
  "cantidad": 2,
  "precio_unitario": 1500.00,
  "total": 3000.00,
  "fecha_venta": "2026-06-04T10:30:00",
  "estado": "completada"
}
```

## Códigos de Estado HTTP

- `200`: Éxito
- `201`: Creado
- `400`: Solicitud inválida
- `404`: No encontrado
- `500`: Error del servidor

## Autenticación

Actualmente, la aplicación requiere estar logueado en el panel admin para acceder a datos.

## Versión

API v1.0 - Junio 2026
