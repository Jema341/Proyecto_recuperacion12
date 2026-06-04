from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Producto, Cliente, Venta, Profile
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from io import BytesIO


# Vista de inicio
@login_required
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


@login_required
def dashboard(request):
    # Parámetros de fecha para filtros
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Convertir strings a datetime
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        except:
            fecha_inicio_dt = None
    else:
        fecha_inicio_dt = None
    
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            fecha_fin_dt = fecha_fin_dt.replace(hour=23, minute=59, second=59)
        except:
            fecha_fin_dt = None
    else:
        fecha_fin_dt = None
    
    # Base de ventas filtrada por rango de fechas
    if fecha_inicio_dt and fecha_fin_dt:
        ventas_filtro = Venta.objects.filter(fecha_venta__gte=fecha_inicio_dt, fecha_venta__lte=fecha_fin_dt, estado='completada')
    else:
        ventas_filtro = Venta.objects.filter(estado='completada')
    
    # Productos con stock bajo (menor a 10 unidades)
    productos_stock_bajo = Producto.objects.filter(stock__lt=10).order_by('stock')
    
    # Clientes nuevos (últimos 5 registrados)
    clientes_nuevos = Cliente.objects.all().order_by('-fecha_registro')[:5]
    
    # Productos más vendidos esta semana
    una_semana_atras = datetime.now() - timedelta(days=7)
    productos_esta_semana = Venta.objects.filter(
        estado='completada',
        fecha_venta__gte=una_semana_atras
    ).values('producto__nombre').annotate(
        cantidad=Sum('cantidad'),
        ingresos=Sum('total')
    ).order_by('-cantidad')[:5]
    
    # Top 5 Productos más vendidos (general)
    top_productos = Venta.objects.filter(estado='completada').values('producto').annotate(
        total_vendidos=Count('id'),
        monto_total=Sum('total')
    ).order_by('-total_vendidos')[:5]
    
    # Obtener detalles de los productos
    top_productos_detalle = []
    for venta in top_productos:
        try:
            producto = Producto.objects.get(id=venta['producto'])
            top_productos_detalle.append({
                'producto': producto,
                'cantidad_ventas': venta['total_vendidos'],
                'monto_total': venta['monto_total']
            })
        except:
            pass
    
    # INDICADORES KPI
    total_ventas = Venta.objects.count()
    ventas_completadas = ventas_filtro.count()
    ventas_pendientes = Venta.objects.filter(estado='pendiente').count()
    
    # Tasa de conversión
    tasa_conversion = (ventas_completadas / total_ventas * 100) if total_ventas > 0 else 0
    
    # Ingresos totales
    ingresos_totales = ventas_filtro.aggregate(total=Sum('total'))['total'] or 0
    
    # Promedio de venta
    promedio_venta = (ingresos_totales / ventas_completadas) if ventas_completadas > 0 else 0
    
    # Ventas este mes
    hoy = datetime.now()
    ventas_este_mes = Venta.objects.filter(
        estado='completada',
        fecha_venta__year=hoy.year,
        fecha_venta__month=hoy.month
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Ventas mes pasado
    mes_pasado = hoy - timedelta(days=30)
    ventas_mes_pasado = Venta.objects.filter(
        estado='completada',
        fecha_venta__year=mes_pasado.year,
        fecha_venta__month=mes_pasado.month
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Crecimiento
    crecimiento = ((ventas_este_mes - ventas_mes_pasado) / ventas_mes_pasado * 100) if ventas_mes_pasado > 0 else 0
    
    # Clientes activos (que han hecho compras)
    clientes_activos = Cliente.objects.filter(venta__estado='completada').distinct().count()
    
    # Datos para gráfico de últimos 6 meses
    meses = []
    ingresos_por_mes = []
    for i in range(6, -1, -1):
        fecha = hoy - timedelta(days=30*i)
        mes_nombre = fecha.strftime('%B')[:3]
        meses.append(mes_nombre)
        
        ingresos = Venta.objects.filter(
            estado='completada',
            fecha_venta__year=fecha.year,
            fecha_venta__month=fecha.month
        ).aggregate(total=Sum('total'))['total'] or 0
        
        ingresos_por_mes.append(float(ingresos))
    
    # Convertir a JSON para el template
    meses_json = json.dumps(meses)
    ingresos_json = json.dumps(ingresos_por_mes)
    
    context = {
        'productos_stock_bajo': productos_stock_bajo,
        'clientes_nuevos': clientes_nuevos,
        'top_productos': top_productos_detalle,
        'productos_esta_semana': productos_esta_semana,
        # KPIs
        'tasa_conversion': round(tasa_conversion, 2),
        'ingresos_totales': round(ingresos_totales, 2),
        'promedio_venta': round(promedio_venta, 2),
        'ventas_este_mes': round(ventas_este_mes, 2),
        'crecimiento': round(crecimiento, 2),
        'clientes_activos': clientes_activos,
        'ventas_pendientes': ventas_pendientes,
        'total_productos': Producto.objects.count(),
        # Gráfico
        'meses': meses_json,
        'ingresos_por_mes': ingresos_json,
        # Filtros
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def ui_icons(request):
    return render(request, 'ui-icons.html')


@login_required
def forms(request):
    return render(request, 'forms.html')


@login_required
def tables(request):
    return render(request, 'tables.html')


@login_required
def calendar(request):
    return render(request, 'calendar.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'login.html')


def guest_login(request):
    guest_username = 'invitado'
    try:
        guest_user = User.objects.get(username=guest_username)
    except User.DoesNotExist:
        try:
            guest_user = User.objects.create_user(
                username=guest_username,
                email='guest-temporal@noreply.local',
                first_name='Invitado',
                last_name='Temporal'
            )
            guest_user.set_unusable_password()
            guest_user.save()
        except Exception as e:
            messages.error(request, 'Error al crear usuario invitado')
            return redirect('login')
    
    auth_login(request, guest_user)
    messages.info(request, 'Has ingresado como invitado')
    return redirect('inicio')


@login_required
def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')


def registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'registration.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe')
            return render(request, 'registration.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado')
            return render(request, 'registration.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        auth_login(request, user)
        messages.success(request, 'Registro completado correctamente')
        return redirect('inicio')
    
    return render(request, 'registration.html')


# Productos
@login_required
def productos(request):
    productos = Producto.objects.all()
    busqueda = request.GET.get('busqueda', '')
    categoria = request.GET.get('categoria', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    
    # Filtro por búsqueda
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda)
        )
    
    # Filtro por categoría
    if categoria:
        productos = productos.filter(categoria=categoria)
    
    # Filtro por rango de precio
    if precio_min:
        try:
            productos = productos.filter(precio__gte=float(precio_min))
        except:
            pass
    
    if precio_max:
        try:
            productos = productos.filter(precio__lte=float(precio_max))
        except:
            pass
    
    # Obtener categorías únicas
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'busqueda': busqueda,
        'categoria': categoria,
        'precio_min': precio_min,
        'precio_max': precio_max,
    }
    
    return render(request, 'productos.html', context)


@login_required
def producto_detalle(request, id):
    producto = Producto.objects.get(id=id)
    
    # Obtener ventas del producto
    ventas_producto = Venta.objects.filter(producto=producto, estado='completada').order_by('-fecha_venta')
    
    # Calcular estadísticas
    total_unidades_vendidas = sum(v.cantidad for v in ventas_producto)
    ingresos_totales = sum(v.total for v in ventas_producto)
    precio_promedio = ingresos_totales / total_unidades_vendidas if total_unidades_vendidas > 0 else 0
    
    # Últimas 10 ventas
    ultimas_ventas = ventas_producto[:10]
    
    context = {
        'producto': producto,
        'total_unidades_vendidas': total_unidades_vendidas,
        'ingresos_totales': ingresos_totales,
        'precio_promedio': precio_promedio,
        'ultimas_ventas': ultimas_ventas,
        'total_ventas': ventas_producto.count()
    }
    
    return render(request, 'producto_detalle.html', context)



@login_required
def editar_producto(request, id):
    producto = Producto.objects.get(id=id)
    
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre', producto.nombre)
        producto.descripcion = request.POST.get('descripcion', producto.descripcion)
        producto.precio = request.POST.get('precio', producto.precio)
        producto.stock = request.POST.get('stock', producto.stock)
        producto.categoria = request.POST.get('categoria', producto.categoria)
        
        # Manejo de imagen
        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']
        
        producto.save()
        messages.success(request, 'Producto actualizado correctamente')
        return redirect('productos')
    
    return render(request, 'editar_producto.html', {'producto': producto})


@login_required
def crear_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        categoria = request.POST.get('categoria')
        
        producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            categoria=categoria
        )
        
        # Manejo de imagen
        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']
        
        producto.save()
        messages.success(request, 'Producto creado correctamente')
        return redirect('productos')
    
    return render(request, 'crear_producto.html')


@login_required
def eliminar_producto(request, id):
    """Elimina un producto con confirmación"""
    producto = Producto.objects.get(id=id)
    
    if request.method == 'POST':
        nombre_producto = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado correctamente')
        return redirect('productos')
    
    # GET - mostrar confirmación
    return render(request, 'confirmar_eliminar.html', {
        'objeto': producto,
        'tipo': 'producto',
        'url_cancelar': 'productos'
    })


@login_required
def eliminar_cliente(request, id):
    """Elimina un cliente con confirmación"""
    cliente = Cliente.objects.get(id=id)
    
    if request.method == 'POST':
        nombre_cliente = cliente.nombre
        # Las ventas se eliminarán en cascada si está configurado
        cliente.delete()
        messages.success(request, f'Cliente "{nombre_cliente}" eliminado correctamente')
        return redirect('clientes')
    
    # GET - mostrar confirmación
    ventas_asociadas = Venta.objects.filter(cliente=cliente).count()
    return render(request, 'confirmar_eliminar.html', {
        'objeto': cliente,
        'tipo': 'cliente',
        'url_cancelar': 'clientes',
        'ventas_asociadas': ventas_asociadas
    })


@login_required
def eliminar_venta(request, id):
    """Elimina una venta con confirmación"""
    venta = Venta.objects.get(id=id)
    
    if request.method == 'POST':
        venta_id = venta.id
        venta.delete()
        messages.success(request, f'Venta #{venta_id} eliminada correctamente')
        return redirect('ventas')
    
    # GET - mostrar confirmación
    return render(request, 'confirmar_eliminar.html', {
        'objeto': venta,
        'tipo': 'venta',
        'url_cancelar': 'ventas'
    })


# Clientes
@login_required
def clientes(request):
    clientes = Cliente.objects.all()
    busqueda = request.GET.get('busqueda', '')
    ciudad = request.GET.get('ciudad', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    
    # Filtro por búsqueda
    if busqueda:
        clientes = clientes.filter(
            Q(nombre__icontains=busqueda) | 
            Q(email__icontains=busqueda) |
            Q(telefono__icontains=busqueda)
        )
    
    # Filtro por ciudad
    if ciudad:
        clientes = clientes.filter(ciudad=ciudad)
    
    # Filtro por fecha de registro
    if fecha_desde:
        try:
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            clientes = clientes.filter(fecha_registro__gte=fecha_desde_dt)
        except:
            pass
    
    # Obtener ciudades únicas
    ciudades = Cliente.objects.values_list('ciudad', flat=True).distinct()
    
    # Agregar estadísticas de cada cliente
    clientes = clientes.annotate(
        total_compras=Count('venta', filter=Q(venta__estado='completada')),
        total_gastado=Sum('venta__total', filter=Q(venta__estado='completada'))
    ).order_by('-fecha_registro')
    
    context = {
        'clientes': clientes,
        'ciudades': ciudades,
        'busqueda': busqueda,
        'ciudad': ciudad,
        'fecha_desde': fecha_desde,
    }
    
    return render(request, 'clientes.html', context)


@login_required
def cliente_detalle(request, id):
    cliente = Cliente.objects.get(id=id)
    
    # Obtener ventas del cliente
    ventas_completadas = Venta.objects.filter(cliente=cliente, estado='completada')
    ventas_pendientes = Venta.objects.filter(cliente=cliente, estado='pendiente')
    ventas_canceladas = Venta.objects.filter(cliente=cliente, estado='cancelada')
    todas_ventas = Venta.objects.filter(cliente=cliente).order_by('-fecha_venta')
    
    # Estadísticas
    total_compras_completadas = ventas_completadas.count()
    total_gastado = ventas_completadas.aggregate(total=Sum('total'))['total'] or 0
    total_compras_pendientes = ventas_pendientes.count()
    total_compras_canceladas = ventas_canceladas.count()
    promedio_compra = (total_gastado / total_compras_completadas) if total_compras_completadas > 0 else 0
    
    # Productos comprados
    productos_comprados = Venta.objects.filter(
        cliente=cliente, 
        estado='completada'
    ).values('producto__nombre').annotate(
        cantidad=Sum('cantidad'),
        veces_comprado=Count('id')
    ).order_by('-cantidad')
    
    context = {
        'cliente': cliente,
        'total_compras_completadas': total_compras_completadas,
        'total_gastado': total_gastado,
        'total_compras_pendientes': total_compras_pendientes,
        'total_compras_canceladas': total_compras_canceladas,
        'promedio_compra': promedio_compra,
        'todas_ventas': todas_ventas,
        'productos_comprados': productos_comprados,
    }
    
    return render(request, 'cliente_detalle.html', context)


@login_required
def editar_cliente(request, id):
    cliente = Cliente.objects.get(id=id)
    
    if request.method == 'POST':
        cliente.nombre = request.POST.get('nombre', cliente.nombre)
        cliente.email = request.POST.get('email', cliente.email)
        cliente.telefono = request.POST.get('telefono', cliente.telefono)
        cliente.direccion = request.POST.get('direccion', cliente.direccion)
        cliente.ciudad = request.POST.get('ciudad', cliente.ciudad)
        cliente.save()
        messages.success(request, 'Cliente actualizado correctamente')
        return redirect('clientes')
    
    return render(request, 'editar_cliente.html', {'cliente': cliente})


# Ventas
@login_required
def ventas(request):
    ventas_list = Venta.objects.all()
    busqueda = request.GET.get('busqueda', '')
    estado = request.GET.get('estado', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    
    # Filtro por búsqueda (cliente o producto)
    if busqueda:
        ventas_list = ventas_list.filter(
            Q(cliente__nombre__icontains=busqueda) | 
            Q(producto__nombre__icontains=busqueda) |
            Q(id__icontains=busqueda)
        )
    
    # Filtro por estado
    if estado:
        ventas_list = ventas_list.filter(estado=estado)
    
    # Filtro por rango de fechas
    if fecha_inicio:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            ventas_list = ventas_list.filter(fecha_venta__gte=fecha_inicio_obj)
        except:
            pass
    
    if fecha_fin:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d')
            fecha_fin_obj = fecha_fin_obj.replace(hour=23, minute=59, second=59)
            ventas_list = ventas_list.filter(fecha_venta__lte=fecha_fin_obj)
        except:
            pass
    
    estados_choices = [('', 'Todos'), ('pendiente', 'Pendiente'), ('completada', 'Completada'), ('cancelada', 'Cancelada')]
    
    context = {
        'ventas': ventas_list,
        'estados_choices': estados_choices,
        'busqueda': busqueda,
        'estado': estado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    
    return render(request, 'ventas.html', context)


@login_required
def editar_venta(request, id):
    venta = Venta.objects.get(id=id)
    
    if request.method == 'POST':
        try:
            venta.cantidad = int(request.POST.get('cantidad', venta.cantidad))
        except (TypeError, ValueError):
            venta.cantidad = venta.cantidad

        try:
            venta.precio_unitario = Decimal(request.POST.get('precio_unitario', venta.precio_unitario))
        except (TypeError, ValueError, InvalidOperation):
            venta.precio_unitario = venta.precio_unitario

        venta.estado = request.POST.get('estado', venta.estado)
        venta.save()
        messages.success(request, 'Venta actualizada correctamente')
        return redirect('ventas')
    
    estados_choices = [('pendiente', 'Pendiente'), ('completada', 'Completada'), ('cancelada', 'Cancelada')]
    
    return render(request, 'editar_venta.html', {'venta': venta, 'estados_choices': estados_choices})


@login_required
def descargar_recibo_venta(request, id):
    """Genera y descarga un recibo PDF de una venta"""
    
    venta = Venta.objects.get(id=id)
    
    # Crear respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recibo_venta_{venta.id}.pdf"'
    
    # Crear documento PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Contenido
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=5,
        alignment=1,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=8,
        spaceBefore=8
    )
    
    # Encabezado
    elements.append(Paragraph("RECIBO DE VENTA", title_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Línea separadora
    from reportlab.platypus import HRFlowable
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3b82f6')))
    elements.append(Spacer(1, 0.2*inch))
    
    # Información del recibo
    info_data = [
        ['Número de Recibo:', f'#VTA-{venta.id}'],
        ['Fecha:', venta.fecha_venta.strftime('%d/%m/%Y %H:%M:%S')],
        ['Estado:', venta.get_estado_display().upper()],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Información del cliente
    elements.append(Paragraph("INFORMACIÓN DEL CLIENTE", heading_style))
    
    cliente_data = [
        ['Nombre:', venta.cliente.nombre],
        ['Email:', venta.cliente.email],
        ['Teléfono:', venta.cliente.telefono or 'N/A'],
        ['Ciudad:', venta.cliente.ciudad or 'N/A'],
    ]
    
    cliente_table = Table(cliente_data, colWidths=[1.5*inch, 3.5*inch])
    cliente_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
    ]))
    elements.append(cliente_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Detalles del producto
    elements.append(Paragraph("DETALLES DE LA COMPRA", heading_style))
    
    detalle_data = [
        ['Producto', 'Cantidad', 'Precio Unitario', 'Total'],
        [
            venta.producto.nombre,
            str(venta.cantidad),
            f'${venta.precio_unitario:.2f}',
            f'${venta.total:.2f}'
        ]
    ]
    
    detalle_table = Table(detalle_data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 1.3*inch])
    detalle_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ]))
    elements.append(detalle_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Resumen financiero
    resumen_data = [
        ['Subtotal:', f'${venta.total:.2f}'],
        ['Impuesto (0%):', '$0.00'],
        ['TOTAL A PAGAR:', f'${venta.total:.2f}'],
    ]
    
    resumen_table = Table(resumen_data, colWidths=[3*inch, 2*inch])
    resumen_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, 1), 'Helvetica'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 1), 10),
        ('FONTSIZE', (0, 2), (-1, 2), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 2), (-1, 2), 12),
        ('TOPPADDING', (0, 2), (-1, 2), 12),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.whitesmoke),
        ('GRID', (0, 2), (-1, 2), 2, colors.HexColor('#3b82f6')),
        ('ALIGN', (0, 2), (-1, 2), 'RIGHT'),
    ]))
    elements.append(resumen_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Notas adicionales (si existen)
    if venta.notas:
        elements.append(Paragraph("NOTAS ADICIONALES", heading_style))
        notes_style = ParagraphStyle(
            'notes',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            alignment=0
        )
        elements.append(Paragraph(venta.notas, notes_style))
        elements.append(Spacer(1, 0.3*inch))
    
    # Pie de página
    from reportlab.platypus import HRFlowable
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#d1d5db')))
    elements.append(Spacer(1, 0.1*inch))
    
    footer_text = "Gracias por su compra. Este recibo es válido como comprobante de transacción."
    elements.append(Paragraph(footer_text, ParagraphStyle(
        'footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        alignment=1
    )))
    
    # Construir PDF
    doc.build(elements)
    
    # Retornar PDF
    buffer.seek(0)
    response.write(buffer.getvalue())
    buffer.close()
    
    return response


@login_required
def cambiar_estado_venta(request, id, estado):
    """Cambia rápidamente el estado de una venta"""
    venta = Venta.objects.get(id=id)
    
    # Validar que el estado sea válido
    estados_validos = ['pendiente', 'completada', 'cancelada']
    if estado in estados_validos:
        venta.estado = estado
        venta.save()
        
        # Mensajes según el estado
        estado_display = dict([('pendiente', 'Pendiente'), ('completada', 'Completada'), ('cancelada', 'Cancelada')])[estado]
        messages.success(request, f'Venta #{venta.id} marcada como {estado_display}')
    else:
        messages.error(request, 'Estado inválido')
    
    return redirect('ventas')


# Reportes
@login_required
def reportes(request):
    # Parámetros de fecha
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Convertir strings a datetime
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        except:
            fecha_inicio_dt = None
    else:
        fecha_inicio_dt = None
    
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            # Agregar un día para incluir todo el día final
            fecha_fin_dt = fecha_fin_dt.replace(hour=23, minute=59, second=59)
        except:
            fecha_fin_dt = None
    else:
        fecha_fin_dt = None
    
    # Filtrar ventas por rango de fechas
    ventas_filtro = Venta.objects.all()
    if fecha_inicio_dt:
        ventas_filtro = ventas_filtro.filter(fecha_venta__gte=fecha_inicio_dt)
    if fecha_fin_dt:
        ventas_filtro = ventas_filtro.filter(fecha_venta__lte=fecha_fin_dt)
    
    # Datos generales (siempre totales)
    total_productos = Producto.objects.count()
    total_clientes = Cliente.objects.count()
    total_ventas = ventas_filtro.count()
    ventas_completadas = ventas_filtro.filter(estado='completada').count()
    
    # Datos para gráfico de ventas por mes (últimos 6 meses o rango seleccionado)
    meses = []
    ventas_por_mes = []
    
    for i in range(5, -1, -1):
        fecha = datetime.now() - timedelta(days=30*i)
        mes = fecha.strftime('%B %Y')
        meses.append(mes)
        
        # Ventas del mes
        ventas_mes = ventas_filtro.filter(
            fecha_venta__year=fecha.year,
            fecha_venta__month=fecha.month,
            estado='completada'
        ).aggregate(total=Sum('total'))['total'] or 0
        ventas_por_mes.append(float(ventas_mes))
    
    # Ventas por categoría
    categorias = []
    ventas_por_categoria = []
    
    categorias_data = Producto.objects.filter(
        venta__in=ventas_filtro.filter(estado='completada')
    ).values('categoria').annotate(
        total=Sum('venta__total')
    ).order_by('-total')
    
    # Colores para las categorías
    colores_categorias = [
        '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
        '#ec4899', '#06b6d4', '#14b8a6', '#f97316', '#6366f1'
    ]
    
    for idx, cat in enumerate(categorias_data):
        categoria_nombre = cat['categoria'] if cat['categoria'] else 'Sin Categoría'
        categorias.append(categoria_nombre)
        ventas_por_categoria.append({
            'valor': float(cat['total'] or 0),
            'color': colores_categorias[idx % len(colores_categorias)]
        })
    
    # Clientes VIP (Top 5 por ingresos)
    clientes_vip = []
    clientes_data = Cliente.objects.annotate(
        total_compras=Count('venta', filter=Q(venta__in=ventas_filtro.filter(estado='completada'))),
        total_gastado=Sum('venta__total', filter=Q(venta__in=ventas_filtro.filter(estado='completada')))
    ).filter(total_compras__gt=0).order_by('-total_gastado')[:5]
    
    for cliente in clientes_data:
        clientes_vip.append({
            'nombre': cliente.nombre,
            'email': cliente.email,
            'total_compras': cliente.total_compras or 0,
            'total_gastado': cliente.total_gastado or 0,
            'promedio_compra': (cliente.total_gastado / cliente.total_compras) if cliente.total_compras > 0 else 0
        })
    
    # Productos Top 5 (más vendidos)
    productos_top = []
    productos_data = Producto.objects.filter(
        venta__in=ventas_filtro.filter(estado='completada')
    ).annotate(
        cantidad_vendida=Sum('venta__cantidad'),
        ingresos_totales=Sum('venta__total'),
        numero_ventas=Count('venta', filter=Q(venta__in=ventas_filtro.filter(estado='completada')))
    ).order_by('-cantidad_vendida')[:5]
    
    nombres_productos_top = []
    cantidades_productos_top = []
    colores_productos_top = [
        '#ff6b6b', '#4ecdc4', '#45b7d1', '#ffa07a', '#98d8c8'
    ]
    
    for producto in productos_data:
        productos_top.append({
            'nombre': producto.nombre,
            'cantidad_vendida': producto.cantidad_vendida or 0,
            'ingresos_totales': producto.ingresos_totales or 0,
            'numero_ventas': producto.numero_ventas or 0,
            'precio_promedio': (producto.ingresos_totales / producto.cantidad_vendida) if producto.cantidad_vendida > 0 else 0
        })
        nombres_productos_top.append(producto.nombre[:20])
        cantidades_productos_top.append(int(producto.cantidad_vendida or 0))
    
    # Preparar datos de categorías para JSON
    categorias_json = json.dumps(categorias)
    valores_categorias_json = json.dumps([cat['valor'] for cat in ventas_por_categoria])
    colores_categorias_json = json.dumps([cat['color'] for cat in ventas_por_categoria])
    
    context = {
        'total_productos': total_productos,
        'total_clientes': total_clientes,
        'total_ventas': total_ventas,
        'ventas_completadas': ventas_completadas,
        'meses': json.dumps(meses),
        'ventas_por_mes': json.dumps(ventas_por_mes),
        'categorias': categorias_json,
        'valores_categorias': valores_categorias_json,
        'colores_categorias': colores_categorias_json,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'clientes_vip': clientes_vip,
        'productos_top': productos_top,
        'nombres_productos_top': json.dumps(nombres_productos_top),
        'cantidades_productos_top': json.dumps(cantidades_productos_top),
        'colores_productos_top': json.dumps(colores_productos_top),
    }

    return render(request, 'reportes.html', context)


@login_required
def exportar_reporte_pdf(request):
    """Genera y descarga un reporte en PDF con filtro de fechas"""
    
    # Parámetros de fecha
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Convertir strings a datetime
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        except:
            fecha_inicio_dt = None
    else:
        fecha_inicio_dt = None
    
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            # Agregar un día para incluir todo el día final
            fecha_fin_dt = fecha_fin_dt.replace(hour=23, minute=59, second=59)
        except:
            fecha_fin_dt = None
    else:
        fecha_fin_dt = None
    
    # Filtrar ventas por rango de fechas
    ventas_filtro = Venta.objects.all()
    if fecha_inicio_dt:
        ventas_filtro = ventas_filtro.filter(fecha_venta__gte=fecha_inicio_dt)
    if fecha_fin_dt:
        ventas_filtro = ventas_filtro.filter(fecha_venta__lte=fecha_fin_dt)
    
    # Recopilar datos
    total_productos = Producto.objects.count()
    total_clientes = Cliente.objects.count()
    total_ventas = ventas_filtro.count()
    ventas_completadas = ventas_filtro.filter(estado='completada').count()
    ingresos_totales = sum(v.total for v in ventas_filtro.filter(estado='completada'))
    
    # Crear respuesta PDF
    nombre_archivo = "reporte_ventas.pdf"
    if fecha_inicio and fecha_fin:
        nombre_archivo = f"reporte_ventas_{fecha_inicio}_a_{fecha_fin}.pdf"
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    
    # Crear documento PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Contenido
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=30,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#374151'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Título
    elements.append(Paragraph("REPORTE DE VENTAS", title_style))
    
    # Información del período
    periodo_text = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    if fecha_inicio or fecha_fin:
        periodo_text += " | Período: "
        if fecha_inicio and fecha_fin:
            periodo_text += f"{fecha_inicio} a {fecha_fin}"
        elif fecha_inicio:
            periodo_text += f"desde {fecha_inicio}"
        else:
            periodo_text += f"hasta {fecha_fin}"
    
    elements.append(Paragraph(periodo_text, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Resumen General
    elements.append(Paragraph("RESUMEN GENERAL", heading_style))
    
    resumen_data = [
        ['Métrica', 'Valor'],
        ['Total Productos', str(total_productos)],
        ['Total Clientes', str(total_clientes)],
        ['Total Ventas', str(total_ventas)],
        ['Ventas Completadas', str(ventas_completadas)],
        ['Ingresos Totales', f'${ingresos_totales:.2f}'],
    ]
    
    resumen_table = Table(resumen_data, colWidths=[3*inch, 2*inch])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(resumen_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Últimas Ventas
    elements.append(Paragraph("ÚLTIMAS 10 VENTAS COMPLETADAS", heading_style))
    
    ultimas_ventas = ventas_filtro.filter(estado='completada').order_by('-fecha_venta')[:10]
    
    if ultimas_ventas:
        ventas_data = [['ID', 'Cliente', 'Producto', 'Cantidad', 'Total', 'Fecha']]
        for venta in ultimas_ventas:
            ventas_data.append([
                str(venta.id),
                venta.cliente.nombre[:15],
                venta.producto.nombre[:15],
                str(venta.cantidad),
                f"${venta.total:.2f}",
                venta.fecha_venta.strftime('%d/%m/%Y')
            ])
        
        ventas_table = Table(ventas_data, colWidths=[0.6*inch, 1.2*inch, 1.2*inch, 0.8*inch, 0.8*inch, 1*inch])
        ventas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')])
        ]))
        elements.append(ventas_table)
    
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Top 5 Productos Más Vendidos
    elements.append(Paragraph("TOP 5 PRODUCTOS MÁS VENDIDOS", heading_style))
    
    productos_top_pdf = Producto.objects.filter(
        venta__in=ventas_filtro.filter(estado='completada')
    ).annotate(
        cantidad_vendida=Sum('venta__cantidad'),
        ingresos_totales=Sum('venta__total'),
        numero_ventas=Count('venta', filter=Q(venta__in=ventas_filtro.filter(estado='completada')))
    ).order_by('-cantidad_vendida')[:5]
    
    if productos_top_pdf:
        productos_data = [['Producto', 'Cantidad', 'Ingresos', 'Precio Promedio']]
        for producto in productos_top_pdf:
            precio_promedio = (producto.ingresos_totales / producto.cantidad_vendida) if producto.cantidad_vendida > 0 else 0
            productos_data.append([
                producto.nombre[:20],
                str(int(producto.cantidad_vendida or 0)),
                f"${producto.ingresos_totales:.2f}",
                f"${precio_promedio:.2f}"
            ])
        
        productos_table = Table(productos_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1.3*inch])
        productos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff6b6b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ffe4e4')])
        ]))
        elements.append(productos_table)
    else:
        elements.append(Paragraph("No hay productos vendidos en este período", styles['Normal']))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Clientes VIP
    elements.append(Paragraph("TOP 5 CLIENTES VIP (POR INGRESOS)", heading_style))
    
    # Calcular clientes VIP
    clientes_vip_pdf = Cliente.objects.annotate(
        total_compras=Count('venta', filter=Q(venta__in=ventas_filtro.filter(estado='completada'))),
        total_gastado=Sum('venta__total', filter=Q(venta__in=ventas_filtro.filter(estado='completada')))
    ).filter(total_compras__gt=0).order_by('-total_gastado')[:5]
    
    if clientes_vip_pdf:
        vip_data = [['Cliente', 'Email', 'Compras', 'Total Gastado', 'Promedio']]
        for cliente in clientes_vip_pdf:
            promedio = (cliente.total_gastado / cliente.total_compras) if cliente.total_compras > 0 else 0
            vip_data.append([
                cliente.nombre[:20],
                cliente.email[:20],
                str(cliente.total_compras),
                f"${cliente.total_gastado:.2f}",
                f"${promedio:.2f}"
            ])
        
        vip_table = Table(vip_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1.2*inch, 1*inch])
        vip_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#faf5ff')])
        ]))
        elements.append(vip_table)
    else:
        elements.append(Paragraph("No hay clientes VIP en este período", styles['Normal']))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Productos con Bajo Stock
    elements.append(Paragraph("PRODUCTOS CON BAJO STOCK (< 10 unidades)", heading_style))
    
    bajo_stock = Producto.objects.filter(stock__lt=10).order_by('stock')[:10]
    
    if bajo_stock:
        stock_data = [['Producto', 'Categoría', 'Stock', 'Precio']]
        for producto in bajo_stock:
            stock_data.append([
                producto.nombre[:20],
                producto.categoria[:15],
                str(producto.stock),
                f"${producto.precio:.2f}"
            ])
        
        stock_table = Table(stock_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch])
        stock_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef2f2')])
        ]))
        elements.append(stock_table)
    else:
        elements.append(Paragraph("Todos los productos tienen stock suficiente", styles['Normal']))
    
    # Construir PDF
    doc.build(elements)
    
    # Retornar PDF
    buffer.seek(0)
    response.write(buffer.getvalue())
    buffer.close()
    
    return response


def get_user_profile(user):
    profile, created = Profile.objects.get_or_create(user=user)
    return profile


# Perfil de Usuario
@login_required(login_url='login')
def profile(request):
    user_profile = get_user_profile(request.user)
    return render(request, 'profile.html', {'user_profile': user_profile})


@login_required(login_url='login')
def edit_profile(request):
    user_profile = get_user_profile(request.user)

    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()

        avatar = request.FILES.get('avatar')
        if avatar:
            user_profile.avatar = avatar

        user_profile.phone = request.POST.get('phone', user_profile.phone)
        user_profile.company = request.POST.get('company', user_profile.company)
        user_profile.location = request.POST.get('location', user_profile.location)
        user_profile.bio = request.POST.get('bio', user_profile.bio)
        user_profile.save()

        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('profile')

    return render(request, 'edit-profile.html', {'user_profile': user_profile})


@login_required(login_url='login')
def user_panel(request):
    user_profile = get_user_profile(request.user)
    return render(request, 'user-panel.html', {'user_profile': user_profile})