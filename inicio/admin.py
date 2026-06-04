from django.contrib import admin
from .models import Producto, Cliente, Venta, Profile


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'fecha_creacion')
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria', 'fecha_creacion')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'ciudad', 'fecha_registro')
    search_fields = ('nombre', 'email')
    list_filter = ('ciudad', 'fecha_registro')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'company', 'location')
    search_fields = ('user__username', 'phone', 'company')
    readonly_fields = ('user',)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cliente',
        'producto',
        'cantidad',
        'total',
        'estado',
        'fecha_venta'
    )
    search_fields = ('cliente__nombre', 'producto__nombre')
    list_filter = ('estado', 'fecha_venta')
    readonly_fields = ('fecha_venta', 'total')