"""
Tests para la aplicación Inicio

Pruebas unitarias para modelos, vistas y utilidades.
"""

from django.test import TestCase
from inicio.models import Producto, Cliente, Venta


class ProductoTestCase(TestCase):
    def setUp(self):
        Producto.objects.create(
            nombre="Laptop",
            descripcion="Laptop de prueba",
            precio=1500.00,
            stock=5,
            categoria="Electrónica"
        )

    def test_producto_creacion(self):
        producto = Producto.objects.get(nombre="Laptop")
        self.assertEqual(producto.precio, 1500.00)
        self.assertEqual(producto.stock, 5)


class ClienteTestCase(TestCase):
    def setUp(self):
        Cliente.objects.create(
            nombre="Juan Pérez",
            email="juan@example.com",
            telefono="0987654321",
            ciudad="Quito"
        )

    def test_cliente_creacion(self):
        cliente = Cliente.objects.get(nombre="Juan Pérez")
        self.assertEqual(cliente.email, "juan@example.com")
        self.assertEqual(cliente.ciudad, "Quito")

    def test_cliente_str(self):
        cliente = Cliente.objects.get(nombre="Juan Pérez")
        self.assertEqual(str(cliente), "Juan Pérez")


class VentaTestCase(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre="Mouse",
            descripcion="Mouse de prueba",
            precio=20.00,
            stock=25,
            categoria="Accesorios"
        )
        self.cliente = Cliente.objects.create(
            nombre="Ana Gomez",
            email="ana@example.com"
        )

    def test_venta_total_autocalculado(self):
        venta = Venta.objects.create(
            cliente=self.cliente,
            producto=self.producto,
            cantidad=3,
            precio_unitario=20.00,
            total=0,
            estado='completada'
        )
        self.assertEqual(float(venta.total), 60.00)
        self.assertEqual(str(venta), f"Venta {venta.id} - {self.cliente.nombre}")
