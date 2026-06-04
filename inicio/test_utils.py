from django.test import TestCase
from inicio.utils import calcular_total_venta, aplicar_descuento, formatear_moneda


class UtilsTestCase(TestCase):
    def test_calcular_total_venta(self):
        self.assertEqual(calcular_total_venta(5, 100), 500)
        self.assertEqual(calcular_total_venta(3, 19.99), 59.97)

    def test_aplicar_descuento(self):
        self.assertEqual(aplicar_descuento(100, 10), 90)
        self.assertEqual(aplicar_descuento(250, 25), 187.5)

    def test_formatear_moneda(self):
        self.assertEqual(formatear_moneda(1234.5), "$1,234.50")
        self.assertEqual(formatear_moneda(0), "$0.00")
