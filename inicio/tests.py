from django.test import TestCase
from inicio.models import Producto, Cliente, Venta
from inicio.serializers import ProductoSerializer, ClienteSerializer, VentaSerializer
from inicio.utils import calcular_total_venta, aplicar_descuento, formatear_moneda, formatear_porcentaje


class UtilsTestCase(TestCase):
    def test_calcular_total_venta(self):
        self.assertEqual(calcular_total_venta(3, 50.0), 150.0)
        self.assertEqual(calcular_total_venta(1, 99.99), 99.99)

    def test_aplicar_descuento(self):
        self.assertEqual(aplicar_descuento(200.0, 10), 180.0)
        self.assertEqual(aplicar_descuento(100.0, 0), 100.0)

    def test_formatear_moneda(self):
        self.assertEqual(formatear_moneda(1234.5), "$1,234.50")

    def test_formatear_porcentaje(self):
        self.assertEqual(formatear_porcentaje(12.3456), "12.35%")


class SerializerTestCase(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre="Camera",
            descripcion="Cámara de prueba",
            precio=250.00,
            stock=10,
            categoria="Fotografía"
        )
        self.cliente = Cliente.objects.create(
            nombre="María López",
            email="maria@example.com",
            telefono="0981234567",
            ciudad="Guayaquil"
        )
        self.venta = Venta.objects.create(
            cliente=self.cliente,
            producto=self.producto,
            cantidad=2,
            precio_unitario=250.00,
            total=500.00,
            estado='completada'
        )

    def test_producto_serializer(self):
        data = ProductoSerializer.serialize(self.producto)
        self.assertEqual(data['nombre'], "Camera")
        self.assertIn('imagen_url', data)

    def test_cliente_serializer(self):
        data = ClienteSerializer.serialize(self.cliente)
        self.assertEqual(data['email'], "maria@example.com")
        self.assertEqual(data['ventas_totales'], 1)

    def test_venta_serializer(self):
        data = VentaSerializer.serialize(self.venta)
        self.assertEqual(data['cliente'], self.cliente.nombre)
        self.assertEqual(data['total'], 500.00)
