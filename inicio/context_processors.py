from .models import Profile, Mensaje


def user_profile(request):
    """
    Context processor que añade el perfil del usuario autenticado y sus mensajes a todos los templates.
    """
    context = {
        'user_profile': None,
        'mensajes': [],
        'notificaciones': [],
        'total_mensajes': 0,
        'total_notificaciones': 0,
    }
    
    if request.user.is_authenticated:
        try:
            profile, created = Profile.objects.get_or_create(user=request.user)
            context['user_profile'] = profile
            
            # Obtener mensajes del usuario
            mensajes = Mensaje.objects.filter(usuario=request.user).order_by('-fecha_envio')[:10]
            context['mensajes'] = mensajes
            context['total_mensajes'] = mensajes.count()
            
            # Obtener notificaciones no leídas
            notificaciones_no_leidas = Mensaje.objects.filter(usuario=request.user, leido=False)
            context['notificaciones'] = notificaciones_no_leidas.order_by('-fecha_envio')[:5]
            context['total_notificaciones'] = notificaciones_no_leidas.count()
        except:
            pass
    
    return context
