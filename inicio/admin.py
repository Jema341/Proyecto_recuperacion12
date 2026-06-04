from django.contrib import admin
from .models import UserProfile, Product

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'company', 'location', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'company', 'phone')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('name', 'description', 'category')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'category')
        }),
        ('Precios y Stock', {
            'fields': ('price', 'stock')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )


