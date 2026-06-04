"""
Serializadores para la aplicación Inicio

Conversión de modelos a formato JSON/diccionario.
"""

from .models import Producto, Cliente, Venta


class ProductoSerializer:
    @staticmethod
    def serialize(producto):
        return {
            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio': float(producto.precio),
            'stock': producto.stock,
            'categoria': producto.categoria,
            'fecha_creacion': producto.fecha_creacion.isoformat(),
        }

    @staticmethod
    def serialize_list(productos):
        return [ProductoSerializer.serialize(p) for p in productos]


class ClienteSerializer:
    @staticmethod
    def serialize(cliente):
        return {
            'id': cliente.id,
            'nombre': cliente.nombre,
            'email': cliente.email,
            'telefono': cliente.telefono,
            'direccion': cliente.direccion,
            'ciudad': cliente.ciudad,
            'fecha_registro': cliente.fecha_registro.isoformat(),
        }

    @staticmethod
    def serialize_list(clientes):
        return [ClienteSerializer.serialize(c) for c in clientes]


class VentaSerializer:
    @staticmethod
    def serialize(venta):
        return {
            'id': venta.id,
            'cliente': venta.cliente.nombre,
            'producto': venta.producto.nombre,
            'cantidad': venta.cantidad,
            'precio_unitario': float(venta.precio_unitario),
            'total': float(venta.total),
            'fecha_venta': venta.fecha_venta.isoformat(),
            'estado': venta.estado,
        }

    @staticmethod
    def serialize_list(ventas):
        return [VentaSerializer.serialize(v) for v in ventas]
