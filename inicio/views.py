from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Producto, Cliente, Venta
from django.db.models import Sum
from datetime import datetime, timedelta
import json


# Vista de inicio
def inicio(request):
    total_productos = Producto.objects.count()
    total_clientes = Cliente.objects.count()
    total_ventas = Venta.objects.filter(estado='completada').count()
    ventas_monto = sum(v.total for v in Venta.objects.filter(estado='completada'))

    ultimas_ventas = Venta.objects.all()[:5]

    context = {
        'total_productos': total_productos,
        'total_clientes': total_clientes,
        'total_ventas': total_ventas,
        'ventas_monto': ventas_monto,
        'ultimas_ventas': ultimas_ventas,
    }

    return render(request, 'index.html', context)


def dashboard(request):
    return render(request, 'dashboard.html')


def ui_icons(request):
    return render(request, 'ui-icons.html')


def forms(request):
    return render(request, 'forms.html')


def tables(request):
    return render(request, 'tables.html')


def calendar(request):
    return render(request, 'calendar.html')


def login_view(request):
    return render(request, 'login.html')


def registration(request):
    return render(request, 'registration.html')


# Productos
def productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos.html', {'productos': productos})


def producto_detalle(request, id):
    producto = Producto.objects.get(id=id)
    return render(request, 'producto_detalle.html', {'producto': producto})


# Clientes
def clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes.html', {'clientes': clientes})


def cliente_detalle(request, id):
    cliente = Cliente.objects.get(id=id)
    return render(request, 'cliente_detalle.html', {'cliente': cliente})


# Ventas
def ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'ventas.html', {'ventas': ventas})


# Reportes
def reportes(request):
    # Datos generales
    total_productos = Producto.objects.count()
    total_clientes = Cliente.objects.count()
    total_ventas = Venta.objects.count()
    ventas_completadas = Venta.objects.filter(estado='completada').count()
    
    # Datos para gráfico de ventas por mes (últimos 6 meses)
    meses = []
    ventas_por_mes = []
    
    for i in range(5, -1, -1):
        fecha = datetime.now() - timedelta(days=30*i)
        mes = fecha.strftime('%B %Y')
        meses.append(mes)
        
        # Ventas del mes
        ventas_mes = Venta.objects.filter(
            fecha_venta__year=fecha.year,
            fecha_venta__month=fecha.month,
            estado='completada'
        ).aggregate(total=Sum('total'))['total'] or 0
        ventas_por_mes.append(float(ventas_mes))
    
    context = {
        'total_productos': total_productos,
        'total_clientes': total_clientes,
        'total_ventas': total_ventas,
        'ventas_completadas': ventas_completadas,
        'meses': json.dumps(meses),
        'ventas_por_mes': json.dumps(ventas_por_mes),
    }

    return render(request, 'reportes.html', context)


# Perfil de Usuario
@login_required(login_url='login')
def profile(request):
    return render(request, 'profile.html')


@login_required(login_url='login')
def edit_profile(request):
    return render(request, 'edit-profile.html')


@login_required(login_url='login')
def user_panel(request):
    return render(request, 'user-panel.html')