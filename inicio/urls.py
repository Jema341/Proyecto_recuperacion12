from django.urls import path
from . import views

urlpatterns = [
    # Dashboard e Inicio
    path('', views.inicio, name='inicio'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # UI y vistas adicionales
    path('ui-icons/', views.ui_icons, name='ui_icons'),
    path('forms/', views.forms, name='forms'),
    path('tables/', views.tables, name='tables'),
    path('calendar/', views.calendar, name='calendar'),

    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registration/', views.registration, name='registration'),

    # Perfil de usuario
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('user-panel/', views.user_panel, name='user_panel'),

    # Productos
    path('productos/', views.productos, name='productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:id>/', views.producto_detalle, name='producto_detalle'),
    path('productos/<int:id>/editar/', views.editar_producto, name='editar_producto'),

    # Clientes
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/<int:id>/', views.cliente_detalle, name='cliente_detalle'),
    path('clientes/<int:id>/editar/', views.editar_cliente, name='editar_cliente'),

    # Ventas
    path('ventas/', views.ventas, name='ventas'),
    path('ventas/<int:id>/editar/', views.editar_venta, name='editar_venta'),

    # Reportes
    path('reportes/', views.reportes, name='reportes'),
]