from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import UserProfile, Product

# Create your views here.
def inicio(request):
  return render(request, 'dashboard.html')

def dashboard(request):
  return render(request, 'dashboard.html')

def ui_icons(request):
  return render(request, 'ui-icons.html')

def forms(request):
  return render(request, 'forms.html')

def tables(request):
  # Obtener parámetro de búsqueda
  search_query = request.GET.get('search', '')
  
  # Obtener todos los productos
  products = Product.objects.all()
  
  # Si hay búsqueda, filtrar
  if search_query:
    products = products.filter(
      Q(name__icontains=search_query) |
      Q(description__icontains=search_query) |
      Q(category__icontains=search_query)
    )
  
  context = {
    'products': products,
    'search_query': search_query,
  }
  return render(request, 'tables.html', context)

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
    # Actualizar datos del usuario
    request.user.first_name = request.POST.get('first_name', request.user.first_name)
    request.user.last_name = request.POST.get('last_name', request.user.last_name)
    request.user.email = request.POST.get('email', request.user.email)
    request.user.save()
    
    # Actualizar perfil
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