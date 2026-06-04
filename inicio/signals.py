"""
Señales Django para la aplicación Inicio

Funcionalidades automáticas basadas en eventos.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Venta


@receiver(post_save, sender=Venta)
def actualizar_stock_venta(sender, instance, created, **kwargs):
    """
    Actualiza el stock del producto cuando se crea una venta.
    """
    if created:
        producto = instance.producto
        producto.stock -= instance.cantidad
        producto.save()


@receiver(pre_delete, sender=Venta)
def restaurar_stock_venta_eliminada(sender, instance, **kwargs):
    """
    Restaura el stock cuando se elimina una venta.
    """
    producto = instance.producto
    producto.stock += instance.cantidad
    producto.save()
