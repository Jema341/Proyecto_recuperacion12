from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile

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


def profile(request):
    return render(request, 'profile.html')


@login_required(login_url='login')
def user_panel(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    context = {
        'user_profile': user_profile,
        'user': request.user
    }

    return render(request, 'user-panel.html', context)


@login_required(login_url='login')
def edit_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()

        user_profile.bio = request.POST.get('bio', user_profile.bio)
        user_profile.phone = request.POST.get('phone', user_profile.phone)
        user_profile.company = request.POST.get('company', user_profile.company)
        user_profile.location = request.POST.get('location', user_profile.location)

        if 'avatar' in request.FILES:
            user_profile.avatar = request.FILES['avatar']

        user_profile.save()

        return redirect('user_panel')

    context = {
        'user_profile': user_profile,
        'user': request.user
    }

    return render(request, 'edit-profile.html', context)


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
    context = {
        'total_productos': Producto.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'total_ventas': Venta.objects.count(),
        'ventas_completadas': Venta.objects.filter(estado='completada').count(),
    }

    return render(request, 'reportes.html', context)