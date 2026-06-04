from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login

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
  return render(request, 'tables.html')

def calendar(request):
  return render(request, 'calendar.html')

def profile(request):
  return render(request, 'profile.html')

def login_view(request):
  return render(request, 'login.html')

def registration(request):
  return render(request, 'registration.html')