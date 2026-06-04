from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Producto, Cliente, Venta
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from io import BytesIO


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
    # Productos con stock bajo (menor a 10 unidades)
    productos_stock_bajo = Producto.objects.filter(stock__lt=10).order_by('stock')
    
    # Clientes nuevos (últimos 5 registrados)
    clientes_nuevos = Cliente.objects.all().order_by('-fecha_registro')[:5]
    
    # Top 5 Productos más vendidos
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
    ventas_completadas = Venta.objects.filter(estado='completada').count()
    ventas_pendientes = Venta.objects.filter(estado='pendiente').count()
    
    # Tasa de conversión
    tasa_conversion = (ventas_completadas / total_ventas * 100) if total_ventas > 0 else 0
    
    # Ingresos totales
    ingresos_totales = Venta.objects.filter(estado='completada').aggregate(total=Sum('total'))['total'] or 0
    
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
    
    context = {
        'productos_stock_bajo': productos_stock_bajo,
        'clientes_nuevos': clientes_nuevos,
        'top_productos': top_productos_detalle,
        # KPIs
        'tasa_conversion': round(tasa_conversion, 2),
        'ingresos_totales': round(ingresos_totales, 2),
        'promedio_venta': round(promedio_venta, 2),
        'ventas_este_mes': round(ventas_este_mes, 2),
        'crecimiento': round(crecimiento, 2),
        'clientes_activos': clientes_activos,
        'ventas_pendientes': ventas_pendientes,
        'total_productos': Producto.objects.count(),
    }
    
    return render(request, 'dashboard.html', context)


def ui_icons(request):
    return render(request, 'ui-icons.html')


def forms(request):
    return render(request, 'forms.html')


def tables(request):
    return render(request, 'tables.html')


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
        return redirect('inicio')
    
    return render(request, 'registration.html')


# Productos
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


# Clientes
def clientes(request):
    clientes = Cliente.objects.all()
    busqueda = request.GET.get('busqueda', '')
    ciudad = request.GET.get('ciudad', '')
    
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
    
    # Obtener ciudades únicas
    ciudades = Cliente.objects.values_list('ciudad', flat=True).distinct()
    
    context = {
        'clientes': clientes,
        'ciudades': ciudades,
        'busqueda': busqueda,
        'ciudad': ciudad,
    }
    
    return render(request, 'clientes.html', context)


def cliente_detalle(request, id):
    cliente = Cliente.objects.get(id=id)
    return render(request, 'cliente_detalle.html', {'cliente': cliente})


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


def editar_venta(request, id):
    venta = Venta.objects.get(id=id)
    
    if request.method == 'POST':
        venta.cantidad = request.POST.get('cantidad', venta.cantidad)
        venta.precio_unitario = request.POST.get('precio_unitario', venta.precio_unitario)
        venta.total = float(venta.cantidad) * float(venta.precio_unitario)
        venta.estado = request.POST.get('estado', venta.estado)
        venta.save()
        messages.success(request, 'Venta actualizada correctamente')
        return redirect('ventas')
    
    estados_choices = [('pendiente', 'Pendiente'), ('completada', 'Completada'), ('cancelada', 'Cancelada')]
    
    return render(request, 'editar_venta.html', {'venta': venta, 'estados_choices': estados_choices})


# Reportes
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
    
    context = {
        'total_productos': total_productos,
        'total_clientes': total_clientes,
        'total_ventas': total_ventas,
        'ventas_completadas': ventas_completadas,
        'meses': json.dumps(meses),
        'ventas_por_mes': json.dumps(ventas_por_mes),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'clientes_vip': clientes_vip,
    }

    return render(request, 'reportes.html', context)


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