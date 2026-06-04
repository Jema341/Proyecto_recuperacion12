"""
Formularios para la aplicación Inicio

Formularios para crear y actualizar datos.
"""

from django import forms
from .models import Producto, Cliente, Venta


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria']
        labels = {
            'nombre': 'Nombre del producto',
            'descripcion': 'Descripción',
            'precio': 'Precio unitario',
            'stock': 'Stock disponible',
            'categoria': 'Categoría',
        }
        help_texts = {
            'precio': 'Ingrese el precio unitario del producto.',
            'stock': 'Ingrese la cantidad disponible en inventario.',
            'categoria': 'Categoría de producto, por ejemplo Electrónica o Hogar.',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Categoría'}),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'email', 'telefono', 'direccion', 'ciudad']
        labels = {
            'nombre': 'Nombre completo',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
        }
        help_texts = {
            'email': 'Usa una dirección de correo válida para identificar al cliente.',
            'telefono': 'Número de teléfono de contacto.',
            'direccion': 'Dirección postal o ubicación del cliente.',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
        }


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente', 'producto', 'cantidad', 'precio_unitario', 'estado', 'notas']
        labels = {
            'cliente': 'Cliente',
            'producto': 'Producto',
            'cantidad': 'Cantidad',
            'precio_unitario': 'Precio unitario',
            'estado': 'Estado de la venta',
            'notas': 'Notas',
        }
        help_texts = {
            'cantidad': 'Cantidad de unidades vendidas. Debe ser mayor que cero.',
            'precio_unitario': 'Precio por unidad del producto.',
            'estado': 'Selecciona el estado actual de la venta.',
            'notas': 'Puedes registrar comentarios o indicaciones adicionales.',
        }
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio unitario'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales sobre esta venta'}),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is not None and cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor que cero.')
        return cantidad

    def clean_precio_unitario(self):
        precio_unitario = self.cleaned_data.get('precio_unitario')
        if precio_unitario is not None and precio_unitario <= 0:
            raise forms.ValidationError('El precio unitario debe ser mayor que cero.')
        return precio_unitario
