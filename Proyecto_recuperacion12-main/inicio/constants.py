"""
Constantes de la aplicación Inicio
"""

# Estados de venta
ESTADO_VENTA_PENDIENTE = 'pendiente'
ESTADO_VENTA_COMPLETADA = 'completada'
ESTADO_VENTA_CANCELADA = 'cancelada'

ESTADOS_VENTA = [
    (ESTADO_VENTA_PENDIENTE, 'Pendiente'),
    (ESTADO_VENTA_COMPLETADA, 'Completada'),
    (ESTADO_VENTA_CANCELADA, 'Cancelada'),
]

# Categorías de productos (Ejemplos)
CATEGORIA_ELECTRÓNICA = 'Electrónica'
CATEGORIA_ROPA = 'Ropa'
CATEGORIA_ALIMENTOS = 'Alimentos'
CATEGORIA_OTROS = 'Otros'

CATEGORIAS_PRODUCTO = [
    CATEGORIA_ELECTRÓNICA,
    CATEGORIA_ROPA,
    CATEGORIA_ALIMENTOS,
    CATEGORIA_OTROS,
]

# Pagos
METODO_PAGO_EFECTIVO = 'efectivo'
METODO_PAGO_TARJETA = 'tarjeta'
METODO_PAGO_TRANSFERENCIA = 'transferencia'

METODOS_PAGO = [
    (METODO_PAGO_EFECTIVO, 'Efectivo'),
    (METODO_PAGO_TARJETA, 'Tarjeta'),
    (METODO_PAGO_TRANSFERENCIA, 'Transferencia Bancaria'),
]
