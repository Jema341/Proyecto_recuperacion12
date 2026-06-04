from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login

# Create your views here.
def inicio(request):
  return render(request, 'index.html')