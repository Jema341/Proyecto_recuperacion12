from .models import Profile


def user_profile(request):
    """
    Context processor que añade el perfil del usuario autenticado a todos los templates.
    """
    context = {
        'user_profile': None,
    }
    
    if request.user.is_authenticated:
        try:
            profile, created = Profile.objects.get_or_create(user=request.user)
            context['user_profile'] = profile
        except:
            pass
    
    return context
