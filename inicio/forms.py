"""
Formularios para la aplicación Inicio

Formularios para crear y actualizar datos.
"""

from django import forms
from .models import Producto, Cliente, Venta


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Categoría'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'email', 'telefono', 'direccion', 'ciudad']
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
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad', 'min': 1}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio unitario', 'min': 0.01, 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales sobre esta venta'}),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None or cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor que cero.')
        return cantidad

    def clean_precio_unitario(self):
        precio_unitario = self.cleaned_data.get('precio_unitario')
        if precio_unitario is None or precio_unitario <= 0:
            raise forms.ValidationError('El precio unitario debe ser mayor que cero.')
        return precio_unitario
