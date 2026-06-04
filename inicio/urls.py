from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('ui-icons/', views.ui_icons, name='ui_icons'),
    path('forms/', views.forms, name='forms'),
    path('tables/', views.tables, name='tables'),
    path('calendar/', views.calendar, name='calendar'),

    path('login/', views.login_view, name='login'),
    path('registration/', views.registration, name='registration'),

    # Productos
    path('productos/', views.productos, name='productos'),
    path('productos/<int:id>/', views.producto_detalle, name='producto_detalle'),

    # Clientes
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/<int:id>/', views.cliente_detalle, name='cliente_detalle'),

    # Ventas
    path('ventas/', views.ventas, name='ventas'),

    # Reportes
    path('reportes/', views.reportes, name='reportes'),
]