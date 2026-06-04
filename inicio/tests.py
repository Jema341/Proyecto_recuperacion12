from django.test import TestCase
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
