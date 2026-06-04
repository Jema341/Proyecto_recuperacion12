"""
Utilidades para la aplicación Inicio

Funciones auxiliares para procesamiento de datos.
"""

def calcular_total_venta(cantidad, precio):
    """
    Calcula el total de una venta.
    
    Args:
        cantidad (int): Cantidad de productos
        precio (float): Precio unitario
    
    Returns:
        float: Total de la venta
    """
    return cantidad * precio


def aplicar_descuento(monto, porcentaje):
    """
    Aplica un descuento a un monto.
    
    Args:
        monto (float): Monto original
        porcentaje (float): Porcentaje de descuento
    
    Returns:
        float: Monto después del descuento
    """
    descuento = monto * (porcentaje / 100)
    return monto - descuento


def formatear_moneda(cantidad):
    """
    Formatea una cantidad como moneda.
    
    Args:
        cantidad (float): Cantidad a formatear
    
    Returns:
        str: Cantidad formateada como moneda
    """
    return f"${cantidad:,.2f}"


def formatear_porcentaje(valor):
    """
    Formatea un valor como porcentaje.
    
    Args:
        valor (float): Valor decimal para formatear
    
    Returns:
        str: Valor formateado en porcentaje
    """
    return f"{valor:.2f}%"
